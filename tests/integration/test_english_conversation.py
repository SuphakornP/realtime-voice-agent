"""Integration tests for English conversation flow."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agent import BILINGUAL_INSTRUCTIONS
from src.models.config import SessionConfig


class TestEnglishConversationFlow:
    """Integration tests for English language conversation."""

    def test_agent_configured_for_english(self) -> None:
        """Test agent is configured to handle English language."""
        # Test using BILINGUAL_INSTRUCTIONS directly (agents package not required)
        assert "English" in BILINGUAL_INSTRUCTIONS or "english" in BILINGUAL_INSTRUCTIONS.lower()

    def test_instructions_mention_english_response(self) -> None:
        """Test instructions specify responding in English when spoken to in English."""
        assert "respond" in BILINGUAL_INSTRUCTIONS.lower()
        assert "English" in BILINGUAL_INSTRUCTIONS

    def test_session_config_supports_audio(self) -> None:
        """Test session config supports audio modality."""
        config = SessionConfig()
        assert "audio" in config.modalities

    def test_voice_selection_available(self) -> None:
        """Test various voice options are available."""
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer", "ash"]
        for voice in valid_voices:
            config = SessionConfig(voice=voice)
            assert config.voice == voice
