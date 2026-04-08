# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_a_data_cleaning\server.py
import sys
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from env_a_data_cleaning.environment import DataCleaningEnv, DataCleaningAction
from shared.base_models import StepResult
import json

app = FastAPI()
env = DataCleaningEnv()

# Custom OpenAPI schema to mark /reset body as optional
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Data Cleaning Environment",
        version="1.0.0",
        routes=app.routes,
    )
    # Make /reset endpoint body optional
    if "/reset" in openapi_schema["paths"]:
        if "post" in openapi_schema["paths"]["/reset"]:
            openapi_schema["paths"]["/reset"]["post"]["requestBody"] = {
                "required": False,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "task_name": {"type": "string", "nullable": True}
                            }
                        }
                    }
                }
            }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

class ResetRequest(BaseModel):
    task_name: Optional[str] = None

@app.post("/reset", response_model=StepResult)
async def reset(request: Request):
    """Reset environment with optional task_name."""
    task_name = None
    
    # Try to get from query params first
    task_name = request.query_params.get("task_name")
    
    # Try to parse body if no query param
    if not task_name:
        try:
            body = await request.body()
            if body:
                data = json.loads(body)
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
