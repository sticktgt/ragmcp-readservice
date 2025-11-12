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

RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt -c constraints.txt

ENV TIKTOKEN_CACHE_DIR=/opt/tiktoken-cache
RUN mkdir -p "$TIKTOKEN_CACHE_DIR" && chmod -R 755 "$TIKTOKEN_CACHE_DIR"

# TokenTextSplitter pre-cache tiktoken encodings
RUN python -c "import tiktoken; [tiktoken.get_encoding(n) for n in ['cl100k_base','o200k_base','p50k_base','r50k_base']]; print('[tiktoken] cache populated')"

RUN mkdir -p /usr/share/nltk_data && \
    python -m nltk.downloader -d /usr/share/nltk_data punkt averaged_perceptron_tagger

ENV NLTK_DATA=/usr/share/nltk_data
# Copy project files last (to leverage layer caching)
COPY . ./readservice/

# Default entrypoint for K8s deployments (can override in cronjob)
CMD ["python", "-m", "readservice.main"]
