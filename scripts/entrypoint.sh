#!/bin/bash

# KisaanAI Multi-Process Entrypoint
# This script launches all 3 backend services and Nginx

echo "🚀 Starting KisaanAI Backend Suite..."

# 1. Start Image Model API in background
echo "Starting Image Model API on port 8001..."
cd /app/Image_model
uvicorn plant_model_service:app --host 0.0.0.0 --port 8001 &

# 2. Start Rasa Action Server in background
echo "Starting Rasa Action Server on port 5055..."
cd /app
rasa run actions --port 5055 &

# 3. Start Rasa Server in background
echo "Starting Rasa Server on port 5005..."
rasa run --enable-api --cors "*" --port 5005 &

# 4. Start Nginx in foreground to keep container alive
echo "Starting Nginx Gateway on port ${PORT:-7860}..."
nginx -g "daemon off;"
