## Runtime Bridge Architecture  
**for fragile native stacks**

This project implements **Runtime Bridge Architecture**,  
a design pattern for using *fragile native stacks* safely in modern applications.

### The problem
Many high-quality engines (TTS, STT, OCR, media processing, AI inference) rely on:

- Native libraries (CUDA, FFmpeg, phonemizer, system-level dependencies)
- Slow-moving ecosystems (PyTorch, ONNX, C++ extensions)
- Strict runtime compatibility (specific Python and OS versions)

Meanwhile, application runtimes (e.g. Python 3.12+) evolve much faster.

Binding both into a single process or environment inevitably leads to:
- Version conflicts
- Broken upgrades
- Non-reproducible deployments
- “Works on my machine” failures

### The idea
**Runtime Bridge Architecture** solves this by drawing a hard boundary:

- **Application Runtime**  
  Remains modern, fast-moving, and developer-friendly.

- **Runtime Capsule**  
  A fully isolated environment that freezes:
  - Python version
  - Native dependencies
  - Engines and models

- **Bridge Interface**  
  A stable, explicit boundary (HTTP / gRPC / UNIX socket) connecting the two.

[ Modern Application Runtime ]
        ↓  Stable Interface
[ Isolated Runtime Capsule ]
(legacy runtime + fragile native stack)

### Core principles
1. Never downgrade the application runtime  
2. Freeze fragile native stacks in isolation  
3. Communicate only through replaceable, observable boundaries  

### Why Docker here?
Docker is used **only as an isolation mechanism**, not as cloud infrastructure.

- Runs locally by default (localhost)
- No accounts, no telemetry, no data exfiltration
- Works in offline and closed-network environments

Docker contains instability instead of externalizing computation.

### Where this pattern applies
Runtime Bridge Architecture extends beyond TTS:

- Speech systems (TTS, STT, diarization)
- Media pipelines (FFmpeg, OpenCV)
- OCR and document processing
- AI inference runtimes (Whisper, diffusion, LLM inference)
- Any workload with heavy native or GPU dependencies

### What this project demonstrates
This repository serves as a **reference implementation** of the pattern,
using Korean TTS as a concrete, real-world example.

It is not merely a wrapper —  
it is an architectural response to a structural problem in modern AI stacks.

(Written by Princeps Lee)

---

**KOR(한국어)**

이 프로젝트는 Runtime Bridge Architecture를 구현합니다.

이는 깨지기 쉬운 네이티브 스택을 현대적인 애플리케이션에서 안전하게 사용하기 위한 아키텍처 패턴입니다.

# **문제 (The Problem)**

고품질 엔진들(TTS, STT, OCR, 미디어 처리, AI 추론)은 대부분 다음에 의존합니다.

- 네이티브 라이브러리
(CUDA, FFmpeg, phonemizer, 시스템 레벨 의존성)
- 느리게 진화하는 생태계
(PyTorch, ONNX, C++ 확장)
- 엄격한 런타임 호환성
(특정 Python 및 OS 버전)

반면, 애플리케이션 런타임은

Python 3.12+처럼 훨씬 빠른 속도로 진화합니다.

이 둘을 하나의 프로세스나 환경에 묶으면, 결국 다음 문제가 발생합니다.

- 버전 충돌
- 업그레이드 실패
- 재현 불가능한 배포
- “내 컴퓨터에서는 되는데요?” 문제

# **아이디어 (The Idea)**

Runtime Bridge Architecture는

이 문제를 명확한 경계를 그어 해결합니다.

- Application Runtime
최신 상태를 유지하며, 빠르게 진화하고 개발자 친화적이어야 합니다.
- Runtime Capsule
다음 요소를 고정한 완전 격리 환경입니다.
    - Python 버전
    - 네이티브 의존성
    - 엔진과 모델
- Bridge Interface
두 영역을 연결하는 명시적이고 안정적인 경계
(HTTP / gRPC / UNIX socket)

[ Modern Application Runtime ]

↓  Stable Interface

[ Isolated Runtime Capsule ]

(legacy runtime + fragile native stack)

# **핵심 원칙 (Core Principles)**

1. 애플리케이션 런타임은 절대 다운그레이드하지 않는다
2. 깨지기 쉬운 네이티브 스택은 격리된 환경에 고정한다
3. 통신은 교체 가능하고 관측 가능한 경계를 통해서만 한다

# **왜 Docker인가? (Why Docker)**

Docker는 클라우드가 아니라 격리를 위한 도구로 사용됩니다.

- 기본 동작은 로컬(localhost)
- 계정 없음, 텔레메트리 없음, 데이터 외부 전송 없음
- 오프라인 및 폐쇄망 환경에서도 동작

Docker는 계산을 외부로 보내는 도구가 아니라,

불안정을 안에 가두는 도구입니다.

# **적용 가능한 영역 (Where This Pattern Applies)**

Runtime Bridge Architecture는 TTS에만 국한되지 않습니다.

- 음성 시스템 (TTS, STT, 화자 분리)
- 미디어 파이프라인 (FFmpeg, OpenCV)
- OCR 및 문서 처리
- AI 추론 런타임 (Whisper, diffusion, LLM inference)
- 네이티브 또는 GPU 의존성이 큰 모든 워크로드

# **이 프로젝트가 보여주는 것 (What This Project Demonstrates)**

이 저장소는 한국어 TTS를 실제 사례로 삼아,

Runtime Bridge Architecture의 레퍼런스 구현을 제공합니다.

이 프로젝트는 단순한 래퍼가 아닙니다.

이는 현대 AI 스택에서 반복적으로 발생하는

구조적 문제에 대한 아키텍처적 응답입니다.

— Written by Princeps Lee

