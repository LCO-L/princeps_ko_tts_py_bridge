"""
Korean TTS Engine / 한국어 TTS 엔진
===================================
Multi-backend TTS engine with Korean optimization
한국어 최적화된 멀티 백엔드 TTS 엔진

Backends / 백엔드:
- MeloTTS (default, lightweight) / MeloTTS (기본, 경량)
- CosyVoice (high quality) / CosyVoice (고품질)
- Edge TTS (fallback, online) / Edge TTS (폴백, 온라인)

Python 3.10 required for full compatibility
완전한 호환성을 위해 Python 3.10 필요

License: Apache 2.0
"""

import os
import io
import time
import hashlib
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

# Audio processing / 오디오 처리
import soundfile as sf


class TTSBackend(Enum):
    """Available TTS backends / 사용 가능한 TTS 백엔드"""
    MELO = "melo"           # MeloTTS - lightweight, good Korean / 경량, 좋은 한국어
    COSYVOICE = "cosyvoice" # CosyVoice - best quality / 최고 품질
    EDGE = "edge"           # Edge TTS - online fallback / 온라인 폴백
    AUTO = "auto"           # Auto-select best available / 최우선 자동 선택


@dataclass
class TTSConfig:
    """TTS configuration / TTS 설정"""
    backend: TTSBackend = TTSBackend.AUTO
    voice: str = "KR"
    speed: float = 1.0
    sample_rate: int = 24000
    cache_enabled: bool = True
    cache_dir: str = "/app/audio_cache"


@dataclass
class TTSResult:
    """TTS synthesis result / TTS 합성 결과"""
    audio_bytes: bytes
    sample_rate: int
    duration: float
    text: str
    voice: str
    backend: str
    cached: bool
    processing_time_ms: float


