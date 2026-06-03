# Dockerfile
# ============================================
# DOCKER IMAGE
# ============================================

FROM python:3.10-slim

WORKDIR /app

# System packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App files
COPY . .

# Create directories
RUN mkdir -p logs data

# Run
CMD ["python", "main.py"]
