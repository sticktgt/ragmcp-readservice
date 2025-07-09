FROM python:3.11-slim

WORKDIR /app

# Copy files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Default command
CMD ["python", "-m", "readservice.main"]
