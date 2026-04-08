# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_a_data_cleaning\server.py
import sys
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from env_a_data_cleaning.environment import DataCleaningEnv, DataCleaningAction
from shared.base_models import StepResult

app = FastAPI()
env = DataCleaningEnv()

class ResetRequest(BaseModel):
    task_name: Optional[str] = None

@app.post("/reset", response_model=StepResult)
def reset(request: Optional[ResetRequest] = None, task_name: Optional[str] = Query(None)):
    """Reset environment. Accepts task_name via query parameter or request body."""
    # Get task_name from query parameter, request body, or default
    actual_task_name = task_name or (request.task_name if request else None)
    if not actual_task_name:
        actual_task_name = "null_filling"  # Default task
    return env.reset(actual_task_name)

@app.post("/step", response_model=StepResult)
def step(action: DataCleaningAction):
    return env.step(action)

@app.get("/state")
def state():
    return env.state()

@app.get("/health")
def health():
    return {"status": "ok"}
