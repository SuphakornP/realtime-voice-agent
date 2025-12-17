"""Conversation turn model for tracking exchanges."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.models import Language


class ConversationTurn(BaseModel):
    """Represents one exchange (user input + agent response)."""

    turn_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique turn identifier",
    )
    session_id: str = Field(
        ...,
        description="Parent session ID",
    )
    user_transcript: str | None = Field(
        default=None,
        description="Transcribed user speech",
    )
    agent_transcript: str | None = Field(
        default=None,
        description="Transcribed agent response",
    )
    detected_language: Language = Field(
        default=Language.UNKNOWN,
        description="Detected language of user input",
    )
    tools_used: list[str] = Field(
        default_factory=list,
        description="Names of tools executed during this turn",
    )
    start_time: datetime = Field(
        default_factory=datetime.now,
        description="Turn start timestamp",
    )
    end_time: datetime | None = Field(
        default=None,
        description="Turn end timestamp",
    )
    latency_ms: int | None = Field(
        default=None,
        ge=0,
        description="Response latency in milliseconds",
    )
    was_interrupted: bool = Field(
        default=False,
        description="Whether user interrupted agent response",
    )

    def complete(self, agent_transcript: str | None = None) -> None:
        """Mark the turn as complete.

        Args:
            agent_transcript: Optional agent response transcript
        """
        self.end_time = datetime.now()
        if agent_transcript:
            self.agent_transcript = agent_transcript

        # Calculate latency if we have both timestamps
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.latency_ms = int(delta.total_seconds() * 1000)

    def duration_ms(self) -> int | None:
        """Get turn duration in milliseconds."""
        if self.end_time is None:
            return None
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() * 1000)

    def add_tool(self, tool_name: str) -> None:
        """Record a tool that was used during this turn.

        Args:
            tool_name: Name of the tool
        """
        if tool_name not in self.tools_used:
            self.tools_used.append(tool_name)

    def mark_interrupted(self) -> None:
        """Mark this turn as interrupted by user."""
        self.was_interrupted = True


__all__ = ["ConversationTurn"]
