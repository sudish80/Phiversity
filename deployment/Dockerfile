# Optimized lightweight build for Railway free tier
# Updated: 2026-02-07 06:08 UTC - Force rebuild with Python 3.12 + espeak-ng
FROM python:3.12-slim

# Cache-busting arg (change value to force rebuild from this point)
ARG CACHE_BUST=2026-02-07-06:21
RUN echo "Cache bust: $CACHE_BUST"

# Install only essential dependencies (minimize size)
# Cache-bust: 2026-02-07-06:20
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    libcairo2-dev \
    libpango1.0-dev \
    libpq-dev \
    build-essential \
    curl \
    espeak-ng \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set working directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies with minimal cache
# Force reinstall to avoid Docker layer caching issues
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --force-reinstall google-generativeai>=0.8.0 && \
    pip install --no-cache-dir -r requirements.txt && \
    pip list && \
    find /usr/local -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p media/videos media/images media/texts voice_cache web_jobs

# Remove unnecessary files to save space
RUN find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true && \
    find . -type d -name .git -exec rm -rf {} + 2>/dev/null || true && \
    rm -rf ./test ./fine\ tuned ./media/Tex/* ./media/images/* 2>/dev/null || true && \
    rm -rf ./*.md ./Prompt* ./HISTORY* ./FIX* ./IMPLEMENTATION* ./PERFORMANCE* ./GENERATION* ./GETTING* ./QUICK* ./README* ./RUN* 2>/dev/null || true

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONOPTIMIZE=2
ENV MANIM_QUALITY=low
ENV JOB_TIMEOUT=600
ENV HOST=0.0.0.0
ENV PORT=8000

# Start server - Railway will provide PORT env var
CMD uvicorn scripts.server.app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
