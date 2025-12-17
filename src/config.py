"""Application settings loaded from environment variables."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_prefix="VOICE_AGENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Required
    openai_api_key: str = Field(
        ...,
        alias="OPENAI_API_KEY",
        description="OpenAI API key with realtime model access",
    )

    # Voice settings
    voice: Literal["alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse", "marin", "cedar"] = Field(
        default="ash",
        description="Voice selection for agent responses",
    )

    # Audio settings
    audio_format: Literal["pcm16", "g711_ulaw", "g711_alaw"] = Field(
        default="pcm16",
        description="Audio format for input/output",
    )

    # VAD settings
    vad_type: Literal["server_vad", "semantic_vad"] = Field(
        default="semantic_vad",
        description="Voice activity detection method",
    )

    # Logging settings
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level",
    )
    log_file: str | None = Field(
        default=None,
        description="Optional log file path",
    )

    # Audio device settings
    input_device: int | None = Field(
        default=None,
        description="Input audio device index",
    )
    output_device: int | None = Field(
        default=None,
        description="Output audio device index",
    )


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


__all__ = ["Settings", "get_settings"]
