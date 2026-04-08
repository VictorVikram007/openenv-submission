# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_b_code_review\server.py
import sys
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Body
from pydantic import BaseModel

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
def reset(req: ResetRequest = Body(default=ResetRequest())):
    """Reset environment with optional task_name."""
    task_name = req.task_name if req.task_name else "bug_detection"
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
