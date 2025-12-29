"""
Korean TTS Client / 한국어 TTS 클라이언트
=========================================
Python 3.12+ compatible client for Korean TTS API
Python 3.12+ 호환 한국어 TTS API 클라이언트

Works with any Python version - connects to Docker TTS service
모든 Python 버전에서 작동 - Docker TTS 서비스에 연결

Usage / 사용법:
    from ko_tts_client import KoreanTTS

    tts = KoreanTTS()
    audio = await tts.speak("안녕하세요!")
    audio.save("output.wav")

License: Apache 2.0
"""

import os
import asyncio
import httpx
from pathlib import Path
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass


@dataclass
class TTSAudio:
    """TTS synthesis result / TTS 합성 결과"""
    audio_bytes: bytes
    duration: float
    sample_rate: int
    text: str
    voice: str
    engine: str
    processing_time_ms: float

    def save(self, path: Union[str, Path]) -> Path:
        """Save audio to file / 파일로 저장"""
        path = Path(path)
        path.write_bytes(self.audio_bytes)
        return path

    def play(self):
        """Play audio (requires sounddevice) / 오디오 재생 (sounddevice 필요)"""
        try:
            import sounddevice as sd
            import soundfile as sf
            import io

            data, sr = sf.read(io.BytesIO(self.audio_bytes))
            sd.play(data, sr)
            sd.wait()
        except ImportError:
            raise RuntimeError("Install sounddevice: pip install sounddevice soundfile")


class KoreanTTS:
    """
    Korean TTS Client / 한국어 TTS 클라이언트

    Connects to Docker-based TTS service (Python 3.10)
    Docker 기반 TTS 서비스에 연결 (Python 3.10)

    Works with Python 3.12+
    Python 3.12+에서 작동

    Example / 예시:
        tts = KoreanTTS()

        # Async usage / 비동기 사용
        audio = await tts.speak("안녕하세요!")
        audio.save("hello.wav")

        # Sync usage / 동기 사용
        audio = tts.speak_sync("반갑습니다!")
        audio.play()
    """

    DEFAULT_URL = "http://localhost:9999"

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        Initialize Korean TTS client / 한국어 TTS 클라이언트 초기화

        Args:
            base_url: TTS API URL (default: http://localhost:9999)
                     TTS API 주소 (기본값: http://localhost:9999)
            timeout: Request timeout in seconds / 요청 타임아웃 (초)
        """
        self.base_url = base_url or os.environ.get("KO_TTS_URL", self.DEFAULT_URL)
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        """Build request headers / 요청 헤더 생성"""
        return {"Content-Type": "application/json"}

    async def speak(
        self,
        text: str,
        voice: str = "KR",
        speed: float = 1.0
    ) -> TTSAudio:
        """
        Synthesize Korean speech (async) / 한국어 음성 합성 (비동기)

        Args:
            text: Korean text to synthesize / 합성할 한국어 텍스트
            voice: Voice ID (KR, KR-1, KR-2, etc.) / 음성 ID
            speed: Speech speed (0.5 - 2.0) / 음성 속도

        Returns:
            TTSAudio object with audio bytes / 오디오 바이트가 포함된 TTSAudio 객체
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/tts",
                json={"text": text, "voice": voice, "speed": speed},
                headers=self._headers()
            )

            response.raise_for_status()

            return TTSAudio(
                audio_bytes=response.content,
                duration=float(response.headers.get("X-TTS-Duration", 0)),
                sample_rate=24000,
                text=text,
                voice=voice,
                engine=response.headers.get("X-TTS-Engine", "unknown"),
                processing_time_ms=float(response.headers.get("X-TTS-Processing-Time-Ms", 0))
            )

    def speak_sync(
        self,
        text: str,
        voice: str = "KR",
        speed: float = 1.0
    ) -> TTSAudio:
        """
        Synthesize Korean speech (sync) / 한국어 음성 합성 (동기)

        Same as speak() but synchronous
        speak()와 동일하지만 동기 방식
        """
        return asyncio.run(self.speak(text, voice, speed))

    async def get_voices(self) -> Dict[str, Any]:
        """Get available voices / 사용 가능한 음성 목록 조회"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/voices",
                headers=self._headers()
            )
            response.raise_for_status()
            return response.json()

    async def get_engines(self) -> Dict[str, Any]:
        """Get available engines / 사용 가능한 엔진 목록 조회"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/engines",
                headers=self._headers()
            )
            response.raise_for_status()
            return response.json()

    async def health_check(self) -> bool:
        """Check if TTS service is available / TTS 서비스 사용 가능 여부 확인"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False


# ═══════════════════════════════════════════════════════════════════════════════
#                    CONVENIENCE FUNCTIONS / 편의 함수
# ═══════════════════════════════════════════════════════════════════════════════

_default_client: Optional[KoreanTTS] = None


def get_client() -> KoreanTTS:
    """Get default TTS client / 기본 TTS 클라이언트 가져오기"""
    global _default_client
    if _default_client is None:
        _default_client = KoreanTTS()
    return _default_client


async def speak(text: str, voice: str = "KR", speed: float = 1.0) -> TTSAudio:
    """
    Quick TTS synthesis / 빠른 TTS 합성

    Example / 예시:
        audio = await speak("안녕하세요!")
        audio.save("hello.wav")
    """
    return await get_client().speak(text, voice, speed)


def speak_sync(text: str, voice: str = "KR", speed: float = 1.0) -> TTSAudio:
    """
    Quick TTS synthesis (sync) / 빠른 TTS 합성 (동기)

    Example / 예시:
        audio = speak_sync("안녕하세요!")
        audio.play()
    """
    return get_client().speak_sync(text, voice, speed)


# ═══════════════════════════════════════════════════════════════════════════════
#                    CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage / 사용법: python ko_tts_client.py '안녕하세요!' [output.wav]")
        sys.exit(1)

    text = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "output.wav"

    print(f"Synthesizing / 합성 중: {text}")
    audio = speak_sync(text)
    audio.save(output)
    print(f"Saved to / 저장됨: {output} ({audio.duration:.2f}s)")
