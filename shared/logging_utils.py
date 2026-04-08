# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\shared\logging_utils.py
from typing import Optional, List

def log_start(task: str, env: str, model: str) -> None:
    """
    Logs the start of a task.
    Format: [START] task=<task> env=<env> model=<model>
    """
    print(f"[START] task={task} env={env} model={model}")

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    """
    Logs a single step of a task.
    Format: [STEP] step=<n> action=<action> reward=<0.00> done=<true|false> error=<msg|null>
    """
    reward_str = f"{reward:.2f}"
    done_str = str(done).lower()
    error_str = error if error is not None else "null"
    # Truncate action for logging if it's too long
    action_str = (action[:100] + '...') if len(action) > 100 else action
    print(f"[STEP] step={step} action={action_str} reward={reward_str} done={done_str} error={error_str}")

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    """
    Logs the end of a task.
    Format: [END] success=<true|false> steps=<n> score=<0.000> rewards=<r1,r2,...,rn>
    """
    success_str = str(success).lower()
    score_str = f"{score:.3f}"
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    print(f"[END] success={success_str} steps={steps} score={score_str} rewards={rewards_str}")
