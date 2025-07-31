FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ curl build-essential libpq-dev \
        libmagic1 pandoc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install Python dependencies
COPY requirements.txt .
COPY constraints.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt -c constraints.txt

# Copy project files last (to leverage layer caching)
COPY . ./readservice/

# Default entrypoint for K8s deployments (can override in cronjob)
CMD ["python", "-m", "readservice.main"]
