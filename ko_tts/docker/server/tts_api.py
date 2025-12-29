"""
Korean TTS API / 한국어 TTS API
================================
Open Source REST API for Korean Text-to-Speech
한국어 텍스트-음성 변환 오픈소스 REST API

This is the WRAPPER - Open Source (Apache 2.0)
이것은 래퍼입니다 - 오픈소스 (Apache 2.0)

TTS engines are pluggable - bring your own or use ours
TTS 엔진은 플러그인 방식 - 직접 설치하거나 호스팅 서비스 사용

Endpoints / 엔드포인트:
- POST /tts          - Synthesize speech / 음성 합성
- GET  /engines      - List available engines / 사용 가능한 엔진 목록
- GET  /voices       - List available voices / 사용 가능한 음성 목록
- GET  /health       - Health check / 헬스 체크

Port: 9999
"""

import os
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Response, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import engine registry / 엔진 레지스트리 임포트
import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

try:
    from engines import get_registry, SynthesisResult
except ImportError:
    from maeum_services.ko_tts.engines import get_registry, SynthesisResult


# ═══════════════════════════════════════════════════════════════════════════════
#                    APP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Korean TTS / 한국어 TTS",
    description="""
    🎤 High-quality Korean TTS API / 고품질 한국어 TTS API

    **Open Source Wrapper** (Apache 2.0)
    - Free to use / 무료 사용 가능
    - Pluggable TTS engines / 플러그인 방식 TTS 엔진
    - DIY or hosted service / DIY 또는 호스팅 서비스
    """,
    version="1.0.0",
    license_info={"name": "Apache 2.0", "url": "https://opensource.org/licenses/Apache-2.0"}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
#                    MODELS / 모델
# ═══════════════════════════════════════════════════════════════════════════════

class TTSRequest(BaseModel):
    """TTS synthesis request / TTS 합성 요청"""
    text: str = Field(..., min_length=1, max_length=5000, description="Korean text / 한국어 텍스트")
    voice: str = Field(default="KR", description="Voice ID / 음성 ID")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speed / 속도")
    engine: Optional[str] = Field(default=None, description="Engine (auto if not specified) / 엔진 (미지정 시 자동)")


# ═══════════════════════════════════════════════════════════════════════════════
#                    ENDPOINTS / 엔드포인트
# ═══════════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    """Initialize on startup / 시작 시 초기화"""
    print("[Ko-TTS] Starting up... / 시작 중...")
    registry = get_registry()
    status = registry.get_status()
    print(f"[Ko-TTS] Engines / 엔진: {status['available_engines']}/{status['total_engines']} available")

    if status['available_engines'] == 0:
        print("[Ko-TTS] No engines available! Install one / 엔진 없음! 설치 필요:")
        print("  pip install melotts     # MeloTTS (recommended / 권장)")
        print("  pip install edge-tts    # Edge TTS (online / 온라인)")


@app.get("/")
async def root():
    """API info / API 정보"""
    return {
        "name": "Korean TTS / 한국어 TTS",
        "version": "1.0.0",
        "license": "Apache 2.0 (Open Source)",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check / 헬스 체크"""
    registry = get_registry()
    status = registry.get_status()

    return {
        "status": "healthy" if status["available_engines"] > 0 else "degraded",
        "available_engines": status["available_engines"],
        "active_engine": status["active_engine"],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/engines")
async def list_engines():
    """List all engines and their status / 모든 엔진 및 상태 목록"""
    registry = get_registry()
    return registry.get_status()


@app.get("/voices")
async def list_voices():
    """List available voices from all engines / 모든 엔진의 사용 가능한 음성 목록"""
    registry = get_registry()
    return {
        "voices": registry.get_all_voices(),
        "default": "KR"
    }


@app.post("/tts")
async def synthesize(request: TTSRequest):
    """
    Synthesize Korean speech from text
    텍스트에서 한국어 음성 합성

    Returns WAV audio file / WAV 오디오 파일 반환

    Example / 예시:
        curl -X POST http://localhost:9999/tts \\
          -H "Content-Type: application/json" \\
          -d '{"text": "안녕하세요!"}' \\
          --output hello.wav
    """
    start = time.time()

    try:
        registry = get_registry()
        result = registry.synthesize(
            text=request.text,
            voice=request.voice,
            speed=request.speed,
            engine=request.engine
        )

        processing_time = (time.time() - start) * 1000

        return Response(
            content=result.audio_bytes,
            media_type="audio/wav",
            headers={
                "X-TTS-Duration": str(result.duration),
                "X-TTS-Voice": result.voice,
                "X-TTS-Engine": registry.get_active_engine().name,
                "X-TTS-Processing-Time-Ms": str(processing_time),
                "Content-Disposition": f'attachment; filename="tts_{int(time.time())}.wav"'
            }
        )

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tts/json")
async def synthesize_json(request: TTSRequest):
    """
    Synthesize and return metadata + base64 audio
    합성 후 메타데이터 + base64 오디오 반환

    For clients that prefer JSON response
    JSON 응답을 선호하는 클라이언트용
    """
    import base64
    start = time.time()

    try:
        registry = get_registry()
        result = registry.synthesize(
            text=request.text,
            voice=request.voice,
            speed=request.speed,
            engine=request.engine
        )

        processing_time = (time.time() - start) * 1000

        return {
            "success": True,
            "audio_base64": base64.b64encode(result.audio_bytes).decode(),
            "sample_rate": result.sample_rate,
            "duration": result.duration,
            "voice": result.voice,
            "engine": registry.get_active_engine().name,
            "processing_time_ms": processing_time
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
#                    OPEN SOURCE INFO / 오픈소스 정보
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/about")
async def about():
    """Open source project info / 오픈소스 프로젝트 정보"""
    return {
        "project": "Korean TTS Wrapper / 한국어 TTS 래퍼",
        "license": "Apache 2.0",
        "description": "Open source wrapper for Korean TTS engines / 한국어 TTS 엔진용 오픈소스 래퍼",
        "architecture": {
            "wrapper": "This API server (open source) / 이 API 서버 (오픈소스)",
            "engines": "Pluggable TTS backends (user's choice) / 플러그인 TTS 백엔드 (사용자 선택)",
            "supported_engines": ["MeloTTS", "Edge TTS", "CosyVoice", "Custom"]
        },
        "usage_options": {
            "diy": "Install engines yourself (free) / 직접 엔진 설치 (무료)",
            "hosted": "Use pre-configured service / 사전 구성된 서비스 사용"
        },
        "contributing": "PRs welcome! Add new engines in engines/ directory / PR 환영! engines/ 디렉토리에 새 엔진 추가"
    }


# ═══════════════════════════════════════════════════════════════════════════════
#                    MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9999)
