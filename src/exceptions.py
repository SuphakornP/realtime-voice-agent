"""Custom exceptions with error codes for Voice Agent."""

from typing import Any


class VoiceAgentError(Exception):
    """Base exception for Voice Agent errors."""

    code: str = "VOICE_AGENT_ERROR"
    message: str = "An error occurred in the voice agent"

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> None:
        self.message = message or self.message
        self.details = details or {}
        self.correlation_id = correlation_id
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for logging/response."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "request_id": self.correlation_id,
            }
        }


class SessionInitError(VoiceAgentError):
    """Failed to initialize voice session."""

    code = "VOICE_SESSION_INIT_FAILED"
    message = "Failed to initialize voice session"


class SessionExpiredError(VoiceAgentError):
    """Voice session has expired or disconnected."""

    code = "VOICE_SESSION_EXPIRED"
    message = "Voice session has expired or disconnected"


class AudioFormatError(VoiceAgentError):
    """Invalid or unsupported audio format."""

    code = "AUDIO_FORMAT_UNSUPPORTED"
    message = "Audio format is not supported"


class AudioDeviceError(VoiceAgentError):
    """Microphone or speaker not available."""

    code = "AUDIO_DEVICE_ERROR"
    message = "Audio device is not available"


class ToolExecutionError(VoiceAgentError):
    """Function tool execution failed."""

    code = "TOOL_EXECUTION_FAILED"
    message = "Tool execution failed"


class APIRateLimitError(VoiceAgentError):
    """OpenAI API rate limit exceeded."""

    code = "API_RATE_LIMITED"
    message = "API rate limit exceeded"


class APIConnectionError(VoiceAgentError):
    """WebSocket connection to API failed."""

    code = "API_CONNECTION_ERROR"
    message = "Failed to connect to API"


class TranscriptionError(VoiceAgentError):
    """Speech transcription failed."""

    code = "TRANSCRIPTION_FAILED"
    message = "Failed to transcribe speech"


class ConfigValidationError(VoiceAgentError):
    """Configuration validation failed."""

    code = "CONFIG_VALIDATION_ERROR"
    message = "Configuration validation failed"


__all__ = [
    "VoiceAgentError",
    "SessionInitError",
    "SessionExpiredError",
    "AudioFormatError",
    "AudioDeviceError",
    "ToolExecutionError",
    "APIRateLimitError",
    "APIConnectionError",
    "TranscriptionError",
    "ConfigValidationError",
]
