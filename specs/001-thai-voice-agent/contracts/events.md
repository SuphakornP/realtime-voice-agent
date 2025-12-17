# Event Contracts: Thai/English Realtime Voice Agent

**Feature**: 001-thai-voice-agent  
**Date**: 2025-12-15  
**Status**: Complete

## Overview

This document defines the event contracts for the Realtime Voice Agent. Events are emitted by the `RealtimeSession` and consumed by event handlers for logging, UI updates, and audio playback control.

---

## Event Base Schema

All events follow this base structure:

```json
{
  "event_id": "uuid-string",
  "session_id": "uuid-string",
  "event_type": "string",
  "timestamp": "ISO-8601 datetime",
  "correlation_id": "uuid-string",
  "payload": {}
}
```

---

## Event Types

### 1. agent_start

Emitted when an agent begins processing.

**Payload**:
```json
{
  "agent_name": "string",
  "instructions_hash": "string"
}
```

**Example**:
```json
{
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "session_id": "s1s2s3s4-s5s6-7890-abcd-ef1234567890",
  "event_type": "agent_start",
  "timestamp": "2025-12-15T15:30:00.000Z",
  "correlation_id": "c1c2c3c4-c5c6-7890-abcd-ef1234567890",
  "payload": {
    "agent_name": "Thai Voice Assistant",
    "instructions_hash": "abc123def456"
  }
}
```

---

### 2. agent_end

Emitted when an agent completes processing.

**Payload**:
```json
{
  "agent_name": "string",
  "reason": "string"
}
```

**Reason Values**: `completed`, `handoff`, `error`, `user_ended`

---

### 3. audio

Emitted for each audio chunk from the agent's response.

**Payload**:
```json
{
  "direction": "output",
  "format": "pcm16",
  "data_base64": "string",
  "duration_ms": 100,
  "sequence_number": 1
}
```

**Notes**:
- `data_base64` contains base64-encoded audio bytes
- `sequence_number` allows ordering for playback
- Typical chunk duration is 100ms

---

### 4. audio_end

Emitted when the agent finishes speaking.

**Payload**:
```json
{
  "total_duration_ms": 2500,
  "chunk_count": 25,
  "transcript": "string | null"
}
```

---

### 5. audio_interrupted

Emitted when user interrupts the agent.

**Payload**:
```json
{
  "interrupted_at_ms": 1200,
  "remaining_chunks_dropped": 13
}
```

**Handler Action**: Stop audio playback immediately, clear audio queue.

---

### 6. tool_start

Emitted when a function tool begins execution.

**Payload**:
```json
{
  "tool_name": "get_current_time",
  "arguments": {},
  "invocation_id": "uuid-string"
}
```

---

### 7. tool_end

Emitted when a function tool completes execution.

**Payload**:
```json
{
  "tool_name": "get_current_time",
  "invocation_id": "uuid-string",
  "result": "15:30 น.",
  "duration_ms": 5,
  "success": true,
  "error": null
}
```

**On Error**:
```json
{
  "tool_name": "get_current_time",
  "invocation_id": "uuid-string",
  "result": null,
  "duration_ms": 10,
  "success": false,
  "error": {
    "code": "TOOL_EXECUTION_FAILED",
    "message": "Timezone database not available"
  }
}
```

---

### 8. error

Emitted when an error occurs during the session.

**Payload**:
```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {},
  "recoverable": true
}
```

**Error Codes**:

| Code | Description | Recoverable |
|------|-------------|-------------|
| `VOICE_SESSION_INIT_FAILED` | Failed to initialize session | No |
| `VOICE_SESSION_EXPIRED` | Session timed out | No |
| `AUDIO_FORMAT_UNSUPPORTED` | Invalid audio format | No |
| `AUDIO_DEVICE_ERROR` | Mic/speaker unavailable | No |
| `TOOL_EXECUTION_FAILED` | Tool raised exception | Yes |
| `API_RATE_LIMITED` | Rate limit exceeded | Yes |
| `API_CONNECTION_ERROR` | WebSocket failed | Yes |
| `TRANSCRIPTION_FAILED` | Speech not recognized | Yes |

---

### 9. guardrail_tripped

Emitted when an output guardrail is triggered.

**Payload**:
```json
{
  "guardrail_name": "sensitive_data_check",
  "triggered_text": "partial output...",
  "action_taken": "response_stopped"
}
```

**Note**: Not used in POC (no guardrails configured).

---

### 10. history_updated

Emitted when conversation history is updated.

**Payload**:
```json
{
  "turn_count": 5,
  "last_user_input": "What time is it?",
  "last_agent_response": "It's 3:30 PM."
}
```

---

### 11. history_added

Emitted when a new item is added to history.

**Payload**:
```json
{
  "role": "user | assistant",
  "content_type": "audio | text",
  "transcript": "string | null"
}
```

---

### 12. raw_model_event

Emitted for low-level model events (debugging).

**Payload**:
```json
{
  "raw_type": "string",
  "raw_data": {}
}
```

**Note**: Only emitted when log level is DEBUG.

---

## Event Flow Diagram

```
Session Start
     │
     ▼
┌─────────────┐
│ agent_start │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│           Conversation Loop              │
│                                          │
│  User speaks → (audio input processed)   │
│       │                                  │
│       ▼                                  │
│  ┌──────────┐    ┌────────────┐         │
│  │tool_start│───►│  tool_end  │         │
│  └──────────┘    └────────────┘         │
│       │                                  │
│       ▼                                  │
│  ┌──────────┐                           │
│  │  audio   │ (multiple chunks)         │
│  └────┬─────┘                           │
│       │                                  │
│       ├───► audio_interrupted (if user  │
│       │     speaks during response)      │
│       │                                  │
│       ▼                                  │
│  ┌──────────┐                           │
│  │audio_end │                           │
│  └──────────┘                           │
│       │                                  │
│       ▼                                  │
│  ┌───────────────┐                      │
│  │history_updated│                      │
│  └───────────────┘                      │
│                                          │
└─────────────────────────────────────────┘
       │
       ▼ (user ends or error)
┌─────────────┐
│  agent_end  │
└─────────────┘
```

---

## Logging Format

All events are logged in JSON format:

```json
{
  "timestamp": "2025-12-15T15:30:00.000Z",
  "level": "INFO",
  "event_type": "audio_end",
  "session_id": "s1s2s3s4-...",
  "correlation_id": "c1c2c3c4-...",
  "payload": {
    "total_duration_ms": 2500,
    "chunk_count": 25
  }
}
```

---

## Error Response Contract

When errors occur, the system logs and optionally speaks an error message:

```json
{
  "error": {
    "code": "API_CONNECTION_ERROR",
    "message": "Unable to connect to voice service. Please check your internet connection.",
    "details": {
      "retry_after_ms": 5000,
      "attempt": 2,
      "max_attempts": 3
    },
    "request_id": "uuid-string"
  }
}
```

---

## Tool Contracts

### get_current_time

**Description**: Returns the current time in Thailand timezone.

**Parameters**: None

**Returns**: `string` - Time in Thai format (e.g., "15:30 น.") or English format (e.g., "3:30 PM")

**Errors**:
- `TOOL_EXECUTION_FAILED` - Timezone library error

**Example Invocation**:
```json
{
  "tool_name": "get_current_time",
  "arguments": {}
}
```

**Example Response**:
```json
{
  "result": "15:30 น."
}
```
