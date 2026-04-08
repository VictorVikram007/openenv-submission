# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_b_code_review\server.py
import sys
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from env_b_code_review.environment import CodeReviewEnv, CodeReviewAction
from shared.base_models import StepResult
import json

app = FastAPI()
env = CodeReviewEnv()

class ResetRequest(BaseModel):
    task_name: Optional[str] = None

@app.post("/reset", response_model=StepResult)
async def reset(request: Request):
    """Reset environment with optional task_name."""
    task_name = request.query_params.get("task_name")

    if not task_name:
        try:
            body = await request.json()
            if isinstance(body, dict):
                task_name = body.get("task_name")
        except Exception:
            # Ignore JSON parsing errors if body is empty or not valid JSON
            pass

    # Use default if not provided
    if not task_name:
        task_name = "bug_detection"
    
    return env.reset(task_name)

@app.post("/step", response_model=StepResult)
def step(action: CodeReviewAction):
    return env.step(action)

@app.get("/state")
def state():
    return env.state()

@app.get("/health")
def health():
    return {"status": "ok"}
