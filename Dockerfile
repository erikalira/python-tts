# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies (espeak-ng and ffmpeg)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    espeak-ng \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user and switch to it
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port (Render provides this via $PORT)
EXPOSE 10000

# Run the application with gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 --log-level info wsgi:app
