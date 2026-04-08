# shared/base_models.py
from pydantic import BaseModel
from typing import Any, Optional

class BaseObservation(BaseModel):
    task_id: str
    step: int
    task_instruction: str
    done: bool = False

class BaseAction(BaseModel):
    pass

class BaseReward(BaseModel):
    score: float
    breakdown: dict[str, float]
    feedback: str

class StepResult(BaseModel):
    observation: dict[str, Any]
    reward: float
    done: bool
    info: dict[str, Any]