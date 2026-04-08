# Deployment Guide

Complete instructions for deploying Meta OpenEnv environments locally, via Docker, and on Hugging Face Spaces.

## 📦 Table of Contents

1. [Live HF Spaces Deployment](#-hugging-face-spaces) (No setup required)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#-docker-deployment)
4. [Docker Compose (Full Stack)](#-docker-compose-full-stack)

---

## 🏠 Local Development Setup

### Prerequisites

- Python 3.10+
- pip or conda
- Git

### Data Cleaning Environment

```bash
# Navigate to environment
cd env_a_data_cleaning

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start API server
uvicorn server:app --reload --port 7860
```

The API will be available at `http://localhost:7860`

### Code Review Environment

In a separate terminal:

```bash
cd env_b_code_review

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start API server (different port)
uvicorn server:app --reload --port 7861
```

The API will be available at `http://localhost:7861`

### Gradio Interface (Optional)

In a third terminal:

```bash
# From root directory
python -m venv venv
source venv/bin/activate

# Install dependencies with Gradio
pip install -r requirements.txt
pip install gradio>=4.0.0

# Run Gradio interface
python app.py
```

Access the interface at `http://localhost:7860` (or find exact port in terminal output)

#### Environment Variables for Gradio Dev

```bash
export DATA_CLEANING_API=http://localhost:7860
export CODE_REVIEW_API=http://localhost:7861
python app.py
```

---

## 🐳 Docker Deployment

### Individual Environment Containers

#### Data Cleaning

```bash
cd env_a_data_cleaning

# Build image
docker build -t meta-data-cleaning:latest .

# Run container
docker run -p 7860:7860 \
  -e HF_TOKEN=your_api_key \
  -e MODEL_NAME=gpt-4 \
  meta-data-cleaning:latest
```

Test with:
```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "null_filling"}'
```

#### Code Review

```bash
cd env_b_code_review

# Build image
docker build -t meta-code-review:latest .

# Run container
docker run -p 7861:7860 \
  -e HF_TOKEN=your_api_key \
  -e MODEL_NAME=gpt-4 \
  meta-code-review:latest
```

Test with:
```bash
curl -X POST http://localhost:7861/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "bug_detection"}'
```

---

## 🎛️ Docker Compose (Full Stack)

Deploy all components (both APIs + Gradio interface) with a single command.

### Prerequisites

- Docker
- Docker Compose
- HF_TOKEN environment variable set (optional)

### Quick Start

```bash
# From root directory
docker-compose up -d
```

This starts:
- **Data Cleaning API** on port 7860 (http://localhost:7860)
- **Code Review API** on port 7861 (http://localhost:7861)
- **Gradio Interface** on port 7862 (http://localhost:7862)

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f data-cleaning
docker-compose logs -f code-review
docker-compose logs -f interface
```

### Stop Services

```bash
docker-compose down
```

### With API Key

```bash
HF_TOKEN=sk_your_key_here docker-compose up -d
```

### Rebuild Images

```bash
docker-compose up -d --build
```

---

## 🌐 Hugging Face Spaces

### ✅ Live Deployment Ready

These environments are **already deployed and ready to use online**:
- 🧹 [Data Cleaning & QA Environment](https://huggingface.co/spaces/vikram727/data-cleaning-qa-env)
- 🔍 [Code Review & Bug Fixing Environment](https://huggingface.co/spaces/vikram727/code-review-bug-fixing-env)

**No installation or setup required!** Just click the links above to start benchmarking.

---

### Deploy Your Own Space (Optional)

If you want to deploy your own instance to HF Spaces:

#### Option 1: Direct Docker Deployment

#### Setup

1. Create new Space on [Hugging Face](https://huggingface.co/new-space)
2. Choose "Docker" as SDK
3. Complete the form

#### Configure Docker

In your Space, use the `docker-compose.yml` with a small adjustment:

**space-docker-compose.yml** (for HF Spaces):
```yaml
version: '3.8'

services:
  data-cleaning:
    build:
      context: ./env_a_data_cleaning
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - MODEL_NAME=gpt-4
    expose:
      - 7860

  code-review:
    build:
      context: ./env_b_code_review
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - MODEL_NAME=gpt-4
    expose:
      - 7861

  interface:
    build: .
    ports:
      - "7860:7860"
    environment:
      - DATA_CLEANING_API=http://data-cleaning:7860
      - CODE_REVIEW_API=http://code-review:7860
```

#### Push to Space

```bash
# Clone your HF Space repository
git clone https://huggingface.co/spaces/your-username/your-space-name
cd your-space-name

# Copy files
cp -r ../meta/* .

# Push to HF
git add .
git commit -m "Add Meta OpenEnv environments"
git push
```

### Option 2: Gradio-Only Deployment

If you want a simpler deployment with just the Gradio interface:

#### Create Space with Python SDK

1. Create new Space on HF with "Gradio" SDK
2. Set environment variables in Space settings:
   - `DATA_CLEANING_API`: Your deployed data cleaning API URL
   - `CODE_REVIEW_API`: Your deployed code review API URL

#### Add `app.py`

```bash
cp app.py <your-space-repo>/
git add app.py
git commit -m "Add Gradio interface"
git push
```

#### Environment Variables

In HF Space settings, add:
```
DATA_CLEANING_API=http://data-cleaning-api-url
CODE_REVIEW_API=http://code-review-api-url
```

### Option 3: Deploy via GitHub to HF Spaces

1. Push code to GitHub
2. Connect GitHub repo to HF Space (in Space settings)
3. Space auto-deploys on push

---

## 🚀 Running Baseline Inference

### Local API Testing

```bash
# Start data cleaning API
cd env_a_data_cleaning
uvicorn server:app --port 7860

# In another terminal, run inference
export HF_TOKEN=sk_your_key
export MODEL_NAME=gpt-4
python inference.py
```

### Docker Container Testing

```bash
# Start container
docker run -p 7860:7860 \
  -e HF_TOKEN=sk_your_key \
  meta-data-cleaning:latest

# In another terminal, test
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "null_filling"}'
```

---

## 🔑 Managing API Keys

### For Local Development

```bash
# Temporary (current session only)
export HF_TOKEN=sk_your_key

# View
echo $HF_TOKEN

# Docker
docker run -e HF_TOKEN=$HF_TOKEN -p 7860:7860 meta-data-cleaning:latest
```

### For HF Spaces

1. Go to Space settings
2. Click "Repository secrets" or "Secrets & Tokens"
3. Add `HF_TOKEN` with your API key
4. Spaces will automatically inject as environment variable

### For Docker Compose

```bash
# Create .env file
echo "HF_TOKEN=sk_your_key" > .env

# Docker Compose reads .env automatically
docker-compose up -d
```

---

## 🧪 Testing Deployments

### Health Checks

```bash
# Data Cleaning
curl http://localhost:7860/health

# Code Review
curl http://localhost:7861/health
```

### Reset Task

```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "null_filling"}'
```

### Full Test Script

```python
import requests
import json

# Test data cleaning
print("Testing Data Cleaning...")
resp = requests.post("http://localhost:7860/reset", 
                    json={"task_name": "null_filling"})
print(f"Status: {resp.status_code}")
print(f"Observation keys: {resp.json()['observation'].keys()}")

# Test code review
print("\nTesting Code Review...")
resp = requests.post("http://localhost:7861/reset", 
                    json={"task_name": "bug_detection"})
print(f"Status: {resp.status_code}")
print(f"Observation keys: {resp.json()['observation'].keys()}")
```

---

## 📊 Performance Tips

### Local Development

- Use `--reload` flag for auto-restart on code changes
- Monitor memory: `watch -n 1 docker stats`

### Docker

- Use `.dockerignore` to exclude unnecessary files
- Multi-stage builds for smaller images
- Set resource limits: `docker run -m 512m --cpus 1.0`

### Gradio

- Batch requests for better performance
- Cache static assets
- Use `share=False` for local development, `share=True` for public access

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :7860

# Kill process
kill -9 <PID>

# Or use different port
uvicorn server:app --port 8000
```

### Connection refused

```bash
# Check if service is running
curl http://localhost:7860/health

# Check logs
docker logs meta-data-cleaning
```

### Out of Memory

```bash
# Increase Docker memory
docker update --memory 2g <container_id>

# Or rebuild with different compose settings
```

### API Key Issues

```bash
# Verify key is set
echo $HF_TOKEN

# Test with curl
curl -X POST http://router.huggingface.co/v1/chat/completions \
  -H "Authorization: Bearer $HF_TOKEN"
```

---

## 📝 Deployment Checklist

- [ ] All tests pass locally
- [ ] Docker images build successfully
- [ ] Environment variables configured
- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] Gradio interface accessible
- [ ] Baseline inference working
- [ ] Documentation updated
- [ ] Performance acceptable (<500ms latency)
- [ ] Logs are clean (no errors on startup)

---

## 📚 References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [HF Spaces Docker Guide](https://huggingface.co/docs/hub/spaces-sdks-docker)
- [Gradio Deployment](https://www.gradio.app/guides/deployment)
- [OpenEnv Spec](https://github.com/allenai/openenv)
