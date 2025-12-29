"""
Ko-TTS Engine Interface / 한국어 TTS 엔진 인터페이스
====================================================
Abstract base class for TTS engine plugins
TTS 엔진 플러그인을 위한 추상 기본 클래스

Open Source (Apache 2.0)
Anyone can implement this interface to add new TTS engines.
누구나 이 인터페이스를 구현하여 새로운 TTS 엔진을 추가할 수 있습니다.

Example / 예시:
    class MyTTSEngine(TTSEngineBase):
        name = "my_tts"

        def synthesize(self, text, voice, speed):
            # Your implementation / 구현
            return SynthesisResult(...)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum


class EngineStatus(Enum):
    """Engine availability status / 엔진 가용성 상태"""
    AVAILABLE = "available"
    NOT_INSTALLED = "not_installed"
    ERROR = "error"


@dataclass
class VoiceInfo:
    """Voice information / 음성 정보"""
    id: str
    name: str
    language: str = "ko"
    gender: str = "unknown"
    description: str = ""


@dataclass
class SynthesisResult:
    """TTS synthesis result / TTS 합성 결과"""
    audio_bytes: bytes
    sample_rate: int
    duration: float
    voice: str
    cached: bool = False


class TTSEngineBase(ABC):
    """
    Abstract base class for TTS engines
    TTS 엔진을 위한 추상 기본 클래스

    Implement this interface to add support for new TTS backends.
    새로운 TTS 백엔드를 추가하려면 이 인터페이스를 구현하세요.

    Required / 필수:
        - name: Engine identifier / 엔진 식별자
        - synthesize(): Core synthesis method / 핵심 합성 메서드
        - get_voices(): List available voices / 사용 가능한 음성 목록
        - check_available(): Check if engine is installed / 엔진 설치 여부 확인

    Optional / 선택:
        - initialize(): Setup/load models / 모델 설정/로드
        - cleanup(): Release resources / 리소스 해제
    """

    # Engine identifier (override in subclass)
    # 엔진 식별자 (서브클래스에서 오버라이드)
    name: str = "base"
    display_name: str = "Base Engine"
    version: str = "1.0.0"

    # Supported languages / 지원 언어
    languages: List[str] = ["ko"]

    # Priority (higher = preferred) / 우선순위 (높을수록 우선)
    priority: int = 0

    def __init__(self):
        self._initialized = False
        self._status = EngineStatus.NOT_INSTALLED

    @abstractmethod
    def check_available(self) -> Tuple[bool, str]:
        """
        Check if this engine is available
        이 엔진이 사용 가능한지 확인

        Returns:
            (is_available, message) / (사용 가능 여부, 메시지)
        """
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the engine (load models, etc.)
        엔진 초기화 (모델 로드 등)

        Returns:
            True if successful / 성공 시 True
        """
        pass

    @abstractmethod
    def synthesize(
        self,
        text: str,
        voice: str = "default",
        speed: float = 1.0
    ) -> SynthesisResult:
        """
        Synthesize speech from text
        텍스트로부터 음성 합성

        Args:
            text: Text to synthesize (Korean) / 합성할 텍스트 (한국어)
            voice: Voice ID / 음성 ID
            speed: Speech speed (0.5 - 2.0) / 음성 속도

        Returns:
            SynthesisResult with audio bytes / 오디오 바이트가 포함된 SynthesisResult
        """
        pass

    @abstractmethod
    def get_voices(self) -> List[VoiceInfo]:
        """
        Get list of available voices
        사용 가능한 음성 목록 조회

        Returns:
            List of VoiceInfo / VoiceInfo 목록
        """
        pass

    def cleanup(self):
        """Release resources (optional override) / 리소스 해제 (선택적 오버라이드)"""
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get engine information / 엔진 정보 조회"""
        available, msg = self.check_available()
        return {
            "name": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "languages": self.languages,
            "priority": self.priority,
            "available": available,
            "status_message": msg,
            "initialized": self._initialized
        }

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name} available={self._status.value}>"
