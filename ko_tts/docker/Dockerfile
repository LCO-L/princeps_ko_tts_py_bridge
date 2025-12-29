# ═══════════════════════════════════════════════════════════════════════════════
#  Korean TTS Docker Container / 한국어 TTS Docker 컨테이너
#  ═══════════════════════════════════════════════════════════════════════════════
#
#  Python 3.10 container with MeloTTS + Edge TTS
#  Python 3.10 컨테이너 - MeloTTS + Edge TTS 지원
#
#  Build / 빌드:  docker build -t ko-tts .
#  Run / 실행:    docker run -p 9999:9999 ko-tts
#
#  License: Apache 2.0
# ═══════════════════════════════════════════════════════════════════════════════

FROM python:3.10-slim

LABEL description="Korean TTS Service / 한국어 TTS 서비스"
LABEL version="1.0.0"
LABEL license="Apache-2.0"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    curl \
    ffmpeg \
    libsndfile1 \
    mecab \
    libmecab-dev \
    mecab-ipadic-utf8 \
    && rm -rf /var/lib/apt/lists/*

# Korean MeCab dictionary
RUN apt-get update && apt-get install -y --no-install-recommends \
    mecab-ko \
    mecab-ko-dic \
    || echo "Korean MeCab not in apt, will install via pip"

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server/ ./server/

# Model cache directory
ENV HF_HOME=/app/models
ENV TRANSFORMERS_CACHE=/app/models
RUN mkdir -p /app/models /app/audio_cache

# Port
EXPOSE 9999

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:9999/health || exit 1

# Run server
CMD ["python", "-m", "uvicorn", "server.tts_api:app", "--host", "0.0.0.0", "--port", "9999"]
