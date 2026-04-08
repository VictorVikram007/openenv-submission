# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_b_code_review\environment.py
from typing import Any, Dict
from pydantic import BaseModel
from shared.base_models import BaseObservation, BaseAction, StepResult
from env_b_code_review.tasks import TASKS
from env_b_code_review.code_generator import generate_buggy_code
from env_b_code_review.graders import BugDetectionGrader, SecurityReviewGrader, FullPRReviewGrader


class CodeReviewObservation(BaseObservation):
    code_snippet: str = ""
    language: str = "python"
    filename: str = "solution.py"
    task_type: str = ""
    context: str = ""


class CodeReviewAction(BaseAction):
    response_json: Dict[str, Any]


class CodeReviewEnv:
    def __init__(self):
        self.current_task_config = None
        self.buggy_code = None
        self.ground_truth = None
        self.step_count = 0
        self.episode_done = False
        self.graders = {
            "bug_detection": BugDetectionGrader(),
            "security_review": SecurityReviewGrader(),
            "full_pr_review": FullPRReviewGrader(),
        }

    def reset(self, task_name: str) -> StepResult:
        if task_name not in TASKS:
            raise ValueError(f"Task '{task_name}' not found.")

        self.current_task_config = TASKS[task_name]
        self.buggy_code, self.ground_truth = generate_buggy_code(self.current_task_config)

        self.step_count = 0
        self.episode_done = False

        obs = CodeReviewObservation(
            task_id=self.current_task_config["task_id"],
            step=self.step_count,
            task_instruction=self.current_task_config["instruction"],
            done=self.episode_done,
            code_snippet=self.buggy_code,
            language=self.current_task_config["language"],
            filename="solution.py",
            task_type=self.current_task_config["task_id"],
            context="Review the following code snippet carefully."
        )

        return StepResult(
            observation=obs.model_dump(),
            reward=0.0,
            done=False,
            info={}
        )

    def step(self, action: CodeReviewAction) -> StepResult:
        if self.episode_done:
            raise Exception("Episode is done, please reset.")
        self.step_count += 1

        task_id = self.current_task_config["task_id"]
        grader = self.graders[task_id]

        score = grader.score(action.response_json, self.ground_truth)
        self.episode_done = True

        obs = CodeReviewObservation(
            task_id=task_id,
            step=self.step_count,
            task_instruction=self.current_task_config["instruction"],
            done=self.episode_done,
            code_snippet="",
            language=self.current_task_config["language"],
            filename="solution.py",
            task_type=task_id,
            context=""
        )

        return StepResult(
            observation=obs.model_dump(),
            reward=score,
            done=self.episode_done,
            info={"score_breakdown": {}}
        )

    def state(self) -> dict[str, Any]:
        safe_task_config = self.current_task_config.copy() if self.current_task_config else {}
        safe_task_config.pop("bug_types", None)
        safe_task_config.pop("vulnerability_types", None)
        safe_task_config.pop("issue_types", None)
        return {
            "task_config": safe_task_config,
            "buggy_code": self.buggy_code,
            "step_count": self.step_count,
            "episode_done": self.episode_done,
        }