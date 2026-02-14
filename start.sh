#!/bin/bash

# Manimations Cloud Startup Script
# This script is used by cloud platforms to start the application

echo "🚀 Starting Manimations API..."

# Create necessary directories
mkdir -p media/videos media/images media/texts voice_cache web_jobs

# Set default environment variables if not provided
export MANIM_QUALITY=${MANIM_QUALITY:-low}
export JOB_TIMEOUT=${JOB_TIMEOUT:-600}
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}

echo "📊 Configuration:"
echo "  - Quality: $MANIM_QUALITY"
echo "  - Timeout: $JOB_TIMEOUT seconds"
echo "  - Storage: ${STORAGE_BACKEND:-local}"

# Check if LLM keys are configured
if [ -z "$OPENAI_API_KEY" ] && [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  WARNING: No LLM API keys configured!"
    echo "   Set OPENAI_API_KEY or GEMINI_API_KEY environment variable"
fi

# Start the server
echo "🌐 Starting server on $HOST:$PORT..."
exec python -m uvicorn scripts.server.app:app \
    --host "$HOST" \
    --port "$PORT" \
    --workers 1
