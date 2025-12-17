"""Voice session model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from src.models import ConnectionState

if TYPE_CHECKING:
    from src.models.config import SessionConfig


class VoiceSession(BaseModel):
    """Represents a single conversation session between user and agent."""

    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique session identifier",
    )
    start_time: datetime = Field(
        default_factory=datetime.now,
        description="Session start timestamp",
    )
    end_time: datetime | None = Field(
        default=None,
        description="Session end timestamp (None if active)",
    )
    agent_name: str = Field(
        default="Thai Voice Assistant",
        description="Name of the active agent",
    )
    connection_state: ConnectionState = Field(
        default=ConnectionState.CONNECTING,
        description="Current WebSocket connection state",
    )
    correlation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Request tracing ID for logging",
    )

    def is_active(self) -> bool:
        """Check if session is currently active."""
        return self.connection_state == ConnectionState.ACTIVE

    def is_closed(self) -> bool:
        """Check if session has been closed."""
        return self.connection_state == ConnectionState.CLOSED

    def duration_seconds(self) -> float | None:
        """Get session duration in seconds, or None if still active."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time).total_seconds()

    def transition_to(self, new_state: ConnectionState) -> None:
        """Transition to a new connection state with validation."""
        valid_transitions: dict[ConnectionState, list[ConnectionState]] = {
            ConnectionState.CONNECTING: [ConnectionState.CONNECTED, ConnectionState.CLOSED],
            ConnectionState.CONNECTED: [ConnectionState.ACTIVE, ConnectionState.CLOSING],
            ConnectionState.ACTIVE: [ConnectionState.CLOSING],
            ConnectionState.CLOSING: [ConnectionState.CLOSED, ConnectionState.ACTIVE],
            ConnectionState.CLOSED: [],
        }

        if new_state not in valid_transitions.get(self.connection_state, []):
            raise ValueError(
                f"Invalid state transition from {self.connection_state} to {new_state}"
            )

        self.connection_state = new_state

        if new_state == ConnectionState.CLOSED and self.end_time is None:
            self.end_time = datetime.now()


__all__ = ["VoiceSession"]
