"""Session event model."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.models import EventType


class SessionEvent(BaseModel):
    """Represents any event that occurs during a voice session."""

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique event identifier",
    )
    session_id: str = Field(
        ...,
        description="Parent session ID",
    )
    event_type: EventType = Field(
        ...,
        description="Type of event",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When event occurred",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data",
    )
    correlation_id: str = Field(
        ...,
        description="Request tracing ID for logging",
    )

    def to_log_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for logging."""
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "payload": self.payload,
        }


__all__ = ["SessionEvent"]
