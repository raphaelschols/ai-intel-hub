# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Generate initial data, start scheduler in background, then Flask app
CMD python -c "from pipeline.scheduler import run_weekly_summary; run_weekly_summary()" && \
    python pipeline/scheduler.py & \
    python -m flask --app app run --host=0.0.0.0 --port=8080