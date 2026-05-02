# Keep the runtime Python aligned with CI and release validation.
FROM python:3.11-slim

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

# Install uv for lockfile-based dependency sync
RUN pip install --no-cache-dir uv==0.11.3

# Copy dependency manifests before application code for better layer caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies from the lockfile
RUN uv sync --locked --no-install-project --no-cache

# Copy application code
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

# Create a non-root user and switch to it
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose the bot HTTP port
EXPOSE 10000

# Run the modular bot entry point
CMD ["python3", "-m", "src.bot"]
