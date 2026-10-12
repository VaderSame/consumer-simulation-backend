from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import uuid
import random

from app.models.schemas import (
    AdvisorMessageRequest,
    AdvisorMessageResponse,
    Condition,
    Trial,
    DecisionSubmission,
    DecisionResult,
    SessionInitResponse,
)
from app.data.trials import get_trial_set_a, load_trial_by_id, get_all_trials
from app.llm.provider import get_model_name
from app.services.advisor_service import generate_advisor_response

router = APIRouter()


TRIAL_ORDER = [
    "trial_set_a_sleep",
    "trial_set_b_joint",
    "trial_set_c_energy",
    "trial_set_d_stress",
]


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "consumer-ai-simulation-api"}


@router.get("/session/init", response_model=SessionInitResponse)
async def init_session(
    prolific_pid: Optional[str] = Query(None),
    study_id: Optional[str] = Query(None),
    force_condition: Optional[Condition] = Query(None)
):
    """
    Initializes a new participant session.
    Randomly assigns to 1 of 4 conditions (or honors researcher force_condition),
    and generates a counterbalanced steer schedule (2 steer trials out of 4).
    """
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    
    if force_condition:
        assigned_condition = force_condition
    else:
        assigned_condition = random.choice([
            Condition.CONTROL,
            Condition.HUMAN_FREE,
            Condition.AI_FREE,
            Condition.AI_STRUCTURED
        ])

    steer_schedule = [True, False, True, False]
    random.shuffle(steer_schedule)

    trial_data = get_trial_set_a()

    return SessionInitResponse(
        session_id=session_id,
        condition=assigned_condition,
        steer_schedule=steer_schedule,
        current_trial=trial_data,
        trial_sequence=TRIAL_ORDER
    )


@router.get("/trials", response_model=List[Trial])
async def list_trials():
    """Returns all 4 configured experimental trials."""
    return get_all_trials()


@router.get("/trial/{trial_id}", response_model=Trial)
async def get_trial(trial_id: str):
    """Returns trial stimuli and configuration for a given trial ID."""
    trial = load_trial_by_id(trial_id)
    if not trial:
        raise HTTPException(status_code=404, detail=f"Trial '{trial_id}' not found")
    return trial



@router.post("/decision", response_model=DecisionResult)
async def submit_decision(submission: DecisionSubmission):
    """
    Submits participant decision and metacognitive ratings (confidence & justification).
    Calculates outcome metrics (ground truth match, steer adherence, calibration)
    and indicates the next trial in sequence for automated progression.
    """
    trial_data = load_trial_by_id(submission.trial_id) or get_trial_set_a()
    is_ground_truth_best = (submission.selected_product_id == trial_data.ground_truth_best_id)
    is_over_reliance = (trial_data.is_steer_trial and submission.selected_product_id == trial_data.steer_target_id)

    # Calculate progression state
    try:
        current_idx = TRIAL_ORDER.index(submission.trial_id)
        if current_idx < len(TRIAL_ORDER) - 1:
            next_trial_id = TRIAL_ORDER[current_idx + 1]
            is_last_trial = False
        else:
            next_trial_id = None
            is_last_trial = True
    except ValueError:
        next_trial_id = None
        is_last_trial = False

    return DecisionResult(
        status="recorded",
        session_id=submission.session_id,
        trial_id=submission.trial_id,
        selected_product_id=submission.selected_product_id,
        is_ground_truth_best=is_ground_truth_best,
        is_over_reliance=is_over_reliance,
        signed_calibration=submission.confidence_score - (100 if is_ground_truth_best else 0),
        next_trial_id=next_trial_id,
        is_last_trial=is_last_trial,
        message="Decision recorded successfully."
    )


@router.post("/advisor/message", response_model=AdvisorMessageResponse)
async def advisor_message(body: AdvisorMessageRequest):
    """
    Live follow-up for the shopping advisor.

    The scripted opening is not generated here. The model answers only
    the participant's question, using that trial's label data.
    """
    if body.condition == Condition.CONTROL:
        raise HTTPException(
            status_code=400,
            detail="The control condition has no advisor.",
        )

    trial = load_trial_by_id(body.trial_id)
    if not trial:
        raise HTTPException(status_code=404, detail=f"Trial '{body.trial_id}' not found")

    question = body.message.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Message is empty.")

    reply = await generate_advisor_response(
        trial=trial,
        condition=body.condition,
        user_message=question,
        history=[turn.model_dump() for turn in body.history],
        active_stage=body.active_stage,
    )

    return AdvisorMessageResponse(
        session_id=body.session_id,
        trial_id=body.trial_id,
        condition=body.condition,
        reply=reply,
        model=get_model_name(),
    )
