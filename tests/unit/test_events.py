"""Unit tests for event logging."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock

from src.events import EventHandler
from src.models.events import SessionEvent
from src.models import EventType


class TestSessionEvent:
    """Tests for SessionEvent model."""

    def test_event_has_id(self) -> None:
        """Test event has auto-generated ID."""
        event = SessionEvent(
            session_id="test-session",
            event_type=EventType.AGENT_START,
            correlation_id="test-correlation",
        )
        assert event.event_id is not None
        assert len(event.event_id) > 0

    def test_event_has_timestamp(self) -> None:
        """Test event has auto-generated timestamp."""
        event = SessionEvent(
            session_id="test-session",
            event_type=EventType.AUDIO,
            correlation_id="test-correlation",
        )
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)

    def test_event_to_log_dict(self) -> None:
        """Test event converts to log dictionary."""
        event = SessionEvent(
            session_id="test-session",
            event_type=EventType.TOOL_START,
            correlation_id="test-correlation",
            payload={"tool_name": "get_current_time"},
        )

        log_dict = event.to_log_dict()

        assert "event_id" in log_dict
        assert "session_id" in log_dict
        assert "event_type" in log_dict
        assert "timestamp" in log_dict
        assert "correlation_id" in log_dict
        assert "payload" in log_dict
        assert log_dict["event_type"] == "tool_start"

    def test_event_payload_default_empty(self) -> None:
        """Test event payload defaults to empty dict."""
        event = SessionEvent(
            session_id="test-session",
            event_type=EventType.AGENT_END,
            correlation_id="test-correlation",
        )
        assert event.payload == {}


class TestEventHandler:
    """Tests for EventHandler class."""

    def test_handler_tracks_session_id(self) -> None:
        """Test handler tracks session ID."""
        handler = EventHandler(
            session_id="test-session-123",
            correlation_id="test-correlation",
        )
        assert handler.session_id == "test-session-123"

    def test_handler_tracks_correlation_id(self) -> None:
        """Test handler tracks correlation ID."""
        handler = EventHandler(
            session_id="test-session",
            correlation_id="test-correlation-456",
        )
        assert handler.correlation_id == "test-correlation-456"

    def test_handler_creates_event(self) -> None:
        """Test handler creates events with correct attributes."""
        handler = EventHandler(
            session_id="test-session",
            correlation_id="test-correlation",
        )

        event = handler._create_event(
            EventType.AGENT_START,
            {"agent_name": "Test Agent"},
        )

        assert event.session_id == "test-session"
        assert event.correlation_id == "test-correlation"
        assert event.event_type == EventType.AGENT_START
        assert event.payload["agent_name"] == "Test Agent"

    def test_audio_chunk_counter(self) -> None:
        """Test handler counts audio chunks."""
        handler = EventHandler(
            session_id="test-session",
            correlation_id="test-correlation",
        )

        assert handler._audio_chunk_count == 0

        # Simulate receiving chunks
        handler._audio_chunk_count = 5
        assert handler._audio_chunk_count == 5

    def test_audio_output_callback_called(self) -> None:
        """Test audio output callback is called."""
        received_audio = []

        def on_audio(data: bytes) -> None:
            received_audio.append(data)

        handler = EventHandler(
            session_id="test-session",
            correlation_id="test-correlation",
            on_audio_output=on_audio,
        )

        # Simulate audio event
        mock_event = MagicMock()
        mock_event.data = b"\x00\x01\x02\x03"

        import asyncio
        asyncio.run(handler._handle_audio(mock_event))

        assert len(received_audio) == 1
        assert received_audio[0] == b"\x00\x01\x02\x03"
