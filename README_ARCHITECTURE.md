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

