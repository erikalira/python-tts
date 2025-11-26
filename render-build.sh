#!/usr/bin/env bash
set -e

echo "Installing system dependencies..."
apt-get update
apt-get install -y espeak-ng

echo "Installing Python packages..."
pip install --no-cache-dir -r requirements.txt

echo "✅ Build complete!"
