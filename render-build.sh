#!/usr/bin/env bash
set -e

# Install system dependencies (Render provides sudo in build scripts)
echo "Installing espeak-ng and ffmpeg..."
apt-get update -qq
apt-get install -y -qq espeak-ng ffmpeg libespeak-ng1

# Verify installations
echo "Verifying installations..."
which espeak-ng || echo "⚠️  espeak-ng not found"
which ffmpeg || echo "⚠️  ffmpeg not found"

# Install Python dependencies
echo "Installing Python packages..."
pip install --no-cache-dir -r requirements.txt

echo "✅ Build complete!"
