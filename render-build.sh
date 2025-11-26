#!/usr/bin/env bash
# Install system dependencies
apt-get update
apt-get install -y espeak-ng ffmpeg

# Install Python dependencies
pip install -r requirements.txt
