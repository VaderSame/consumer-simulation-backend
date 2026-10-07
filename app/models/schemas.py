from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class Condition(str, Enum):
    CONTROL = "control"
    HUMAN_FREE = "human_free"
    AI_FREE = "ai_free"
    AI_STRUCTURED = "ai_structured"


class ProductForm(str, Enum):
    CAPSULE = "CAPSULE"
    GUMMY = "GUMMY"
    TABLET = "TABLET"


class IngredientItem(BaseModel):
    name: str
    amount: str
    daily_value: Optional[str] = None


class SupplementFacts(BaseModel):
    serving_size: str
    servings_per_container: int
    ingredients: List[IngredientItem]
    other_ingredients: Optional[str] = None
    directions: Optional[str] = None
    warnings: Optional[str] = None


class Product(BaseModel):
    id: str
    name: str
    form: ProductForm
    price: float
    highlight_text: str
    is_ground_truth_best: bool = False
    is_steer_target: bool = False
    steer_false_claim: Optional[str] = None
    ground_truth_notes: Optional[str] = None
    supplement_facts: SupplementFacts


class PromptChip(BaseModel):
    id: str
    label: str
    stage: str  # clarify, evaluate, verify, decide


class Trial(BaseModel):
    trial_id: str
    trial_number: int
    total_trials: int
    category: str
    scenario_title: str
    scenario_description: str
    is_steer_trial: bool
    scripted_opening: str
    steer_target_id: Optional[str] = None
    ground_truth_best_id: str
    products: List[Product]
    scaffold_chips: Dict[str, List[PromptChip]] = Field(default_factory=dict)


class DecisionSubmission(BaseModel):
    session_id: str
    prolific_id: Optional[str] = None
    trial_id: str
    condition: Condition
    selected_product_id: str
    justification: str
    confidence_score: int  # 0 to 100


class SessionInitResponse(BaseModel):
    session_id: str
    condition: Condition
    steer_schedule: List[bool]
    current_trial: Trial
