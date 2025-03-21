#!/bin/bash

# Update package list
apt-get update

# Install system dependencies for PyAudio
apt-get install -y portaudio19-dev python3-pyaudio python3-dev build-essential

# Install Python dependencies
pip install --no-cache-dir -r requirements.txt
