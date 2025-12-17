"""Configuration models for voice session."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TurnDetectionConfig(BaseModel):
    """Voice activity detection configuration."""

    type: Literal["server_vad", "semantic_vad"] = Field(
        default="semantic_vad",
        description="Detection method for turn-taking",
    )
    threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Voice activity threshold (0.0-1.0)",
    )
    silence_duration_ms: int = Field(
        default=500,
        gt=0,
        description="Silence duration to detect turn end in milliseconds",
    )
    prefix_padding_ms: int = Field(
        default=300,
        ge=0,
        description="Audio padding before speech in milliseconds",
    )
    interrupt_response: bool = Field(
        default=True,
        description="Allow user to interrupt agent responses",
    )


class SessionConfig(BaseModel):
    """Configuration for a voice session."""

    model_name: str = Field(
        default="gpt-4o-realtime-preview",
        description="Realtime model to use",
    )
    voice: Literal["alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse", "marin", "cedar"] = Field(
        default="ash",
        description="Voice selection for agent responses",
    )
    modalities: list[Literal["audio", "text"]] = Field(
        default=["audio"],
        min_length=1,
        description="Input/output modes",
    )
    input_audio_format: Literal["pcm16", "g711_ulaw", "g711_alaw"] = Field(
        default="pcm16",
        description="Format for input audio",
    )
    output_audio_format: Literal["pcm16", "g711_ulaw", "g711_alaw"] = Field(
        default="pcm16",
        description="Format for output audio",
    )
    turn_detection: TurnDetectionConfig = Field(
        default_factory=TurnDetectionConfig,
        description="VAD configuration",
    )
    transcription_model: str = Field(
        default="gpt-4o-mini-transcribe",
        description="Model for input audio transcription",
    )

    @field_validator("modalities")
    @classmethod
    def validate_modalities(cls, v: list[str]) -> list[str]:
        """Ensure at least one modality is specified."""
        if not v:
            raise ValueError("At least one modality must be specified")
        return v

    def to_runner_config(self) -> dict:
        """Convert to format expected by RealtimeRunner."""
        return {
            "model_settings": {
                "model_name": self.model_name,
                "voice": self.voice,
                "modalities": self.modalities,
                "input_audio_format": self.input_audio_format,
                "output_audio_format": self.output_audio_format,
                "input_audio_transcription": {"model": self.transcription_model},
                "turn_detection": {
                    "type": self.turn_detection.type,
                    "interrupt_response": self.turn_detection.interrupt_response,
                },
            }
        }


__all__ = ["SessionConfig", "TurnDetectionConfig"]
