"""
MeloTTS Engine Plugin / MeloTTS 엔진 플러그인
=============================================
High-quality Korean TTS using MeloTTS
MeloTTS를 사용한 고품질 한국어 TTS

Requirements / 요구사항:
    pip install melotts

License: MIT
"""

import io
import time
from typing import List, Tuple

from .base import TTSEngineBase, VoiceInfo, SynthesisResult, EngineStatus

# Try importing MeloTTS / MeloTTS 임포트 시도
MELO_AVAILABLE = False
try:
    from melo.api import TTS as MeloTTS
    MELO_AVAILABLE = True
except ImportError:
    MeloTTS = None


class MeloEngine(TTSEngineBase):
    """
    MeloTTS Engine / MeloTTS 엔진

    High-quality, lightweight Korean TTS
    고품질, 경량 한국어 TTS

    Best balance of quality and speed
    품질과 속도의 최적 균형
    """

    name = "melo"
    display_name = "MeloTTS"
    version = "0.1.0"
    languages = ["ko", "en", "zh", "ja"]
    priority = 80  # High priority / 높은 우선순위

    VOICES = [
        VoiceInfo("KR", "Korean Default / 한국어 기본", "ko", "female", "기본 한국어 음성"),
        VoiceInfo("KR-1", "Korean Voice 1 / 한국어 음성 1", "ko", "female", "한국어 음성 1"),
        VoiceInfo("KR-2", "Korean Voice 2 / 한국어 음성 2", "ko", "male", "한국어 음성 2"),
    ]

    def __init__(self):
        super().__init__()
        self._model = None
        self._sample_rate = 44100

    def check_available(self) -> Tuple[bool, str]:
        """Check if MeloTTS is installed / MeloTTS 설치 여부 확인"""
        if MELO_AVAILABLE:
            self._status = EngineStatus.AVAILABLE
            return True, "MeloTTS is installed / MeloTTS 설치됨"
        else:
            self._status = EngineStatus.NOT_INSTALLED
            return False, "MeloTTS not installed. Run: pip install melotts / 설치 필요"

    def initialize(self) -> bool:
        """Initialize MeloTTS model / MeloTTS 모델 초기화"""
        if not MELO_AVAILABLE:
            return False

        try:
            print(f"[{self.name}] Loading MeloTTS model... / 모델 로딩 중...")
            start = time.time()

            self._model = MeloTTS(language='KR', device='auto')
            self._sample_rate = self._model.hps.data.sampling_rate

            elapsed = (time.time() - start) * 1000
            print(f"[{self.name}] Loaded in {elapsed:.0f}ms / 로드 완료")

            self._initialized = True
            return True

        except Exception as e:
            print(f"[{self.name}] Failed to initialize / 초기화 실패: {e}")
            self._status = EngineStatus.ERROR
            return False

    def synthesize(
        self,
        text: str,
        voice: str = "KR",
        speed: float = 1.0
    ) -> SynthesisResult:
        """Synthesize speech using MeloTTS / MeloTTS로 음성 합성"""
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("MeloTTS initialization failed / 초기화 실패")

        start = time.time()

        # Get speaker ID / 스피커 ID 가져오기
        speaker_ids = self._model.hps.data.spk2id
        speaker_id = speaker_ids.get(voice, list(speaker_ids.values())[0])

        # Synthesize / 합성
        import tempfile
        import soundfile as sf

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
            self._model.tts_to_file(text, speaker_id, f.name, speed=speed)
            audio_data, sr = sf.read(f.name)

        # Convert to bytes / 바이트로 변환
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sr, format='WAV')
        audio_bytes = buffer.getvalue()

        duration = len(audio_data) / sr
        processing_time = (time.time() - start) * 1000

        print(f"[{self.name}] Synthesized {len(text)} chars in {processing_time:.0f}ms / 합성 완료")

        return SynthesisResult(
            audio_bytes=audio_bytes,
            sample_rate=sr,
            duration=duration,
            voice=voice
        )

    def get_voices(self) -> List[VoiceInfo]:
        """Get available MeloTTS voices / 사용 가능한 MeloTTS 음성 목록"""
        return self.VOICES

    def cleanup(self):
        """Release model resources / 모델 리소스 해제"""
        self._model = None
        self._initialized = False
