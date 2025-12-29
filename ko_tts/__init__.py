"""
Korean TTS / 한국어 TTS
=======================
High-quality Korean TTS - Python 3.12+ compatible
고품질 한국어 TTS - Python 3.12+ 호환

Architecture / 아키텍처:
    Docker (Python 3.10) ← REST API → Client (Python 3.12+)

Components / 구성요소:
- engines/: TTS engine plugins / TTS 엔진 플러그인
- server/: Docker TTS server (Python 3.10) / Docker TTS 서버
- client/: Python 3.12+ client library / 클라이언트 라이브러리
- docker/: Dockerfile, docker-compose.yml

Quick Start / 빠른 시작:
    # 1. Start Docker service / Docker 서비스 시작
    cd docker && docker-compose up -d

    # 2. Use in Python / Python에서 사용
    from maeum_services.ko_tts import speak_sync

    audio = speak_sync("안녕하세요!")
    audio.save("hello.wav")

License: Apache 2.0
"""

# Client exports (Python 3.12+ compatible)
from .client import (
    KoreanTTS,
    TTSAudio,
    speak,
    speak_sync,
    get_client
)

__version__ = "1.0.0"
__all__ = [
    "KoreanTTS",
    "TTSAudio",
    "speak",
    "speak_sync",
    "get_client"
]
