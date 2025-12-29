# 🎤 Princeps Ko-TTS Python Bridge

**Python 3.12+에서 고품질 한국어 TTS를 사용하세요**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.12+-green.svg)](https://python.org)

> 🌉 **Bridge the Gap** - 기존의 최고 품질 한국어 TTS 엔진들은 Python 3.10/3.11만 지원합니다.
> 이 프로젝트는 Docker를 통해 Python 3.12+ 앱에서 이 엔진들을 사용할 수 있게 해줍니다.

---

## 🚨 문제

| TTS 엔진 | 한국어 품질 | Python 지원 |
|----------|------------|-------------|
| CosyVoice | ⭐⭐⭐⭐⭐ | **3.10 only** |
| MeloTTS | ⭐⭐⭐⭐ | 3.9-3.11 |
| Coqui XTTS | ⭐⭐⭐⭐⭐ | **< 3.12** |

**2025년 현재, Python 3.12+에서 고품질 한국어 TTS = 불가능** 😢

---

## ✅ 해결책

```
┌─────────────────────────────────────────────────────┐
│  Your Python 3.12+ App                              │
│                                                     │
│  from ko_tts import speak_sync                      │
│  audio = speak_sync("안녕하세요!")                    │
└───────────────────────┬─────────────────────────────┘
                        │ HTTP REST API
                        ▼
┌─────────────────────────────────────────────────────┐
│  Docker Container (Python 3.10)        Port: 9999   │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  MeloTTS    │  │  Edge TTS   │  │  Your Own   │  │
│  │  (Local)    │  │  (Online)   │  │  Engine     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
│                                                     │
│           🔌 플러그인 시스템 (자동 감지)               │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 두 가지 방법

### Option A: DIY (무료)

직접 설치하고 운영하세요:

```bash
git clone https://github.com/LCO-L/princeps_ko_tts_py_bridge
cd princeps_ko_tts_py_bridge/docker
docker-compose up -d
```

### Option B: Hosted Service (준비 중)

호스팅 서비스를 이용하면 Docker 없이 바로 사용 가능:

```python
from ko_tts import KoreanTTS

tts = KoreanTTS(api_url="https://your-hosted-service.com/tts")
audio = await tts.speak("안녕하세요!")
```

**→ 문의: GitHub Issues**

---

## 🚀 Quick Start

### 1. Docker 서비스 시작

```bash
cd docker
docker-compose up -d
```

### 2. Python에서 사용

```python
from maeum_services.ko_tts import speak_sync

# 간단 사용
audio = speak_sync("안녕하세요!")
audio.save("hello.wav")
audio.play()

# 비동기 사용
from maeum_services.ko_tts import KoreanTTS

async with KoreanTTS() as tts:
    audio = await tts.speak("반갑습니다!", voice="KR", speed=1.2)
    print(f"Duration: {audio.duration}s")
```

### 3. cURL로 테스트

```bash
curl -X POST http://localhost:9999/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "안녕하세요!"}' \
  --output hello.wav
```

---

## 📡 API Endpoints

| Method | Path | 설명 |
|--------|------|------|
| POST | `/tts` | 음성 합성 (WAV 반환) |
| POST | `/tts/json` | 음성 합성 (Base64 JSON) |
| GET | `/engines` | 사용 가능한 엔진 목록 |
| GET | `/voices` | 사용 가능한 음성 목록 |
| GET | `/health` | 헬스 체크 |
| GET | `/about` | 프로젝트 정보 |

---

## 🔌 플러그인 시스템

### 내장 엔진

| 엔진 | 타입 | 우선순위 | 설명 |
|------|------|----------|------|
| **MeloTTS** | 로컬 | 80 | 고품질 로컬 TTS (권장) |
| **Edge TTS** | 온라인 | 20 | Microsoft Edge (fallback) |

### 나만의 엔진 추가

`engines/` 디렉토리에 새 파일을 추가하면 자동으로 감지됩니다:

```python
# engines/my_engine.py
from .base import TTSEngineBase, VoiceInfo, SynthesisResult

class MyCustomEngine(TTSEngineBase):
    name = "my_engine"
    display_name = "My Custom Engine"
    priority = 100  # 높을수록 우선

    def synthesize(self, text, voice, speed) -> SynthesisResult:
        # 구현
        ...
```

---

## 🎙️ 사용 가능한 음성

### MeloTTS
- `KR` - 한국어 기본
- `KR-1` - 한국어 음성 1
- `KR-2` - 한국어 음성 2

### Edge TTS (온라인)
- `ko-KR-SunHiNeural` - 선희 (여성)
- `ko-KR-InJoonNeural` - 인준 (남성)
- `ko-KR-HyunsuNeural` - 현수 (남성)
- `ko-KR-YuJinNeural` - 유진 (여성)

---

## 📁 프로젝트 구조

```
ko_tts/
├── engines/                    # 🔌 플러그인 엔진들
│   ├── __init__.py            # 엔진 exports
│   ├── base.py                # TTSEngineBase 인터페이스
│   ├── registry.py            # 엔진 자동 감지 & 관리
│   ├── melo.py                # MeloTTS 플러그인
│   └── edge.py                # Edge TTS 플러그인
├── server/
│   └── tts_api.py             # FastAPI REST API
├── client/
│   └── ko_tts_client.py       # Python 3.12+ 클라이언트
├── docker/
│   ├── Dockerfile             # Python 3.10 컨테이너
│   ├── docker-compose.yml     # 서비스 구성
│   └── requirements.txt       # 의존성
└── README_tts.md
```

---

## 🤝 Contributing

PR 환영합니다! 새로운 TTS 엔진을 추가하려면:

1. `engines/` 디렉토리에 새 파일 생성
2. `TTSEngineBase` 인터페이스 구현
3. PR 제출

---

## 📄 License

**Apache 2.0** - 자유롭게 사용, 수정, 배포하세요!

이 프로젝트는 **래퍼(wrapper)만 오픈소스**입니다.
TTS 엔진들은 각자의 라이선스를 따릅니다.

---

## 📧 Contact

- **GitHub**: https://github.com/LCO-L/princeps_ko_tts_py_bridge
- **Issues**: https://github.com/LCO-L/princeps_ko_tts_py_bridge/issues

---

<p align="center">
  <b>🌉 Bridge the Python Version Gap for Korean TTS</b><br>
  Made by Princeps
</p>

