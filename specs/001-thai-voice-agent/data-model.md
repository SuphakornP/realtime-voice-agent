# Data Model: Thai/English Realtime Voice Agent

**Feature**: 001-thai-voice-agent  
**Date**: 2025-12-15  
**Status**: Complete

## Overview

This document defines the key entities and their relationships for the Realtime Voice Agent POC. Since this is a stateless POC, entities represent runtime objects rather than persisted data.

---

## Entities

### 1. VoiceSession

Represents a single conversation session between user and agent.

| Attribute | Type | Description |
|-----------|------|-------------|
| `session_id` | `str` | Unique identifier (UUID) |
| `start_time` | `datetime` | Session start timestamp |
| `end_time` | `datetime | None` | Session end timestamp (None if active) |
| `agent_name` | `str` | Name of the active agent |
| `connection_state` | `ConnectionState` | Current WebSocket state |
| `config` | `SessionConfig` | Audio and model configuration |
| `correlation_id` | `str` | Request tracing ID |

**States**: `CONNECTING` → `CONNECTED` → `ACTIVE` → `CLOSING` → `CLOSED`

**Validation Rules**:
- `session_id` must be valid UUID format
- `start_time` must be set on creation
- `connection_state` must follow valid state transitions

---

### 2. SessionConfig

Configuration for a voice session.

| Attribute | Type | Description |
|-----------|------|-------------|
| `model_name` | `str` | Realtime model (e.g., "gpt-realtime") |
| `voice` | `str` | Voice selection (e.g., "nova") |
| `modalities` | `list[str]` | Input/output modes (["audio"]) |
| `input_audio_format` | `str` | Input format (pcm16, g711_ulaw, g711_alaw) |
| `output_audio_format` | `str` | Output format (pcm16, g711_ulaw, g711_alaw) |
| `turn_detection` | `TurnDetectionConfig` | VAD configuration |
| `transcription_model` | `str` | Model for transcription |

**Validation Rules**:
- `voice` must be one of: alloy, echo, fable, onyx, nova, shimmer, ash
- `input_audio_format` must be one of: pcm16, g711_ulaw, g711_alaw
- `output_audio_format` must be one of: pcm16, g711_ulaw, g711_alaw
- `modalities` must contain at least one of: "audio", "text"

---

### 3. TurnDetectionConfig

Voice activity detection configuration.

| Attribute | Type | Description |
|-----------|------|-------------|
| `type` | `str` | Detection method (server_vad, semantic_vad) |
| `threshold` | `float` | Voice activity threshold (0.0-1.0) |
| `silence_duration_ms` | `int` | Silence to detect turn end |
| `prefix_padding_ms` | `int` | Audio padding before speech |
| `interrupt_response` | `bool` | Allow user interruptions |

**Validation Rules**:
- `type` must be one of: server_vad, semantic_vad
- `threshold` must be between 0.0 and 1.0
- `silence_duration_ms` must be positive integer
- `prefix_padding_ms` must be non-negative integer

---

### 4. SessionEvent

Represents any event that occurs during a session.

| Attribute | Type | Description |
|-----------|------|-------------|
| `event_id` | `str` | Unique event identifier (UUID) |
| `session_id` | `str` | Parent session ID |
| `event_type` | `EventType` | Type of event |
| `timestamp` | `datetime` | When event occurred |
| `payload` | `dict` | Event-specific data |
| `correlation_id` | `str` | Request tracing ID |

**Event Types**:
- `agent_start` - Agent begins processing
- `agent_end` - Agent completes processing
- `audio` - Audio chunk received/sent
- `audio_end` - Agent finished speaking
- `audio_interrupted` - User interrupted agent
- `tool_start` - Tool execution begins
- `tool_end` - Tool execution completes
- `handoff` - Agent transfer (not used in POC)
- `error` - Error occurred
- `guardrail_tripped` - Safety guardrail triggered

---

### 5. ConversationTurn

Represents one exchange (user input + agent response).

