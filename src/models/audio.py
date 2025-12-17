"""Audio chunk model."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AudioChunk(BaseModel):
    """Represents a chunk of audio data."""

    chunk_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique chunk identifier",
    )
    session_id: str = Field(
        ...,
        description="Parent session ID",
    )
    direction: Literal["input", "output"] = Field(
        ...,
        description="Direction of audio flow",
    )
    data: bytes = Field(
        ...,
        description="Raw audio bytes",
    )
    format: Literal["pcm16", "g711_ulaw", "g711_alaw"] = Field(
        default="pcm16",
        description="Audio format",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When chunk was captured/received",
    )
    duration_ms: int = Field(
        ...,
        gt=0,
        description="Duration in milliseconds",
    )
    sequence_number: int = Field(
        default=0,
        ge=0,
        description="Sequence number for ordering",
    )

    @field_validator("data")
    @classmethod
    def validate_data_not_empty(cls, v: bytes) -> bytes:
        """Ensure audio data is not empty."""
        if not v:
            raise ValueError("Audio data must not be empty")
        return v

    model_config = {"arbitrary_types_allowed": True}


__all__ = ["AudioChunk"]
