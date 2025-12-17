"""Integration tests for interruption handling."""

import pytest
from unittest.mock import MagicMock, patch

from src.audio import AudioOutputStream
from src.events import EventHandler
from src.models.conversation import ConversationTurn
from src.models import Language


class TestInterruptionHandling:
    """Integration tests for user interruption of agent speech."""

    def test_audio_queue_can_be_cleared(self) -> None:
        """Test audio output queue can be cleared for interruption."""
        with patch("src.audio.sd"):
            output = AudioOutputStream()
            output._running = True

            # Simulate agent speaking (multiple chunks queued)
            for i in range(10):
                output.play(b"\x00" * 1000)

            assert output.queue_size == 10

            # Simulate interruption
            output.clear()

            assert output.queue_size == 0

    def test_event_handler_calls_interrupt_callback(self) -> None:
        """Test event handler calls interrupt callback."""
        interrupt_called = False

        def on_interrupt():
            nonlocal interrupt_called
            interrupt_called = True

        handler = EventHandler(
            session_id="test-session",
            correlation_id="test-correlation",
            on_audio_interrupted=on_interrupt,
        )

        # Simulate interrupt event
        mock_event = MagicMock()
        mock_event.type = "audio_interrupted"

        import asyncio
        asyncio.run(handler._handle_audio_interrupted(mock_event))

        assert interrupt_called

    def test_conversation_turn_tracks_interruption(self) -> None:
        """Test conversation turn can track interruption."""
        turn = ConversationTurn(
            session_id="test-session",
            detected_language=Language.THAI,
        )

        assert turn.was_interrupted is False

        turn.mark_interrupted()

        assert turn.was_interrupted is True

    def test_interrupt_resets_audio_chunk_count(self) -> None:
        """Test interruption resets audio chunk counter in event handler."""
        handler = EventHandler(
            session_id="test-session",
            correlation_id="test-correlation",
        )

        # Simulate receiving audio chunks
        handler._audio_chunk_count = 15

        # Simulate interrupt
        mock_event = MagicMock()
        import asyncio
        asyncio.run(handler._handle_audio_interrupted(mock_event))

        assert handler._audio_chunk_count == 0
