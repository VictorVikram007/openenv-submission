# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_a_data_cleaning\inference.py
import os
import sys
import requests
from openai import OpenAI

# Add shared to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.logging_utils import log_start, log_step, log_end

# --- Config ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")
# In a real scenario, you'd use a more secure way to handle API keys
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or "dummy-key"
SUCCESS_THRESHOLD = 0.5
ENV_NAME = "data-cleaning-qa-env"

client = OpenAI(api_key=API_KEY, base_url="https://router.huggingface.co/v1") # Using a placeholder for local dev

SYSTEM_PROMPT = """You are a data cleaning expert. You will receive a dirty CSV.
Your job is to clean it according to the instruction and return
ONLY the cleaned CSV as plain text, no explanation, no markdown.
First line must be the header row."""

def run_inference():
    tasks = ["null_filling", "type_coercion_dedup", "full_qa_pipeline"]
    
    for task in tasks:
        log_start(task, ENV_NAME, MODEL_NAME)
        
        # 1. Reset environment
        try:
            response = requests.post(f"{API_BASE_URL}/reset", json={"task_name": task})
            response.raise_for_status()
            result = response.json()
            obs = result['observation']
        except requests.RequestException as e:
            log_step(0, "reset", 0.0, True, str(e))
            log_end(False, 0, 0.0, [])
            continue

        # 2. Call LLM to get action
        prompt = f"Instruction: {obs['task_instruction']}\n\nDirty CSV:\n{obs['dirty_csv']}"
        
        try:
            chat_completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
            )
            cleaned_csv_content = chat_completion.choices[0].message.content
        except Exception as e:
            log_step(1, "llm_call", 0.0, True, str(e))
            log_end(False, 1, 0.0, [])
            continue

        # 3. Step environment
        action = {
            "cleaned_csv": cleaned_csv_content,
            "issues_found": [], # Placeholder for this env
            "transformations": [] # Placeholder
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/step", json=action)
            response.raise_for_status()
            step_result = response.json()
            
            reward = step_result['reward']
            done = step_result['done']
            
            log_step(1, "clean_csv", reward, done, None)
            
            # 4. Log end
            success = reward >= SUCCESS_THRESHOLD
            log_end(success, 1, reward, [reward])

        except requests.RequestException as e:
            log_step(1, "step", 0.0, True, str(e))
            log_end(False, 1, 0.0, [])
            continue

if __name__ == "__main__":
    run_inference()
