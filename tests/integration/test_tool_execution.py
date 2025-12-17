"""Integration tests for tool execution flow."""

import pytest
from unittest.mock import MagicMock

from src.tools import get_current_time, AVAILABLE_TOOLS
from src.events import EventHandler
from src.models.conversation import ConversationTurn
from src.models import Language


class TestToolExecution:
    """Integration tests for tool execution during conversation."""

    def test_get_current_time_available(self) -> None:
        """Test get_current_time tool is available."""
        assert "get_current_time" in [t.__name__ for t in AVAILABLE_TOOLS]

    def test_tool_returns_valid_time(self) -> None:
        """Test tool returns valid time string."""
        result = get_current_time()
        assert result is not None
        assert len(result) > 0

    def test_tool_thai_response(self) -> None:
        """Test tool can return Thai formatted time."""
        result = get_current_time(language="th")
        # Should contain Thai time marker
        assert "น." in result

    def test_tool_english_response(self) -> None:
        """Test tool can return English formatted time."""
        result = get_current_time(language="en")
        # Should contain AM/PM
        assert "AM" in result or "PM" in result

    def test_event_handler_logs_tool_start(self) -> None:
        """Test event handler logs tool start."""
        handler = EventHandler(
            session_id="test-session",
            correlation_id="test-correlation",
        )

        mock_event = MagicMock()
        mock_event.tool_name = "get_current_time"
        mock_event.name = "get_current_time"
        mock_event.arguments = {}

        import asyncio
        asyncio.run(handler._handle_tool_start(mock_event))
        # Should not raise

    def test_event_handler_logs_tool_end(self) -> None:
        """Test event handler logs tool end."""
        handler = EventHandler(
            session_id="test-session",
            correlation_id="test-correlation",
        )

        mock_event = MagicMock()
        mock_event.tool_name = "get_current_time"
        mock_event.name = "get_current_time"
        mock_event.result = "15:30 น."
        mock_event.success = True

        import asyncio
        asyncio.run(handler._handle_tool_end(mock_event))
        # Should not raise

    def test_conversation_turn_tracks_tools(self) -> None:
        """Test conversation turn tracks tools used."""
        turn = ConversationTurn(
            session_id="test-session",
            detected_language=Language.THAI,
        )

        assert len(turn.tools_used) == 0

        turn.add_tool("get_current_time")

        assert "get_current_time" in turn.tools_used

    def test_tool_not_added_twice(self) -> None:
        """Test same tool is not added twice to turn."""
        turn = ConversationTurn(
            session_id="test-session",
            detected_language=Language.ENGLISH,
        )

        turn.add_tool("get_current_time")
        turn.add_tool("get_current_time")

        assert turn.tools_used.count("get_current_time") == 1
