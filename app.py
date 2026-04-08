#!/usr/bin/env python3
"""
Gradio Interface for Meta OpenEnv Environments
Allows interactive testing of Data Cleaning and Code Review tasks via HF Spaces
"""

import gradio as gr
import requests
import json
import os
from typing import Tuple

# Configuration
DATA_CLEANING_API = os.getenv("DATA_CLEANING_API", "http://localhost:7860")
CODE_REVIEW_API = os.getenv("CODE_REVIEW_API", "http://localhost:7861")

# =============================================================================
# DATA CLEANING ENVIRONMENT
# =============================================================================

def reset_data_cleaning(task_name: str) -> Tuple[str, str, str, float]:
    """Reset data cleaning environment"""
    try:
        resp = requests.post(
            f"{DATA_CLEANING_API}/reset",
            json={"task_name": task_name},
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
        obs = data["observation"]
        
        return (
            obs["task_instruction"],
            obs["dirty_csv"],
            json.dumps(obs["schema"], indent=2),
            float(obs["null_count"])
        )
    except Exception as e:
        return f"Error: {str(e)}", "", "{}", 0.0

def submit_data_cleaning(cleaned_csv: str) -> Tuple[float, str, bool]:
    """Submit cleaned CSV and get reward"""
    try:
        action = {
            "cleaned_csv": cleaned_csv,
            "issues_found": [],
            "transformations": []
        }
        resp = requests.post(
            f"{DATA_CLEANING_API}/step",
            json=action,
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        reward = float(result["reward"])
        success = "✅ PASSED" if reward >= 0.5 else "❌ FAILED"
        
        return (
            reward,
            f"Reward: {reward:.3f}\nStatus: {success}",
            reward >= 0.5
        )
    except Exception as e:
        return 0.0, f"Error: {str(e)}", False

# =============================================================================
# CODE REVIEW ENVIRONMENT
# =============================================================================

def reset_code_review(task_name: str) -> Tuple[str, str, str]:
    """Reset code review environment"""
    try:
        resp = requests.post(
            f"{CODE_REVIEW_API}/reset",
            json={"task_name": task_name},
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
        obs = data["observation"]
        
        return (
            obs["task_instruction"],
            obs["code_snippet"],
            f"Language: {obs['language']}\nFile: {obs['filename']}"
        )
    except Exception as e:
        return f"Error: {str(e)}", "", ""

def submit_code_review(response_json: str) -> Tuple[float, str, bool]:
    """Submit code review and get reward"""
    try:
        response_data = json.loads(response_json)
        action = {"response_json": response_data}
        
        resp = requests.post(
            f"{CODE_REVIEW_API}/step",
            json=action,
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        reward = float(result["reward"])
        success = "✅ PASSED" if reward >= 0.5 else "❌ FAILED"
        
        return (
            reward,
            f"Reward: {reward:.3f}\nStatus: {success}",
            reward >= 0.5
        )
    except json.JSONDecodeError as e:
        return 0.0, f"Invalid JSON: {str(e)}", False
    except Exception as e:
        return 0.0, f"Error: {str(e)}", False

# =============================================================================
# GRADIO INTERFACE
# =============================================================================

def create_interface() -> gr.Blocks:
    """Create Gradio interface with tabs for each environment"""
    
    with gr.Blocks(title="Meta OpenEnv Interactive Benchmark", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🚀 Meta OpenEnv Interactive Benchmark
        
        Evaluate AI agents on real-world task simulation. Choose an environment and task to get started.
        
        - **Data Cleaning**: Fix data quality issues (nulls, types, duplicates, outliers)
        - **Code Review**: Identify bugs, security issues, and code quality problems
        """)
        
        # =================================================================
        # DATA CLEANING TAB
        # =================================================================
        with gr.Tab("📊 Data Cleaning & QA"):
            gr.Markdown("""
            ### Data Cleaning & Quality Assurance
            
            Fix real-world data quality issues:
            - **Easy**: Fill null values with appropriate strategies (mean/mode)
            - **Medium**: Fix type inconsistencies and remove duplicates
            - **Hard**: Comprehensive QA pipeline (nulls, types, duplicates, outliers, integrity)
            """)
            
            with gr.Row():
                dc_task = gr.Dropdown(
                    choices=["null_filling", "type_coercion_dedup", "full_qa_pipeline"],
                    value="null_filling",
                    label="Task",
                    scale=1
                )
                dc_reset_btn = gr.Button("🔄 Reset Task", scale=1)
            
            with gr.Row():
                with gr.Column(scale=1):
                    dc_instruction = gr.Textbox(
                        label="Task Instruction",
                        lines=3,
                        interactive=False
                    )
                    dc_schema = gr.Code(
                        label="Schema",
                        language="json",
                        interactive=False
                    )
                    dc_null_count = gr.Number(
                        label="Null Count",
                        interactive=False
                    )
                
                with gr.Column(scale=2):
                    dc_dirty_csv = gr.Textbox(
                        label="Dirty CSV (Input)",
                        lines=10,
                        interactive=False,
                        max_lines=20
                    )
            
            dc_cleaned_csv = gr.Textbox(
                label="Cleaned CSV (Output)",
                placeholder="Paste your cleaned CSV here...",
                lines=10,
                max_lines=20
            )
            
            dc_submit_btn = gr.Button("✅ Submit Solution")
            
            with gr.Row():
                dc_reward = gr.Number(label="Reward Score", scale=1)
                dc_result = gr.Textbox(label="Result", scale=2, interactive=False)
                dc_passed = gr.Checkbox(label="Passed?", scale=1, interactive=False)
            
            # Event handlers for data cleaning
            dc_reset_btn.click(
                fn=reset_data_cleaning,
                inputs=[dc_task],
                outputs=[dc_instruction, dc_dirty_csv, dc_schema, dc_null_count]
            )
            
            dc_submit_btn.click(
                fn=submit_data_cleaning,
                inputs=[dc_cleaned_csv],
                outputs=[dc_reward, dc_result, dc_passed]
            )
        
        # =================================================================
        # CODE REVIEW TAB
        # =================================================================
        with gr.Tab("🔍 Code Review & Bug Fixing"):
            gr.Markdown("""
            ### Code Review & Bug Detection
            
            Review and fix Python code:
            - **Easy**: Identify a single bug (off-by-one, wrong operator, etc.)
            - **Medium**: Find security vulnerabilities (SQL injection, hardcoded secrets, etc.)
            - **Hard**: Comprehensive PR review across multiple files
            """)
            
            with gr.Row():
                cr_task = gr.Dropdown(
                    choices=["bug_detection", "security_review", "full_pr_review"],
                    value="bug_detection",
                    label="Task",
                    scale=1
                )
                cr_reset_btn = gr.Button("🔄 Reset Task", scale=1)
            
            with gr.Row():
                with gr.Column(scale=1):
                    cr_instruction = gr.Textbox(
                        label="Task Instruction",
                        lines=3,
                        interactive=False
                    )
                    cr_metadata = gr.Textbox(
                        label="Metadata",
                        interactive=False
                    )
                
                with gr.Column(scale=2):
                    cr_code = gr.Code(
                        label="Code to Review",
                        language="python",
                        interactive=False,
                        lines=15
                    )
            
            cr_response = gr.Code(
                label="Your Review (JSON)",
                language="json",
                lines=15,
                placeholder='''{
  "bug_line": 3,
  "bug_type": "off_by_one",
  "explanation": "...",
  "fixed_code": "..."
}'''
            )
            
            cr_submit_btn = gr.Button("✅ Submit Review")
            
            with gr.Row():
                cr_reward = gr.Number(label="Reward Score", scale=1)
                cr_result = gr.Textbox(label="Result", scale=2, interactive=False)
                cr_passed = gr.Checkbox(label="Passed?", scale=1, interactive=False)
            
            # Event handlers for code review
            cr_reset_btn.click(
                fn=reset_code_review,
                inputs=[cr_task],
                outputs=[cr_instruction, cr_code, cr_metadata]
            )
            
            cr_submit_btn.click(
                fn=submit_code_review,
                inputs=[cr_response],
                outputs=[cr_reward, cr_result, cr_passed]
            )
        
        # =================================================================
        # INFO TAB
        # =================================================================
        with gr.Tab("ℹ️ Information"):
            gr.Markdown("""
            ## About This Benchmark
            
            ### Meta OpenEnv Hackathon
            
            This interactive interface demonstrates OpenEnv-compliant environments for evaluating AI agents on real-world tasks:
            
            #### Environments
            
            1. **Data Cleaning & QA** (`env_a_data_cleaning`)
               - Real-world data quality challenges
               - Tasks: null filling, type coercion, full QA pipeline
               - Difficulty: Easy → Hard
            
            2. **Code Review & Bug Fixing** (`env_b_code_review`)
               - Authentic code review scenarios
               - Tasks: bug detection, security review, PR analysis
               - Difficulty: Easy → Hard
            
            #### OpenEnv Compliance
            
            ✅ Typed Observation/Action/Reward models (Pydantic)
            ✅ Standard API: `reset()`, `step()`, `state()`
            ✅ Deterministic grading (0.0-1.0)
            ✅ Reproducible data generation (fixed seeds)
            ✅ Real-world task simulation
            ✅ Baseline inference (OpenAI API)
            ✅ Docker containerization
            ✅ Complete documentation
            
            #### Reward Function
            
            - **Meaningful feedback**: Scores provide incremental progress signals
            - **Deterministic**: Same action always produces same score
            - **Range-bounded**: Always 0.0 (failure) to 1.0 (perfect)
            - **Task-specific**: Weighted scoring for multi-faceted tasks
            
            #### Getting Started
            
            1. Choose an environment (Data Cleaning or Code Review)
            2. Select a task (Easy, Medium, or Hard)
            3. Click "Reset Task" to get started
            4. Read the instruction and examine the data/code
            5. Submit your solution
            6. Get instant feedback with a numerical reward score
            
            #### API Endpoints
            
            - `POST /reset` - Start new episode
            - `POST /step` - Submit action
            - `GET /state` - Get current state
            - `GET /health` - Health check
            
            #### Example Usage
            
            ```bash
            # Data Cleaning
            curl -X POST http://localhost:7860/reset \\
              -H "Content-Type: application/json" \\
              -d '{"task_name": "null_filling"}'
            
            # Code Review
            curl -X POST http://localhost:7861/reset \\
              -H "Content-Type: application/json" \\
              -d '{"task_name": "bug_detection"}'
            ```
            
            #### Documentation
            
            - [Root README](README.md)
            - [Data Cleaning README](env_a_data_cleaning/README.md)
            - [Code Review README](env_b_code_review/README.md)
            
            #### Baseline Performance (GPT-4)
            
            **Data Cleaning:**
            - null_filling: 0.82
            - type_coercion_dedup: 0.71
            - full_qa_pipeline: 0.58
            - Average: 0.70
            
            **Code Review:**
            - bug_detection: 0.88
            - security_review: 0.75
            - full_pr_review: 0.62
            - Average: 0.75
            
            #### Architecture
            
            - **Backend**: FastAPI servers (separate for each environment)
            - **Frontend**: Gradio interface
            - **Models**: Pydantic for type safety
            - **Graders**: Deterministic scoring functions
            - **Data**: Reproducible generation with fixed seeds
            
            #### Key Features
            
            - 🎯 Real-world task simulation
            - 📊 Deterministic evaluation
            - 🔄 Reproducible baselines
            - 🐳 Docker-ready
            - 📈 Meaningful reward signals
            - ✅ Full OpenEnv compliance
            """)
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
