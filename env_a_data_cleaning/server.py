# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_a_data_cleaning\server.py
from fastapi import FastAPI
from pydantic import BaseModel

from env_a_data_cleaning.environment import DataCleaningEnv, DataCleaningAction
from shared.base_models import StepResult

app = FastAPI()
env = DataCleaningEnv()

class ResetRequest(BaseModel):
    task_name: str

@app.post("/reset", response_model=StepResult)
def reset(request: ResetRequest):
    return env.reset(request.task_name)

@app.post("/step", response_model=StepResult)
def step(action: DataCleaningAction):
    return env.step(action)

@app.get("/state")
def state():
    return env.state()

@app.get("/health")
def health():
    return {"status": "ok"}
