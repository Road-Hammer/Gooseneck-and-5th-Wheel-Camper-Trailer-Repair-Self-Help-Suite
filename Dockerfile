# STWL Camper Suite — runs on Hugging Face Spaces (Docker) and any host with Docker.
# Copyright 2026 Susquehanna Timberwolf Lines, LLC

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STWL_HOST=0.0.0.0 \
    STWL_PORT=7860 \
    # HF Spaces expects port 7860
    PORT=7860

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt README.md LICENSE NOTICE COPYRIGHT.md ./
COPY src ./src
COPY content ./content
COPY tests ./tests

RUN pip install --upgrade pip \
    && pip install -e . \
    && mkdir -p /app/data /data \
    && useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app

# Persist user DB on Spaces persistent storage when mounted at /data
ENV STWL_DATA_DIR=/data

USER appuser

# Build FTS index at image build so cold start has guides
RUN stwl-camper index || true

EXPOSE 7860

# HF Spaces sets PORT; default 7860
CMD ["sh", "-c", "stwl-camper index && stwl-camper serve --host 0.0.0.0 --port ${PORT:-7860}"]
