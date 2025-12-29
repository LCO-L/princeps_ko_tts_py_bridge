"""
TTS Engine Registry / TTS 엔진 레지스트리
=========================================
Auto-discovers and manages TTS engine plugins
TTS 엔진 플러그인 자동 감지 및 관리

Open Source (Apache 2.0)
"""

import importlib
import pkgutil
from typing import Dict, List, Optional, Type
from pathlib import Path

from .base import TTSEngineBase, SynthesisResult, VoiceInfo


class EngineRegistry:
    """
    TTS Engine Plugin Registry / TTS 엔진 플러그인 레지스트리

    Auto-discovers engines in the engines/ directory
    engines/ 디렉토리에서 엔진 자동 감지

    Manages engine lifecycle and selection
    엔진 라이프사이클 및 선택 관리
    """

    def __init__(self):
        self._engines: Dict[str, TTSEngineBase] = {}
        self._active_engine: Optional[TTSEngineBase] = None

    def discover_engines(self) -> List[str]:
        """
        Auto-discover all engine plugins
        모든 엔진 플러그인 자동 감지

        Scans the engines/ directory for TTSEngineBase subclasses
        engines/ 디렉토리에서 TTSEngineBase 서브클래스 스캔
        """
        discovered = []

        # Import all modules in engines package
        # engines 패키지의 모든 모듈 임포트
        engines_dir = Path(__file__).parent

        for file in engines_dir.glob("*.py"):
            if file.name.startswith("_") or file.name in ["base.py", "registry.py"]:
                continue

            module_name = file.stem
            try:
                module = importlib.import_module(f".{module_name}", package="maeum_services.ko_tts.engines")

                # Find TTSEngineBase subclasses / TTSEngineBase 서브클래스 찾기
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        issubclass(attr, TTSEngineBase) and
                        attr is not TTSEngineBase):

                        engine = attr()
                        self._engines[engine.name] = engine
                        discovered.append(engine.name)
                        print(f"[Registry] Discovered engine / 엔진 발견: {engine.name}")

            except Exception as e:
                print(f"[Registry] Failed to load / 로드 실패 {module_name}: {e}")

        return discovered

    def register_engine(self, engine_class: Type[TTSEngineBase]):
        """Manually register an engine class / 엔진 클래스 수동 등록"""
        engine = engine_class()
        self._engines[engine.name] = engine
        print(f"[Registry] Registered / 등록됨: {engine.name}")

    def get_engine(self, name: str) -> Optional[TTSEngineBase]:
        """Get engine by name / 이름으로 엔진 조회"""
        return self._engines.get(name)

    def get_available_engines(self) -> List[TTSEngineBase]:
        """Get all available (installed) engines / 사용 가능한 (설치된) 모든 엔진 조회"""
        available = []
        for engine in self._engines.values():
            is_available, _ = engine.check_available()
            if is_available:
                available.append(engine)
        return sorted(available, key=lambda e: -e.priority)

    def get_best_engine(self) -> Optional[TTSEngineBase]:
        """Get the best available engine (highest priority) / 최우선 사용 가능 엔진 조회"""
        available = self.get_available_engines()
        return available[0] if available else None

    def set_active_engine(self, name: str) -> bool:
        """Set the active engine by name / 이름으로 활성 엔진 설정"""
        engine = self._engines.get(name)
        if not engine:
            return False

        is_available, msg = engine.check_available()
        if not is_available:
            print(f"[Registry] Engine {name} not available / 사용 불가: {msg}")
            return False

        self._active_engine = engine
        return True

    def get_active_engine(self) -> TTSEngineBase:
        """Get or select active engine / 활성 엔진 조회 또는 선택"""
        if self._active_engine:
            return self._active_engine

        # Auto-select best available / 최우선 엔진 자동 선택
        best = self.get_best_engine()
        if not best:
            raise RuntimeError("No TTS engine available. Install one: pip install melotts / 엔진 없음")

        self._active_engine = best
        return self._active_engine

    def synthesize(
        self,
        text: str,
        voice: str = "KR",
        speed: float = 1.0,
        engine: Optional[str] = None
    ) -> SynthesisResult:
        """
        Synthesize using active or specified engine
        활성 또는 지정된 엔진으로 합성

        Args:
            text: Korean text / 한국어 텍스트
            voice: Voice ID / 음성 ID
            speed: Speech speed / 음성 속도
            engine: Optional engine name (uses active if not specified)
                   선택적 엔진 이름 (미지정 시 활성 엔진 사용)
        """
        if engine:
            eng = self.get_engine(engine)
            if not eng:
                raise ValueError(f"Unknown engine / 알 수 없는 엔진: {engine}")
        else:
            eng = self.get_active_engine()

        # Initialize if needed / 필요 시 초기화
        if not eng._initialized:
            eng.initialize()

        return eng.synthesize(text, voice, speed)

    def get_all_voices(self) -> Dict[str, List[VoiceInfo]]:
        """Get voices from all available engines / 모든 사용 가능 엔진의 음성 조회"""
        voices = {}
        for engine in self.get_available_engines():
            voices[engine.name] = engine.get_voices()
        return voices

    def get_status(self) -> Dict:
        """Get registry status / 레지스트리 상태 조회"""
        engines_info = []
        for engine in self._engines.values():
            info = engine.get_info()
            info["is_active"] = engine == self._active_engine
            engines_info.append(info)

        return {
            "total_engines": len(self._engines),
            "available_engines": len(self.get_available_engines()),
            "active_engine": self._active_engine.name if self._active_engine else None,
            "engines": engines_info
        }

    def cleanup(self):
        """Cleanup all engines / 모든 엔진 정리"""
        for engine in self._engines.values():
            engine.cleanup()
        self._active_engine = None


# Global registry instance / 전역 레지스트리 인스턴스
_registry: Optional[EngineRegistry] = None


def get_registry() -> EngineRegistry:
    """Get or create global registry / 전역 레지스트리 조회 또는 생성"""
    global _registry
    if _registry is None:
        _registry = EngineRegistry()
        _registry.discover_engines()
    return _registry


def synthesize(text: str, voice: str = "KR", speed: float = 1.0) -> SynthesisResult:
    """
    Quick synthesis using best available engine
    최우선 사용 가능 엔진으로 빠른 합성

    Example / 예시:
        result = synthesize("안녕하세요!")
        with open("output.wav", "wb") as f:
            f.write(result.audio_bytes)
    """
    return get_registry().synthesize(text, voice, speed)
