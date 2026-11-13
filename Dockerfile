# Phiversity cloud backend: FastAPI + Manim + edge-tts + ffmpeg.
# Render "Runtime: Docker" builds this file (render.yaml points here).
#
# LaTeX is included because the bundled demo lectures and the LLM's
# Manim code use MathTex. Without it the pipeline would still work for
# LLM lectures (detect_latex() turns LaTeX off) but demos would fail.

FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MANIM_DISABLE_WINDOW=1

# System deps: ffmpeg (compose), pango/cairo (Manim rendering), fonts,
# and a compact LaTeX for MathTex.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libcairo2 \
        libglib2.0-0 \
        fonts-liberation \
        fonts-dejavu-core \
        texlive-latex-base \
        texlive-fonts-recommended \
        texlive-latex-recommended \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY phiversity /app/phiversity

RUN pip install --no-cache-dir /app/phiversity \
    && pip install --no-cache-dir \
        "fastapi>=0.109" \
        "uvicorn[standard]>=0.27" \
        "edge-tts>=6.1" \
        "manim==0.18.0"

# The web service renders inline (single free service). Set to 0 and run
# phiversity-worker separately if you split the load.
ENV PHIVERSITY_INLINE_WORKER=1

EXPOSE 8000

# Render injects $PORT; default 8000 keeps local Docker runs simple.
CMD ["sh", "-c", "uvicorn phiversity.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
