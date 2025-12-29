"""
Korean TTS Server / 한국어 TTS 서버
===================================
REST API server for Korean Text-to-Speech
한국어 텍스트-음성 변환 REST API 서버

License: Apache 2.0
"""
from .tts_api import app
from .tts_engine import get_tts_engine, KoreanTTSEngine

__all__ = ["app", "get_tts_engine", "KoreanTTSEngine"]
