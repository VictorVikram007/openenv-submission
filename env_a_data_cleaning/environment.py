# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_a_data_cleaning\environment.py
import sys
from pathlib import Path
import pandas as pd
from io import StringIO
from typing import Any, Optional
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.base_models import BaseObservation, BaseAction, StepResult
from env_a_data_cleaning.tasks import TASKS
from env_a_data_cleaning.data_generator import generate_dirty_csv
from env_a_data_cleaning.graders import NullFillingGrader, TypeCoercionGrader, FullQAPipelineGrader


class DataCleaningObservation(BaseObservation):
    dirty_csv: str = ""
    schema: dict = {}
    null_count: int = 0


class DataCleaningAction(BaseAction):
    cleaned_csv: str
    issues_found: list = []
    transformations: list = []


class DataCleaningEnv:
    def __init__(self):
        self.current_task_config = None
        self.dirty_df = None
        self.clean_df = None
        self.step_count = 0
        self.episode_done = False
        self.graders = {
            "null_filling": NullFillingGrader(),
            "type_coercion_dedup": TypeCoercionGrader(),
            "full_qa_pipeline": FullQAPipelineGrader(),
        }

    def reset(self, task_name: str) -> StepResult:
        if task_name not in TASKS:
            raise ValueError(f"Task '{task_name}' not found.")

        self.current_task_config = TASKS[task_name]
        dirty_csv_str, clean_csv_str = generate_dirty_csv(self.current_task_config)

        self.dirty_df = pd.read_csv(StringIO(dirty_csv_str))
        self.clean_df = pd.read_csv(StringIO(clean_csv_str))

        self.step_count = 0
        self.episode_done = False

        obs = DataCleaningObservation(
            task_id=self.current_task_config["task_id"],
            step=self.step_count,
            task_instruction=self.current_task_config["instruction"],
            done=self.episode_done,
            dirty_csv=dirty_csv_str,
            schema=self.dirty_df.dtypes.apply(lambda x: x.name).to_dict(),
            null_count=int(self.dirty_df.isnull().sum().sum())
        )

        return StepResult(
            observation=obs.model_dump(),
            reward=0.0,
            done=False,
            info={}
        )

    def step(self, action: DataCleaningAction) -> StepResult:
        if self.episode_done:
            raise Exception("Episode is done, please reset.")
        self.step_count += 1

        task_id = self.current_task_config["task_id"]
        grader = self.graders[task_id]

        ground_truth_csv = self.clean_df.to_csv(index=False)
        if task_id == "full_qa_pipeline":
            score = grader.score(action.cleaned_csv, action.issues_found, ground_truth_csv)
        else:
            score = grader.score(action.cleaned_csv, ground_truth_csv)

        self.episode_done = True

        obs = DataCleaningObservation(
            task_id=task_id,
            step=self.step_count,
            task_instruction=self.current_task_config["instruction"],
            done=self.episode_done,
            dirty_csv="",
            schema={},
            null_count=0
        )

        return StepResult(
            observation=obs.model_dump(),
            reward=score,
            done=self.episode_done,
            info={"score_breakdown": {}}
        )

    def state(self) -> dict[str, Any]:
        return {
            "task_config": self.current_task_config,
            "step_count": self.step_count,
            "episode_done": self.episode_done,
        }