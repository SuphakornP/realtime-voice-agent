# Research: Thai/English Realtime Voice Agent

**Feature**: 001-thai-voice-agent  
**Date**: 2025-12-15  
**Status**: Complete

## Overview

This document captures technology research and decisions for the Realtime Voice Agent POC.

---

## 1. OpenAI Agents SDK - Realtime Voice

### Decision
Use `openai-agents[voice]` package with `RealtimeAgent`, `RealtimeRunner`, and `RealtimeSession` components.

### Rationale
- Official OpenAI SDK with first-party support for realtime voice
- Provides high-level abstractions (Agent, Runner, Session) that simplify implementation
- Built-in support for tools, handoffs, and guardrails
- WebSocket-based streaming with low latency
- Semantic VAD for natural turn detection

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| Direct Realtime API (raw WebSocket) | More complex, requires manual session management |
| Whisper + GPT-4 + TTS pipeline | Higher latency (not real-time), more components to manage |
| Third-party voice SDKs (Deepgram, AssemblyAI) | Doesn't integrate with OpenAI's agent framework |

### Key Components
```python
from agents.realtime import RealtimeAgent, RealtimeRunner, RealtimeSession
from agents import function_tool
```

---

## 2. Audio Format Selection

### Decision
Use **PCM16** (16-bit PCM) as the primary audio format.

### Rationale
- Default format for OpenAI Realtime API
- Widely supported by audio libraries (pyaudio, sounddevice)
- Low latency, no compression overhead
- Suitable for desktop POC environment

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| G.711 μ-law | Telephony-focused, not needed for desktop POC |
| G.711 A-law | Same as above |
| Opus | Not supported by OpenAI Realtime API |

### Configuration
```python
config = {
    "model_settings": {
        "input_audio_format": "pcm16",
        "output_audio_format": "pcm16",
    }
}
```

---

## 3. Voice Activity Detection (VAD)

### Decision
Use **semantic_vad** with interrupt_response enabled.

### Rationale
- Semantic VAD understands speech patterns better than simple energy-based detection
- Reduces false positives from background noise
- `interrupt_response: True` allows natural conversation interruptions
- Better suited for Thai language which has different prosodic patterns than English

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| server_vad | Less sophisticated, more false positives |
| Manual VAD | Requires custom implementation, more complexity |
| No VAD (push-to-talk) | Poor user experience for conversational POC |

### Configuration
```python
"turn_detection": {
    "type": "semantic_vad",
    "interrupt_response": True
}
```

---

## 4. Voice Selection

### Decision
Use **nova** as the default voice, with option to configure.

### Rationale
- Nova provides clear, natural-sounding speech
- Testing showed acceptable Thai pronunciation
- Can be changed via configuration if needed

### Available Voices
- alloy, echo, fable, onyx, nova, shimmer, ash

### Configuration
```python
"voice": "nova"  # Configurable via environment variable
```

---

## 5. Thai Language Support

### Decision
Use bilingual agent instructions with language detection in the prompt.

### Rationale
- OpenAI's realtime model supports Thai language natively
- No special configuration needed beyond instructions
- Agent can detect language from user input and respond accordingly
- Transcription model (gpt-4o-mini-transcribe) handles Thai well

### Implementation
```python
instructions = """
คุณเป็นผู้ช่วย AI ที่สามารถสื่อสารได้ทั้งภาษาไทยและภาษาอังกฤษ
You are an AI assistant capable of communicating in both Thai and English.

- ตอบกลับเป็นภาษาเดียวกับที่ผู้ใช้พูด
- Respond in the same language the user speaks
- Keep responses brief and conversational
"""
```

---

## 6. Audio I/O Library

### Decision
Use **sounddevice** for audio input/output.

### Rationale
- Cross-platform (macOS, Linux, Windows)
- Simple async-friendly API
- Good performance for real-time streaming
- No complex dependencies (uses PortAudio)

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| pyaudio | Older API, more complex installation |
| pygame.mixer | Not designed for real-time streaming |
| Built-in audioop | Too low-level, deprecated in Python 3.11+ |

### Installation
```bash
pip install sounddevice numpy
```

---

## 7. Logging Strategy

### Decision
Use Python's built-in `logging` module with structured JSON output.

### Rationale
- Standard library, no additional dependencies
- Supports correlation IDs via LogRecord extras
- Can output to stdout (development) or file (production)
- Meets constitution requirement for error logging with correlation IDs

### Implementation
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "correlation_id": getattr(record, 'correlation_id', None),
            "event_type": getattr(record, 'event_type', None),
        }
        return json.dumps(log_data)
```

---

## 8. Configuration Management

### Decision
Use **python-dotenv** for environment variables with Pydantic for validation.

### Rationale
- Environment variables for secrets (API key) per security best practices
- Pydantic provides type validation and clear error messages
- `.env` file for local development, env vars in production

### Configuration Schema
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    voice: str = "nova"
    audio_format: str = "pcm16"
    vad_type: str = "semantic_vad"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
```

---

## 9. Testing Strategy

### Decision
Use pytest with pytest-asyncio, mock OpenAI API for unit/integration tests.

### Rationale
- pytest is the standard Python testing framework
- pytest-asyncio handles async test functions
- Mocking API calls allows fast, deterministic tests
- Manual testing required for actual voice quality validation

### Test Categories
| Category | Scope | Mocked |
|----------|-------|--------|
| Unit | Individual functions (tools, config) | N/A |
| Integration | Session flow, event handling | OpenAI API |
| E2E (Manual) | Full voice conversation | No |

---

## 10. Error Handling Patterns

### Decision
Use custom exception classes with error codes, wrap all API calls.

### Rationale
- Meets constitution requirement for structured error handling
- Domain-specific error codes aid debugging
- All errors logged with correlation IDs

### Error Codes
| Code | Description |
|------|-------------|
| `VOICE_SESSION_INIT_FAILED` | Failed to initialize session |
| `VOICE_SESSION_EXPIRED` | Session timed out or disconnected |
| `AUDIO_FORMAT_UNSUPPORTED` | Invalid audio format configuration |
| `AUDIO_DEVICE_ERROR` | Microphone/speaker not available |
| `TOOL_EXECUTION_FAILED` | Function tool raised exception |
| `API_RATE_LIMITED` | OpenAI rate limit exceeded |
| `API_CONNECTION_ERROR` | WebSocket connection failed |

---

## Summary

All technical decisions have been made. No NEEDS CLARIFICATION items remain.

| Area | Decision |
|------|----------|
| SDK | openai-agents[voice] |
| Audio Format | PCM16 |
| VAD | semantic_vad with interrupts |
| Voice | nova (configurable) |
| Audio Library | sounddevice |
| Logging | Python logging with JSON |
| Config | python-dotenv + Pydantic |
| Testing | pytest + pytest-asyncio |