class KoreanTTSEngine:
    """
    Korean TTS Engine with multiple backend support
    멀티 백엔드 지원 한국어 TTS 엔진

    Priority / 우선순위: MeloTTS > CosyVoice > Edge TTS
    """

    # Available voices per backend / 백엔드별 사용 가능한 음성
    VOICES = {
        "melo": {
            "KR": "Korean default / 한국어 기본",
            "KR-1": "Korean voice 1 / 한국어 음성 1",
            "KR-2": "Korean voice 2 / 한국어 음성 2",
        },
        "cosyvoice": {
            "korean_female_1": "Korean Female 1 / 한국어 여성 1",
            "korean_male_1": "Korean Male 1 / 한국어 남성 1",
        },
        "edge": {
            "ko-KR-SunHiNeural": "Sun-Hi (Female) / 선희 (여성)",
            "ko-KR-InJoonNeural": "In-Joon (Male) / 인준 (남성)",
            "ko-KR-HyunsuNeural": "Hyunsu (Male) / 현수 (남성)",
            "ko-KR-YuJinNeural": "Yu-Jin (Female) / 유진 (여성)",
        }
    }

    def __init__(self, config: Optional[TTSConfig] = None):
        self.config = config or TTSConfig()
        self._melo_model = None
        self._cosyvoice_model = None
        self._initialized = False
        self._available_backends: List[str] = []

        # Cache / 캐시
        self._cache: Dict[str, bytes] = {}
        Path(self.config.cache_dir).mkdir(parents=True, exist_ok=True)

    def initialize(self) -> bool:
        """Initialize available backends / 사용 가능한 백엔드 초기화"""
        print("[KoTTS] Initializing backends... / 백엔드 초기화 중...")
        start = time.time()

        # Try MeloTTS / MeloTTS 시도
        try:
            from melo.api import TTS as MeloTTS
            self._melo_model = MeloTTS(language='KR', device='auto')
            self._available_backends.append("melo")
            print("[KoTTS] MeloTTS loaded / 로드됨")
        except Exception as e:
            print(f"[KoTTS] MeloTTS not available / 사용 불가: {e}")

        # Try CosyVoice / CosyVoice 시도
        try:
            from cosyvoice.cli.cosyvoice import CosyVoice
            self._cosyvoice_model = CosyVoice('pretrained_models/CosyVoice-300M')
            self._available_backends.append("cosyvoice")
            print("[KoTTS] CosyVoice loaded / 로드됨")
        except Exception as e:
            print(f"[KoTTS] CosyVoice not available / 사용 불가: {e}")

        # Edge TTS is always available (online) / Edge TTS는 항상 사용 가능 (온라인)
        try:
            import edge_tts
            self._available_backends.append("edge")
            print("[KoTTS] Edge TTS available (online fallback) / 사용 가능 (온라인 폴백)")
        except:
            pass

        elapsed = (time.time() - start) * 1000
        print(f"[KoTTS] Initialized in {elapsed:.0f}ms | Backends / 백엔드: {self._available_backends}")

        self._initialized = len(self._available_backends) > 0
        return self._initialized

    def get_backend(self) -> str:
        """Select best available backend / 최우선 사용 가능 백엔드 선택"""
        if self.config.backend == TTSBackend.AUTO:
            # Priority order / 우선순위 순서
            for backend in ["melo", "cosyvoice", "edge"]:
                if backend in self._available_backends:
                    return backend
            raise RuntimeError("No TTS backend available / TTS 백엔드 없음")

        backend = self.config.backend.value
        if backend not in self._available_backends:
            raise RuntimeError(f"Backend '{backend}' not available / 사용 불가")
        return backend

    def _cache_key(self, text: str, voice: str, speed: float) -> str:
        """Generate cache key / 캐시 키 생성"""
        content = f"{text}|{voice}|{speed}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cached(self, key: str) -> Optional[bytes]:
        """Get from cache / 캐시에서 조회"""
        if not self.config.cache_enabled:
            return None

        # Memory cache / 메모리 캐시
        if key in self._cache:
            return self._cache[key]

        # Disk cache / 디스크 캐시
        cache_path = Path(self.config.cache_dir) / f"{key}.wav"
        if cache_path.exists():
            return cache_path.read_bytes()

        return None

    def _set_cache(self, key: str, audio_bytes: bytes):
        """Save to cache / 캐시에 저장"""
        if not self.config.cache_enabled:
            return

        # Memory cache (limit size) / 메모리 캐시 (크기 제한)
        if len(self._cache) < 1000:
            self._cache[key] = audio_bytes

        # Disk cache / 디스크 캐시
        cache_path = Path(self.config.cache_dir) / f"{key}.wav"
        cache_path.write_bytes(audio_bytes)

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: Optional[float] = None
    ) -> TTSResult:
        """
        Synthesize Korean speech from text
        텍스트에서 한국어 음성 합성

        Args:
            text: Korean text to synthesize / 합성할 한국어 텍스트
            voice: Voice ID (backend-specific) / 음성 ID (백엔드별)
            speed: Speech speed multiplier / 음성 속도 배율

        Returns:
            TTSResult with audio bytes / 오디오 바이트가 포함된 TTSResult
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("TTS initialization failed / TTS 초기화 실패")

        voice = voice or self.config.voice
        speed = speed or self.config.speed

        # Check cache / 캐시 확인
        cache_key = self._cache_key(text, voice, speed)
        cached_audio = self._get_cached(cache_key)

        if cached_audio:
            # Calculate duration from cached audio / 캐시된 오디오에서 길이 계산
            audio_array, sr = sf.read(io.BytesIO(cached_audio))
            duration = len(audio_array) / sr

            return TTSResult(
                audio_bytes=cached_audio,
                sample_rate=sr,
                duration=duration,
                text=text,
                voice=voice,
                backend="cache",
                cached=True,
                processing_time_ms=0.0
            )

        # Synthesize / 합성
        start = time.time()
        backend = self.get_backend()

        if backend == "melo":
            audio_bytes, sample_rate = await self._synthesize_melo(text, voice, speed)
        elif backend == "cosyvoice":
            audio_bytes, sample_rate = await self._synthesize_cosyvoice(text, voice, speed)
        elif backend == "edge":
            audio_bytes, sample_rate = await self._synthesize_edge(text, voice, speed)
        else:
            raise RuntimeError(f"Unknown backend / 알 수 없는 백엔드: {backend}")

        processing_time = (time.time() - start) * 1000

        # Calculate duration / 길이 계산
        audio_array, _ = sf.read(io.BytesIO(audio_bytes))
        duration = len(audio_array) / sample_rate

        # Cache / 캐시
        self._set_cache(cache_key, audio_bytes)

        return TTSResult(
            audio_bytes=audio_bytes,
            sample_rate=sample_rate,
            duration=duration,
            text=text,
            voice=voice,
            backend=backend,
            cached=False,
            processing_time_ms=processing_time
        )

    async def _synthesize_melo(
        self, text: str, voice: str, speed: float
    ) -> Tuple[bytes, int]:
        """Synthesize with MeloTTS / MeloTTS로 합성"""
        # MeloTTS synthesis
        speaker_ids = self._melo_model.hps.data.spk2id
        speaker_id = speaker_ids.get(voice, list(speaker_ids.values())[0])

        # Run in thread pool (MeloTTS is sync) / 스레드 풀에서 실행 (MeloTTS는 동기)
        loop = asyncio.get_event_loop()
        audio_array = await loop.run_in_executor(
            None,
            lambda: self._melo_model.tts_to_file(
                text, speaker_id, None, speed=speed, quiet=True
            )
        )

        # If tts_to_file returns path, read it / 경로 반환 시 읽기
        if isinstance(audio_array, str):
            audio_array, sr = sf.read(audio_array)
        else:
            sr = self._melo_model.hps.data.sampling_rate

        # Convert to bytes / 바이트로 변환
        buffer = io.BytesIO()
        sf.write(buffer, audio_array, sr, format='WAV')
        return buffer.getvalue(), sr

    async def _synthesize_cosyvoice(
        self, text: str, voice: str, speed: float
    ) -> Tuple[bytes, int]:
        """Synthesize with CosyVoice / CosyVoice로 합성"""
        loop = asyncio.get_event_loop()

        # CosyVoice synthesis
        def _synth():
            output = self._cosyvoice_model.inference_sft(text, voice)
            return next(output)['tts_speech'].numpy()

        audio_array = await loop.run_in_executor(None, _synth)
        sr = 22050  # CosyVoice default

        # Apply speed / 속도 적용
        if speed != 1.0:
            import librosa
            audio_array = librosa.effects.time_stretch(audio_array, rate=speed)

        # Convert to bytes / 바이트로 변환
        buffer = io.BytesIO()
        sf.write(buffer, audio_array, sr, format='WAV')
        return buffer.getvalue(), sr

    async def _synthesize_edge(
        self, text: str, voice: str, speed: float
    ) -> Tuple[bytes, int]:
        """Synthesize with Edge TTS (online) / Edge TTS로 합성 (온라인)"""
        import edge_tts

        # Map simple voice names to Edge TTS voices / 간단한 음성 이름을 Edge TTS 음성에 매핑
        voice_map = {
            "KR": "ko-KR-SunHiNeural",
            "KR-1": "ko-KR-SunHiNeural",
            "KR-2": "ko-KR-InJoonNeural",
        }
        edge_voice = voice_map.get(voice, voice)

        # Rate adjustment / 속도 조절
        rate = f"+{int((speed-1)*100)}%" if speed >= 1 else f"{int((speed-1)*100)}%"

        communicate = edge_tts.Communicate(text, edge_voice, rate=rate)

        # Collect audio chunks / 오디오 청크 수집
        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        audio_bytes = b"".join(audio_chunks)

        # Edge TTS returns MP3, convert to WAV / Edge TTS는 MP3 반환, WAV로 변환
        import subprocess
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", "pipe:0", "-f", "wav", "-ar", "24000", "pipe:1",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        wav_bytes, _ = await process.communicate(audio_bytes)

        return wav_bytes, 24000

    def list_voices(self) -> Dict[str, Dict[str, str]]:
        """List available voices per backend / 백엔드별 사용 가능한 음성 목록"""
        result = {}
        for backend in self._available_backends:
            if backend in self.VOICES:
                result[backend] = self.VOICES[backend]
        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics / 엔진 통계 조회"""
        return {
            "initialized": self._initialized,
            "available_backends": self._available_backends,
            "cache_size": len(self._cache),
            "config": {
                "backend": self.config.backend.value,
                "voice": self.config.voice,
                "speed": self.config.speed,
                "sample_rate": self.config.sample_rate,
            }
        }


# Singleton / 싱글톤
_engine: Optional[KoreanTTSEngine] = None


def get_tts_engine() -> KoreanTTSEngine:
    """Get singleton TTS engine / 싱글톤 TTS 엔진 조회"""
    global _engine
    if _engine is None:
        _engine = KoreanTTSEngine()
    return _engine
