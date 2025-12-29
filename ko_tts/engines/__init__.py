"""
Ko-TTS Engine Plugins / 한국어 TTS 엔진 플러그인
================================================

Open Source Plugin System (Apache 2.0)
오픈소스 플러그인 시스템

Built-in Engines / 내장 엔진:
- MeloTTS (melo) - High-quality, lightweight / 고품질, 경량
- Edge TTS (edge) - Online fallback / 온라인 폴백

Add Your Own Engine / 나만의 엔진 추가:
    1. Create a new file in engines/ (e.g., my_engine.py)
       engines/에 새 파일 생성 (예: my_engine.py)
    2. Implement TTSEngineBase interface
       TTSEngineBase 인터페이스 구현
    3. Engine auto-discovered on startup
       시작 시 엔진 자동 감지

Example / 예시:
    from maeum_services.ko_tts.engines import get_registry, synthesize

    # Quick synthesis / 빠른 합성
    result = synthesize("안녕하세요!")

    # Custom engine / 커스텀 엔진
    registry = get_registry()
    registry.set_active_engine("melo")
    result = registry.synthesize("반갑습니다!")

License: Apache 2.0
"""

from .base import (
    TTSEngineBase,
    VoiceInfo,
    SynthesisResult,
    EngineStatus
)

from .registry import (
    EngineRegistry,
    get_registry,
    synthesize
)

# Import built-in engines (for auto-discovery)
# 내장 엔진 임포트 (자동 감지용)
from . import melo
from . import edge

__all__ = [
    # Base / 기본
    "TTSEngineBase",
    "VoiceInfo",
    "SynthesisResult",
    "EngineStatus",

    # Registry / 레지스트리
    "EngineRegistry",
    "get_registry",
    "synthesize",
]
