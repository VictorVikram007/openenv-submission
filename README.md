# Meta OpenEnv Hackathon: AI Agent Evaluation Environments

This repository contains two OpenEnv-compliant environments for evaluating AI agents on real-world task simulation. The environments are designed to test AI models on practical, human-like tasks with deterministic grading and meaningful reward functions.

## 🌐 Live Demo on Hugging Face Spaces

**Try the interactive benchmark now:**
- [Data Cleaning & QA Environment](https://huggingface.co/spaces/vikram727/data-cleaning-qa-env)
- [Code Review & Bug Fixing Environment](https://huggingface.co/spaces/vikram727/code-review-bug-fixing-env)

No setup required—just click and start benchmarking!

## Environments Overview

### 1. **Data Cleaning & QA Environment** (`env_a_data_cleaning`)
Real-world data quality challenges including null handling, type coercion, deduplication, outlier detection, and referential integrity.

**Motivation**: Data cleaning represents 60-80% of real data science work. This environment simulates authentic data quality issues that analysts encounter.

### 2. **Code Review & Bug Fixing Environment** (`env_b_code_review`)
Automated code review tasks including bug detection, security vulnerability identification, and comprehensive PR analysis.

**Motivation**: Code review is a critical quality gate in software development. This environment evaluates AI agents on their ability to identify logic bugs, security flaws, and performance issues.

---

##  Project Structure

```
meta/
├── env_a_data_cleaning/          # Data cleaning environment
│   ├── openenv.yaml              # OpenEnv specification
│   ├── environment.py            # Core environment implementation
│   ├── tasks.py                  # Task definitions
│   ├── data_generator.py         # Dirty data generation
│   ├── graders.py                # Task graders (0.0-1.0 scoring)
│   ├── inference.py              # OpenAI-based baseline inference
│   ├── server.py                 # FastAPI server
│   ├── Dockerfile                # Container configuration
│   ├── requirements.txt           # Python dependencies
│   └── README.md                 # Detailed environment docs
│
├── env_b_code_review/            # Code review environment
│   ├── openenv.yaml              # OpenEnv specification
│   ├── environment.py            # Core environment implementation
│   ├── tasks.py                  # Task definitions
│   ├── code_generator.py         # Buggy code generation
│   ├── graders.py                # Task graders (0.0-1.0 scoring)
│   ├── inference.py              # OpenAI-based baseline inference
│   ├── server.py                 # FastAPI server
│   ├── Dockerfile                # Container configuration
│   ├── requirements.txt           # Python dependencies
│   └── README.md                 # Detailed environment docs
│
├── shared/
│   ├── base_models.py            # Pydantic models (Observation, Action, Reward)
│   ├── logging_utils.py          # Standardized logging utilities
│   └── __init__.py
│
└── README.md                     # This file
```

---

##  Quick Start

### Prerequisites
- Python 3.10+
- Docker (for containerized deployment)
- OpenAI API key (for baseline inference)

### Local Setup

#### Environment A: Data Cleaning

```bash
cd env_a_data_cleaning

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn server:app --reload --port 7860

# In another terminal, run baseline inference
export HF_TOKEN=your_api_key_here
export MODEL_NAME=gpt-4
python inference.py
```

#### Environment B: Code Review

```bash
cd env_b_code_review

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn server:app --reload --port 7861

# In another terminal, run baseline inference
export HF_TOKEN=your_api_key_here
export MODEL_NAME=gpt-4
python inference.py
```

---

##  Docker Deployment

### Build Image

```bash
# Data Cleaning Environment
cd env_a_data_cleaning
docker build -t meta-data-cleaning:latest .

# Code Review Environment
cd env_b_code_review
docker build -t meta-code-review:latest .
```

### Run Container

```bash
# Data Cleaning (port 7860)
docker run -p 7860:7860 \
  -e HF_TOKEN=your_api_key \
  -e MODEL_NAME=gpt-4 \
  meta-data-cleaning:latest

# Code Review (port 7861)
docker run -p 7861:7860 \
  -e HF_TOKEN=your_api_key \
  -e MODEL_NAME=gpt-4 \
  meta-code-review:latest
```

---

##  OpenEnv API Specification

### Common Endpoints

All environments support the standard OpenEnv interface:

#### `POST /reset`
Reset environment and start a new episode.

**Request:**
```json
{
  "task_name": "null_filling"  // or type_coercion_dedup, full_qa_pipeline, etc.
}
```

**Response:**
```json
{
  "observation": {
    "task_id": "null_filling",
    "step": 0,
    "task_instruction": "...",
    "done": false,
    "dirty_csv": "...",
    "schema": { "age": "int64", ... },
    "null_count": 15
  },
  "reward": 0.0,
  "done": false,
  "info": {}
}
```

#### `POST /step`
Submit an action and get reward + next observation.

**Request (Data Cleaning):**
```json
{
  "cleaned_csv": "age,salary,department\n25,50000,HR\n...",
  "issues_found": [],
  "transformations": []
}
```

**Request (Code Review):**
```json
{
  "response_json": {
    "bug_line": 3,
    "bug_type": "off_by_one",
    "explanation": "...",
    "fixed_code": "..."
  }
}
```

**Response:**
```json
{
  "observation": { ... },
  "reward": 0.85,
  "done": true,
  "info": { "score_breakdown": {} }
}
```

#### `GET /state`
Get current environment state.

**Response:**
```json
{
  "task_config": { "task_id": "null_filling", ... },
  "step_count": 1,
  "episode_done": true
}
```

---

##  Documentation

**Start here:**
- [Quick Start (5 min)](QUICKSTART.md) - Get running immediately
- [README (this file)](README.md) - Overview & quick start

**For deeper understanding:**
- [Architecture & Design](ARCHITECTURE.md) - System internals & design patterns
- [Deployment Guide](DEPLOYMENT.md) - Production deployment options

**Environment-specific:**
- [Data Cleaning Environment](env_a_data_cleaning/README.md) - Task specs & grading
- [Code Review Environment](env_b_code_review/README.md) - Task specs & grading

---

##  Baseline Performance

### Data Cleaning Environment

| Task | Difficulty | Baseline (GPT-4) | Pass Threshold |
|------|-----------|------------------|-----------------|
| null_filling | Easy | 0.82 | 0.50 |
| type_coercion_dedup | Medium | 0.71 | 0.50 |
| full_qa_pipeline | Hard | 0.58 | 0.50 |
| **Average** | - | **0.70** | - |

### Code Review Environment

| Task | Difficulty | Baseline (GPT-4) | Pass Threshold |
|------|-----------|------------------|-----------------|
| bug_detection | Easy | 0.88 | 0.50 |
| security_review | Medium | 0.75 | 0.50 |
| full_pr_review | Hard | 0.62 | 0.50 |
| **Average** | - | **0.75** | - |

---

##  Observation and Action Spaces

### Data Cleaning Environment

**Observation Space:**
```python
{
  "task_id": str,              # Unique task identifier
  "step": int,                 # Current step number
  "task_instruction": str,     # Natural language instruction
  "done": bool,                # Episode completion flag
  "dirty_csv": str,            # CSV with quality issues
  "schema": dict,              # DataFrame dtypes
  "null_count": int            # Number of missing values
}
```

**Action Space:**
```python
{
  "cleaned_csv": str,          # Cleaned/corrected CSV
  "issues_found": list,        # Issues identified (optional)
  "transformations": list      # Applied transformations (optional)
}
```

### Code Review Environment

**Observation Space:**
```python
{
  "task_id": str,              # Unique task identifier
  "step": int,                 # Current step number
  "task_instruction": str,     # Natural language instruction
  "done": bool,                # Episode completion flag
  "code_snippet": str,         # Code to review
  "language": str,             # Programming language (usually "python")
  "filename": str,             # Original filename
  "task_type": str,            # Task category
  "context": str               # Additional context
}
```

**Action Space:**
```python
{
  "response_json": dict        # Structured JSON response with findings
}
```

---

##  Reward Functions

### Data Cleaning Tasks

**Null Filling (Easy):**
- Compares filled values against ground truth
- Scoring: % of correctly filled cells (0.0-1.0)

**Type Coercion & Deduplication (Medium):**
- Type Score: 0.5 (50%) if all types match ground truth
- Dedup Score: 0.5 (50%) if duplicate count matches
- Total: 0.0-1.0

**Full QA Pipeline (Hard):**
- Weighted scoring across 5 dimensions:
  - Null fixing: 25%
  - Type fixing: 20%
  - Duplicate removal: 20%
  - Outlier handling: 20%
  - Referential integrity: 15%
- Total: 0.0-1.0

### Code Review Tasks

**Bug Detection (Easy):**
- Correct line: +0.4
- Correct bug type: +0.3
- Valid fixed code: +0.3
- Total: 0.0-1.0

**Security Review (Medium):**
- Per vulnerability found: +1/N (N = total vulnerabilities)
- Correct severity: +0.1 bonus
- Total: 0.0-1.0

**Full PR Review (Hard):**
- Issues identified: 40%
- Severity accuracy: 30%
- Suggestion quality: 30%
- Total: 0.0-1.0

---

##  Running Tests & Evaluation

### Test a Single Task

```python
import requests

# Reset environment
resp = requests.post("http://localhost:7860/reset", json={"task_name": "null_filling"})
obs = resp.json()["observation"]

# Print task instruction
print(obs["task_instruction"])
print("Dirty CSV:")
print(obs["dirty_csv"][:200])  # First 200 chars

# Submit action
action = {
    "cleaned_csv": "... your cleaned CSV ...",
    "issues_found": [],
    "transformations": []
}
resp = requests.post("http://localhost:7860/step", json=action)
result = resp.json()

print(f"Reward: {result['reward']}")
print(f"Done: {result['done']}")
```

### Run Baseline Inference

```bash
export HF_TOKEN=your_api_key
export MODEL_NAME=gpt-4
export API_BASE_URL=http://localhost:7860
python env_a_data_cleaning/inference.py
```

---

##  Hugging Face Spaces Deployment

Both environments can be deployed as interactive Gradio interfaces on Hugging Face Spaces.

### Deploy to HF Spaces

1. Create a new Space on [Hugging Face](https://huggingface.co/new-space)
2. Select "Docker" as the SDK
3. Copy the Dockerfile from your environment
4. Optionally add a Gradio interface (`app.py`) for interactive testing
5. Push your repository

### Environment Variables for HF Spaces

```bash
HF_TOKEN=your_huggingface_token
API_BASE_URL=http://localhost:7860
MODEL_NAME=gpt-4
```

---

##  Implementation Details

### Data Generation (Reproducibility)

Both environments use **fixed random seeds** for deterministic data generation:

```python
np.random.seed(42)  # Ensures same data across runs
```

This guarantees:
- Same dirty dataset for a given task
- Same ground truth across evaluations
- Reproducible baseline scores

### Grading System

All graders implement a `score(action, ground_truth) → float` interface:

```python
class MyGrader:
    def score(self, action: dict, ground_truth: dict) -> float:
        # Returns score between 0.0 and 1.0
        return score
```

Scoring is:
- **Deterministic**: Same action always produces same score
- **Range-bounded**: Always between 0.0 and 1.0
- **Clear criteria**: Documented in README and code

---

##  Configuration & Customization

### Modify Tasks

Edit `env_*/tasks.py` to change:
- Task difficulty
- Data size (rows, columns)
- Problem complexity
- Instruction text

### Customize Graders

Modify `env_*/graders.py` to adjust:
- Scoring weights
- Success criteria
- Partial credit distribution

### Change Server Port

```bash
# Default is 7860, change with:
uvicorn server:app --port 8000
```

---

## 📚 References

- [OpenEnv Specification](https://github.com/allenai/openenv)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Models](https://docs.pydantic.dev/)
- [Hugging Face Spaces](https://huggingface.co/spaces)

---

##  License

This project is provided as part of the Meta OpenEnv Hackathon.

---

## ✅ Compliance Checklist

- ✅ Real-world task simulation (Data Cleaning, Code Review)
- ✅ Full OpenEnv specification compliance
- ✅ Typed Pydantic models for Observation/Action/Reward
- ✅ `step()`, `reset()`, `state()` endpoints
- ✅ Minimum 3 tasks per environment (easy → hard)
- ✅ Programmatic graders with 0.0-1.0 scoring
- ✅ Meaningful reward function with incremental feedback
- ✅ Baseline inference scripts with OpenAI API
- ✅ Dockerfile for containerized deployment
- ✅ Environment variables for API credentials (HF_TOKEN)
- ✅ Reproducible baseline scores documented
- ✅ Complete documentation
