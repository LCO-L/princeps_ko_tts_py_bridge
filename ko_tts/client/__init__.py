"""
Korean TTS Client / 한국어 TTS 클라이언트
=========================================
Python 3.12+ compatible client
Python 3.12+ 호환 클라이언트

Usage / 사용법:
    from maeum_services.ko_tts.client import KoreanTTS, speak_sync

    # Quick usage / 간단 사용
    audio = speak_sync("안녕하세요!")
    audio.save("hello.wav")

    # Full client / 전체 클라이언트
    async with KoreanTTS() as tts:
        audio = await tts.speak("반갑습니다!")

License: Apache 2.0
"""

from .ko_tts_client import (
    KoreanTTS,
    TTSAudio,
    RateLimitError,
    ProTierRequired,
    speak,
    speak_sync,
    get_client
)

__all__ = [
    "KoreanTTS",
    "TTSAudio",
    "RateLimitError",
    "ProTierRequired",
    "speak",
    "speak_sync",
    "get_client"
]
