# Implementation Plan: Thai/English Realtime Voice Agent

**Branch**: `001-thai-voice-agent` | **Date**: 2025-12-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-thai-voice-agent/spec.md`

## Summary

Build a real-time voice-enabled AI agent POC using OpenAI's Agents SDK that supports natural voice conversations in both Thai and English languages. The system will stream audio bidirectionally via WebSocket, handle user interruptions, execute function tools during conversations, and log all session events for debugging and analysis.

**Technical Approach**: Use OpenAI Agents SDK's `RealtimeAgent`, `RealtimeRunner`, and `RealtimeSession` components with PCM16 audio format and semantic VAD for turn detection. Implement bilingual agent instructions and simple demo tools (time).

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: openai-agents[voice], pyaudio (audio I/O), python-dotenv (env vars)  
**Storage**: N/A (stateless POC, logs to stdout/file)  
**Testing**: pytest with pytest-asyncio for async tests  
**Target Platform**: macOS/Linux desktop with microphone and speakers  
**Project Type**: Single project (CLI application)  
**Performance Goals**: <500ms response latency (p95), real-time audio streaming  
**Constraints**: <200ms interruption response, stable WebSocket connection required  
**Scale/Scope**: Single user POC, 1 agent, 1-2 demo tools

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. RESTful API Design** | ✅ N/A | POC uses WebSocket for realtime, no REST endpoints |
| **II. Comprehensive Error Handling** | ✅ Pass | Error events logged with correlation IDs per FR-008, FR-011 |
| **III. Input Validation** | ✅ Pass | Audio format validation per FR-012, config validation at startup |
| **IV. Security Best Practices** | ✅ Pass | API key via env var, no secrets in code |
| **V. Test Coverage Requirements** | ✅ Pass | Unit tests for tools, integration tests for session flow |

**Gate Status**: ✅ PASSED - All applicable principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-thai-voice-agent/
├── plan.md              # This file
├── research.md          # Phase 0: Technology research
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Setup and run guide
├── contracts/           # Phase 1: API/event contracts
│   └── events.md        # Event type definitions
└── tasks.md             # Phase 2: Implementation tasks
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py              # Entry point, CLI interface
├── agent.py             # RealtimeAgent configuration
├── runner.py            # RealtimeRunner setup and session management
├── tools.py             # Function tools (get_time, etc.)
├── events.py            # Event handlers and logging
├── audio.py             # Audio input/output handling
└── config.py            # Configuration and validation

tests/
├── __init__.py
├── unit/
│   ├── test_tools.py    # Tool function tests
│   ├── test_config.py   # Config validation tests
│   └── test_events.py   # Event handler tests
├── integration/
│   └── test_session.py  # Session flow tests (mocked API)
└── conftest.py          # Shared fixtures
```

**Structure Decision**: Single project structure selected. This is a CLI-based POC without web frontend or mobile components. All source code in `src/`, all tests in `tests/` with unit/integration separation per constitution.

## Complexity Tracking

> No violations - design follows constitution principles
