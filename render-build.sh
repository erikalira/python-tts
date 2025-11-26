#!/usr/bin/env bash
set -e

echo "Installing Python packages..."
pip install --no-cache-dir -r requirements.txt

echo "✅ Build complete!"
