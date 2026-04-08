# Quick Start Guide

Get started with Meta OpenEnv environments in 5 minutes.

## 🌐 Live Demo (No Setup Required)

**Try online right now:**
- 🧹 [Data Cleaning Environment](https://huggingface.co/spaces/vikram727/data-cleaning-qa-env)
- 🔍 [Code Review Environment](https://huggingface.co/spaces/vikram727/code-review-bug-fixing-env)

No installation needed—just visit the links above!

## ⚡ Fastest Way (Use Online - No Setup!)

**Click to start benchmarking right now:**
- 🧹 [Data Cleaning Environment](https://huggingface.co/spaces/vikram727/data-cleaning-qa-env)
- 🔍 [Code Review Environment](https://huggingface.co/spaces/vikram727/code-review-bug-fixing-env)

No installation, configuration, or API keys needed!

---

## ⚡ Fastest Way (Docker Compose)

```bash
# 1. Clone/download this repo
# 2. Setup API key (optional for testing without API)
cp .env.example .env
# Edit .env and add your HF_TOKEN

# 3. Start everything with one command
docker-compose up -d

# 4. Open browser
# - Gradio Interface: http://localhost:7862
# - Data Cleaning API: http://localhost:7860
# - Code Review API: http://localhost:7861
```

Done! 🎉 Now you can use the interactive interface.

---

## 🚀 Without Docker (Python Only)

### Terminal 1: Data Cleaning API

```bash
cd env_a_data_cleaning
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --port 7860
```

### Terminal 2: Code Review API

```bash
cd env_b_code_review
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --port 7861
```

### Terminal 3: Gradio Interface (Optional)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open: http://localhost:7860

---

## 🌍 Prefer Online?

No Docker or Python setup needed! Use the live HF Spaces:
- [Data Cleaning](https://huggingface.co/spaces/vikram727/data-cleaning-qa-env)
- [Code Review](https://huggingface.co/spaces/vikram727/code-review-bug-fixing-env)

---

## 🧪 Test an API

### Data Cleaning

```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "null_filling"}'
```

### Code Review

```bash
curl -X POST http://localhost:7861/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "bug_detection"}'
```

### Python Script

```python
import requests

# Reset environment
resp = requests.post("http://localhost:7860/reset", 
                    json={"task_name": "null_filling"})
obs = resp.json()["observation"]

print("Task:", obs["task_instruction"])
print("Dirty CSV (first 300 chars):")
print(obs["dirty_csv"][:300])

# Submit solution
action = {
    "cleaned_csv": "age,salary,department,city,score\n25,85000,HR,New York,87.5",
    "issues_found": [],
    "transformations": []
}
result = requests.post("http://localhost:7860/step", json=action).json()
print(f"Reward: {result['reward']}")
```

---

## 📊 Tasks Available

### Data Cleaning
- `null_filling` - Fill missing values (Easy)
- `type_coercion_dedup` - Fix types and duplicates (Medium)
- `full_qa_pipeline` - Complete data cleaning (Hard)

### Code Review
- `bug_detection` - Find a bug (Easy)
- `security_review` - Find security issues (Medium)
- `full_pr_review` - Review multiple files (Hard)

---

## 📚 Full Documentation

- [Complete README](README.md) - Architecture & concepts
- [Data Cleaning Docs](env_a_data_cleaning/README.md) - Task details & grading
- [Code Review Docs](env_b_code_review/README.md) - Task details & grading
- [Deployment Guide](DEPLOYMENT.md) - Production setup

---

## 🆘 Troubleshooting

### Port already in use?
```bash
# Use different port
uvicorn server:app --port 8000
```

### Docker issues?
```bash
# Check logs
docker-compose logs -f

# Restart
docker-compose down && docker-compose up -d
```

### API not responding?
```bash
# Check health
curl http://localhost:7860/health

# Make sure services are running
docker-compose ps
```

---

## 📈 Run Baseline Inference

Benchmark against GPT-4:

```bash
export HF_TOKEN=sk_your_api_key
export MODEL_NAME=gpt-4

# Data Cleaning
python env_a_data_cleaning/inference.py

# Code Review
python env_b_code_review/inference.py
```

---

## 🎯 Next Steps

1. **Explore Tasks**: Use Gradio interface to try all 6 tasks
2. **Build Agent**: Implement your own agent to solve tasks
3. **Benchmark**: Compare your agent against baselines
4. **Deploy**: Push to HF Spaces for public ranking

---

## 💡 Tips

- Tasks are deterministic (same input = same output)
- Rewards are 0.0-1.0 (higher is better)
- Each task is single-step (one action per reset)
- Check task instructions for exact requirements
- Review sample code in source files for implementation details

---

## 🔗 Resources

- [OpenEnv Specification](https://github.com/allenai/openenv)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Gradio Guide](https://www.gradio.app/)
- [Docker Docs](https://docs.docker.com/)

---

Happy benchmarking! 🚀
