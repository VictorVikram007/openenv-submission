# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_b_code_review\server.py
from fastapi import FastAPI
from pydantic import BaseModel

from env_b_code_review.environment import CodeReviewEnv, CodeReviewAction
from shared.base_models import StepResult

app = FastAPI()
env = CodeReviewEnv()

class ResetRequest(BaseModel):
    task_name: str

@app.post("/reset", response_model=StepResult)
def reset(request: ResetRequest):
    return env.reset(request.task_name)

@app.post("/step", response_model=StepResult)
def step(action: CodeReviewAction):
    return env.step(action)

@app.get("/state")
def state():
    return env.state()

@app.get("/health")
def health():
    return {"status": "ok"}
