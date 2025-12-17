"""Data models and enums for Voice Agent."""

from enum import Enum


class ConnectionState(str, Enum):
    """WebSocket connection states for voice session."""

    CONNECTING = "connecting"
    CONNECTED = "connected"
    ACTIVE = "active"
    CLOSING = "closing"
    CLOSED = "closed"


class EventType(str, Enum):
    """Types of events that occur during a voice session."""

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


class AudioDirection(str, Enum):
    """Direction of audio data flow."""

    INPUT = "input"
    OUTPUT = "output"


class Language(str, Enum):
    """Supported languages for voice agent."""

    THAI = "th"
    ENGLISH = "en"
    UNKNOWN = "unknown"


__all__ = [
    "ConnectionState",
    "EventType",
    "AudioDirection",
    "Language",
]
