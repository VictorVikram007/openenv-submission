# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_a_data_cleaning\Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy shared modules
COPY shared/ ./shared/

# Copy environment specific files
COPY env_a_data_cleaning/ ./env_a_data_cleaning/

# Install dependencies
RUN pip install --no-cache-dir -r ./env_a_data_cleaning/requirements.txt

WORKDIR /app/env_a_data_cleaning

EXPOSE 7860

# Set Python path to find modules correctly
ENV PYTHONPATH=/app:$PYTHONPATH

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
