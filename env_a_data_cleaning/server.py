# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_a_data_cleaning\server.py
import sys
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any

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
    """Reset environment with optional task_name."""
    task_name = None
    
    # Try to parse body if present
    try:
        content_type = request.headers.get("content-type", "")
        if content_type and "application/json" in content_type:
            body = await request.body()
            if body:
                data = await request.json()
                if isinstance(data, dict):
                    task_name = data.get("task_name")
    except:
        pass
    
    # Use default if not provided
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
