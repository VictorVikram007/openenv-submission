# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_a_data_cleaning\server.py
import sys
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query, Request
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from env_a_data_cleaning.environment import DataCleaningEnv, DataCleaningAction
from shared.base_models import StepResult
import json

app = FastAPI()
env = DataCleaningEnv()

class ResetRequest(BaseModel):
    task_name: Optional[str] = None

@app.post("/reset", response_model=StepResult)
async def reset(request: Request):
    """Reset environment. Accepts task_name via query parameter or request body."""
    task_name = request.query_params.get("task_name")
    
    # Try to get from request body if not in query params
    if not task_name:
        try:
            body = await request.json()
            task_name = body.get("task_name") if isinstance(body, dict) else None
        except:
            pass
    
    # Use default if still not found
    if not task_name:
        task_name = "null_filling"
    
    return env.reset(task_name)

@app.post("/step", response_model=StepResult)
def step(action: DataCleaningAction):
    return env.step(action)

@app.get("/state")
def state():
    return env.state()

@app.get("/health")
def health():
    return {"status": "ok"}
