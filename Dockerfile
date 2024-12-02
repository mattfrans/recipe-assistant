# Use Python 3.11 as base image for better compatibility with the dependencies
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a directory for storing model cache and vector store data
RUN mkdir -p /app/data

# Set environment variable for model cache directory
ENV TRANSFORMERS_CACHE=/app/data/model_cache \
    SENTENCE_TRANSFORMERS_HOME=/app/data/st_cache

# Create a non-root user and switch to it
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Set Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Command to run the example
CMD ["python", "src/example.py"]
