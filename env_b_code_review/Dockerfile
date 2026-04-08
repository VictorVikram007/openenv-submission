# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_b_code_review\Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy shared modules
COPY shared/ ./shared/

# Copy environment specific files
COPY env_b_code_review/ ./env_b_code_review/

# Install dependencies
RUN pip install --no-cache-dir -r ./env_b_code_review/requirements.txt

WORKDIR /app/env_b_code_review

EXPOSE 7860

# Set Python path to find modules correctly
ENV PYTHONPATH=/app:$PYTHONPATH

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
