"""Integration tests for Thai conversation flow."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agent import BILINGUAL_INSTRUCTIONS
from src.models.config import SessionConfig
from src.models.session import VoiceSession
from src.models import ConnectionState


class TestThaiConversationFlow:
    """Integration tests for Thai language conversation."""

    @pytest.fixture
    def mock_realtime_session(self) -> MagicMock:
        """Create mock realtime session."""
        mock = MagicMock()
        mock.send_audio = AsyncMock()
        mock.send_message = AsyncMock()
        mock.__aiter__ = MagicMock(return_value=iter([]))
        return mock

    def test_agent_configured_for_thai(self) -> None:
        """Test agent is configured to handle Thai language."""
        # Test using BILINGUAL_INSTRUCTIONS directly (agents package not required)
        assert "ไทย" in BILINGUAL_INSTRUCTIONS or "Thai" in BILINGUAL_INSTRUCTIONS

    def test_session_config_for_voice(self) -> None:
        """Test session config is set up for voice interaction."""
        config = SessionConfig()
        assert "audio" in config.modalities
        assert config.input_audio_format == "pcm16"
        assert config.output_audio_format == "pcm16"

    def test_session_can_transition_to_active(self) -> None:
        """Test voice session can transition through states."""
        session = VoiceSession()
        assert session.connection_state == ConnectionState.CONNECTING

        session.transition_to(ConnectionState.CONNECTED)
        assert session.connection_state == ConnectionState.CONNECTED

        session.transition_to(ConnectionState.ACTIVE)
        assert session.connection_state == ConnectionState.ACTIVE
        assert session.is_active()

    def test_session_tracks_correlation_id(self) -> None:
        """Test session has correlation ID for tracing."""
        session = VoiceSession()
        assert session.correlation_id is not None
        assert len(session.correlation_id) > 0

    def test_turn_detection_allows_interrupts(self) -> None:
        """Test turn detection is configured for interrupts."""
        config = SessionConfig()
        assert config.turn_detection.interrupt_response is True

    def test_semantic_vad_is_default(self) -> None:
        """Test semantic VAD is the default for better Thai support."""
        config = SessionConfig()
        assert config.turn_detection.type == "semantic_vad"

    @pytest.mark.asyncio
    async def test_session_lifecycle(self) -> None:
        """Test complete session lifecycle."""
        session = VoiceSession(agent_name="Thai Voice Assistant")

        # Start
        assert session.connection_state == ConnectionState.CONNECTING
        session.transition_to(ConnectionState.CONNECTED)
        session.transition_to(ConnectionState.ACTIVE)

        # Active conversation
        assert session.is_active()
        assert not session.is_closed()

        # End
        session.transition_to(ConnectionState.CLOSING)
        session.transition_to(ConnectionState.CLOSED)

        assert session.is_closed()
        assert session.end_time is not None
        assert session.duration_seconds() is not None
        assert session.duration_seconds() >= 0
