"""
Edge TTS Engine Plugin / Edge TTS 엔진 플러그인
===============================================
Microsoft Edge TTS (Online fallback)
Microsoft Edge TTS (온라인 폴백)

Requirements / 요구사항:
    pip install edge-tts

Note: Requires internet connection / 인터넷 연결 필요
License: MIT
"""

import io
import asyncio
from typing import List, Tuple

from .base import TTSEngineBase, VoiceInfo, SynthesisResult, EngineStatus

# Try importing edge-tts / edge-tts 임포트 시도
EDGE_AVAILABLE = False
try:
    import edge_tts
    EDGE_AVAILABLE = True
except ImportError:
    edge_tts = None


class EdgeEngine(TTSEngineBase):
    """
    Edge TTS Engine (Online) / Edge TTS 엔진 (온라인)

    Free, high-quality TTS via Microsoft Edge
    Microsoft Edge를 통한 무료 고품질 TTS

    Requires internet connection
    인터넷 연결 필요

    Use as fallback when local engines unavailable
    로컬 엔진 사용 불가 시 폴백으로 사용
    """

    name = "edge"
    display_name = "Edge TTS (Online)"
    version = "1.0.0"
    languages = ["ko", "en", "ja", "zh", "es", "fr", "de"]
    priority = 20  # Low priority (online fallback) / 낮은 우선순위 (온라인 폴백)

    VOICES = [
        VoiceInfo("ko-KR-SunHiNeural", "선희 (Sun-Hi)", "ko", "female", "밝고 친근한 여성 음성"),
        VoiceInfo("ko-KR-InJoonNeural", "인준 (In-Joon)", "ko", "male", "차분한 남성 음성"),
        VoiceInfo("ko-KR-HyunsuNeural", "현수 (Hyunsu)", "ko", "male", "젊은 남성 음성"),
        VoiceInfo("ko-KR-YuJinNeural", "유진 (Yu-Jin)", "ko", "female", "자연스러운 여성 음성"),
    ]

    # Voice aliases for convenience / 편의를 위한 음성 별칭
    VOICE_ALIASES = {
        "KR": "ko-KR-SunHiNeural",
        "KR-1": "ko-KR-SunHiNeural",
        "KR-2": "ko-KR-InJoonNeural",
        "default": "ko-KR-SunHiNeural",
    }

    def __init__(self):
        super().__init__()

    def check_available(self) -> Tuple[bool, str]:
        """Check if edge-tts is installed / edge-tts 설치 여부 확인"""
        if EDGE_AVAILABLE:
            self._status = EngineStatus.AVAILABLE
            return True, "Edge TTS is installed (requires internet) / 설치됨 (인터넷 필요)"
        else:
            self._status = EngineStatus.NOT_INSTALLED
            return False, "edge-tts not installed. Run: pip install edge-tts / 설치 필요"

    def initialize(self) -> bool:
        """No initialization needed for Edge TTS / Edge TTS는 초기화 불필요"""
        if not EDGE_AVAILABLE:
            return False
        self._initialized = True
        return True

    def synthesize(
        self,
        text: str,
        voice: str = "KR",
        speed: float = 1.0
    ) -> SynthesisResult:
        """Synthesize speech using Edge TTS / Edge TTS로 음성 합성"""
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Edge TTS initialization failed / 초기화 실패")

        # Run async synthesis / 비동기 합성 실행
        return asyncio.run(self._synthesize_async(text, voice, speed))

    async def _synthesize_async(
        self,
        text: str,
        voice: str,
        speed: float
    ) -> SynthesisResult:
        """Async synthesis implementation / 비동기 합성 구현"""
        import time
        start = time.time()

        # Resolve voice alias / 음성 별칭 해석
        edge_voice = self.VOICE_ALIASES.get(voice, voice)

        # Rate adjustment / 속도 조절
        rate = f"+{int((speed-1)*100)}%" if speed >= 1 else f"{int((speed-1)*100)}%"

        # Synthesize / 합성
        communicate = edge_tts.Communicate(text, edge_voice, rate=rate)

        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        mp3_bytes = b"".join(audio_chunks)

        # Convert MP3 to WAV / MP3를 WAV로 변환
        wav_bytes, sample_rate = await self._mp3_to_wav(mp3_bytes)

        # Calculate duration / 길이 계산
        import soundfile as sf
        audio_data, sr = sf.read(io.BytesIO(wav_bytes))
        duration = len(audio_data) / sr

        processing_time = (time.time() - start) * 1000
        print(f"[{self.name}] Synthesized {len(text)} chars in {processing_time:.0f}ms (online) / 합성 완료")

        return SynthesisResult(
            audio_bytes=wav_bytes,
            sample_rate=sample_rate,
            duration=duration,
            voice=edge_voice
        )

    async def _mp3_to_wav(self, mp3_bytes: bytes) -> Tuple[bytes, int]:
        """Convert MP3 to WAV using ffmpeg / ffmpeg로 MP3를 WAV로 변환"""
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", "pipe:0", "-f", "wav", "-ar", "24000", "pipe:1",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        wav_bytes, _ = await process.communicate(mp3_bytes)
        return wav_bytes, 24000

    def get_voices(self) -> List[VoiceInfo]:
        """Get available Edge TTS voices / 사용 가능한 Edge TTS 음성 목록"""
        return self.VOICES

    def cleanup(self):
        """No cleanup needed / 정리 불필요"""
        pass
