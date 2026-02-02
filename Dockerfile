# Cloud-optimized deployment for Railway, Render, Fly.io
FROM python:3.11-slim

# Install system dependencies for Manim and multimedia processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    texlive \
    texlive-latex-extra \
    texlive-fonts-extra \
    texlive-latex-recommended \
    texlive-science \
    tipa \
    libcairo2-dev \
    libpango1.0-dev \
    libpq-dev \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p media/videos media/images media/texts voice_cache web_jobs

# Expose port for FastAPI
EXPOSE 8000

# Set environment variables for cloud deployment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MANIM_QUALITY=${MANIM_QUALITY:-low}
ENV JOB_TIMEOUT=${JOB_TIMEOUT:-600}
ENV HOST=0.0.0.0
ENV PORT=8000

# Run the FastAPI server with gunicorn for production
CMD ["uvicorn", "scripts.server.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