| Attribute | Type | Description |
|-----------|------|-------------|
| `turn_id` | `str` | Unique turn identifier |
| `session_id` | `str` | Parent session ID |
| `user_transcript` | `str | None` | Transcribed user speech |
| `agent_transcript` | `str | None` | Transcribed agent response |
| `detected_language` | `str` | Detected language (th, en) |
| `tools_used` | `list[str]` | Names of tools executed |
| `start_time` | `datetime` | Turn start timestamp |
| `end_time` | `datetime | None` | Turn end timestamp |
| `latency_ms` | `int | None` | Response latency in milliseconds |
| `was_interrupted` | `bool` | Whether user interrupted |

**Validation Rules**:
- `detected_language` must be one of: th, en, unknown
- `latency_ms` must be non-negative if set

---

### 6. AudioChunk

Represents a chunk of audio data.

| Attribute | Type | Description |
|-----------|------|-------------|
| `chunk_id` | `str` | Unique chunk identifier |
| `session_id` | `str` | Parent session ID |
| `direction` | `str` | "input" or "output" |
| `data` | `bytes` | Raw audio bytes |
| `format` | `str` | Audio format (pcm16, etc.) |
| `timestamp` | `datetime` | When chunk was captured/received |
| `duration_ms` | `int` | Duration in milliseconds |

**Validation Rules**:
- `direction` must be one of: input, output
- `data` must not be empty
- `duration_ms` must be positive

---

### 7. FunctionTool

Represents a callable function tool.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Tool name (e.g., "get_current_time") |
| `description` | `str` | Human-readable description |
| `parameters` | `dict` | JSON Schema for parameters |
| `handler` | `Callable` | Function to execute |

**Validation Rules**:
- `name` must be valid Python identifier
- `description` must not be empty
- `handler` must be callable

---

## Entity Relationships

```
┌─────────────────┐
│  VoiceSession   │
├─────────────────┤
│ session_id (PK) │
│ config ─────────┼──────► SessionConfig
│                 │              │
└────────┬────────┘              ▼
         │                TurnDetectionConfig
         │
         ├──────────────────────────────────┐
         │                                  │
         ▼                                  ▼
┌─────────────────┐              ┌─────────────────┐
│  SessionEvent   │              │ConversationTurn │
├─────────────────┤              ├─────────────────┤
│ event_id (PK)   │              │ turn_id (PK)    │
│ session_id (FK) │              │ session_id (FK) │
│ event_type      │              │ tools_used[]────┼──► FunctionTool
└─────────────────┘              └─────────────────┘
         │
         ▼
┌─────────────────┐
│   AudioChunk    │
├─────────────────┤
│ chunk_id (PK)   │
│ session_id (FK) │
└─────────────────┘
```

---

## State Transitions

### VoiceSession Connection State

```
     ┌──────────────┐
     │  CONNECTING  │
     └──────┬───────┘
            │ WebSocket connected
            ▼
     ┌──────────────┐
     │  CONNECTED   │
     └──────┬───────┘
            │ Session initialized
            ▼
     ┌──────────────┐
     │    ACTIVE    │◄────────┐
     └──────┬───────┘         │
            │                 │ Reconnected
            │ User/system     │
            │ closes          │
            ▼                 │
     ┌──────────────┐         │
     │   CLOSING    │─────────┘
     └──────┬───────┘  (if reconnect)
            │
            │ Cleanup complete
            ▼
     ┌──────────────┐
     │    CLOSED    │
     └──────────────┘
```

---

## Enumerations

### ConnectionState
```python
class ConnectionState(str, Enum):
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ACTIVE = "active"
    CLOSING = "closing"
    CLOSED = "closed"
```

### EventType
```python
class EventType(str, Enum):
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    AUDIO = "audio"
    AUDIO_END = "audio_end"
    AUDIO_INTERRUPTED = "audio_interrupted"
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    HANDOFF = "handoff"
    ERROR = "error"
    GUARDRAIL_TRIPPED = "guardrail_tripped"
    HISTORY_UPDATED = "history_updated"
    HISTORY_ADDED = "history_added"
    RAW_MODEL_EVENT = "raw_model_event"
```

### AudioDirection
```python
class AudioDirection(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
```

### Language
```python
class Language(str, Enum):
    THAI = "th"
    ENGLISH = "en"
    UNKNOWN = "unknown"
```
