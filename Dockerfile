# Use Python 3.13 slim image
FROM python:3.13-slim

ARG APP_VERSION=local
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="tts-hotkey-windows-bot" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}"

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

# Expose the bot HTTP port
EXPOSE 10000

# Run the modular bot entry point
CMD ["python3", "-m", "src.bot"]
