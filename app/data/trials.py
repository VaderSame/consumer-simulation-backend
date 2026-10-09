import json
from pathlib import Path
from typing import Dict, List, Optional
from app.models.schemas import Trial

TRIALS_DIR = Path(__file__).parent / "trials"

_TRIALS_CACHE: Dict[str, Trial] = {}

FILE_MAPPING: Dict[str, str] = {
    "trial_set_a_sleep": "set_a_sleep.json",
    "trial_sleep_set_a": "set_a_sleep.json",
    "trial_set_b_joint": "set_b_joint.json",
    "trial_set_c_energy": "set_c_energy.json",
    "trial_set_d_stress": "set_d_stress.json",
}


def load_trial_by_id(trial_id: str) -> Optional[Trial]:
    """
    Loads trial data dynamically from JSON file.
    Decouples stimulus content from Python backend logic.
    """
    if trial_id in _TRIALS_CACHE:
        return _TRIALS_CACHE[trial_id]

    filename = FILE_MAPPING.get(trial_id)
    if not filename:
        return None

    filepath = TRIALS_DIR / filename
    if not filepath.exists():
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        trial = Trial(**data)
        _TRIALS_CACHE[trial_id] = trial
        return trial


def get_trial_set_a() -> Trial:
    """Returns the default Set A trial for initial session handshake."""
    trial = load_trial_by_id("trial_set_a_sleep")
    if not trial:
        raise FileNotFoundError("Could not find set_a_sleep.json in trials directory")
    return trial


def get_all_trials() -> List[Trial]:
    """Returns all 4 experimental trials in sequence."""
    order = ["trial_set_a_sleep", "trial_set_b_joint", "trial_set_c_energy", "trial_set_d_stress"]
    return [t for tid in order if (t := load_trial_by_id(tid))]
