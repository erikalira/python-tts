# Keep the runtime Python aligned with CI and release validation.
#
# Two stages so the runtime image carries only what the bot needs at run time:
# uv (~57 MB) and the build-time pip metadata stay in the builder, and the
# virtualenv is copied in already owned by the runtime user, which avoids a
# recursive chown duplicating every dependency into an extra layer.

FROM python:3.11-slim AS builder

WORKDIR /app

# Install uv for lockfile-based dependency sync.
RUN pip install --no-cache-dir uv==0.11.3

# Copy dependency manifests before application code for better layer caching.
COPY pyproject.toml uv.lock ./

# Install runtime Python dependencies from the lockfile.
RUN uv sync --locked --no-default-groups --no-install-project --no-cache


FROM python:3.11-slim AS runtime

ARG APP_VERSION=local
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="tts-hotkey-windows-bot" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}"

# Set working directory
WORKDIR /app

# Install system dependencies (espeak-ng and ffmpeg), upgrading base packages first
# so vulnerability scans see the latest patched Debian packages.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends upgrade && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    espeak-ng \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create the non-root user before copying, so every COPY can land already-owned
# files instead of needing a recursive chown afterwards.
RUN useradd -m -u 1000 appuser

# The virtualenv is the largest artifact; copying it with --chown keeps it in a
# single layer rather than one layer to write and another to re-own.
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

ENV PATH="/app/.venv/bin:$PATH"

USER appuser

# Expose the bot HTTP port
EXPOSE 10000

# Run the modular bot entry point
CMD ["python3", "-m", "src.bot"]
