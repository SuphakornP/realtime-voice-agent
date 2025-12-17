"""Integration tests for language switching."""

import pytest

from src.agent import BILINGUAL_INSTRUCTIONS
from src.models.conversation import ConversationTurn
from src.models import Language


class TestLanguageSwitching:
    """Integration tests for switching between Thai and English."""

    def test_instructions_support_language_switching(self) -> None:
        """Test instructions mention language switching capability."""
        lower_instructions = BILINGUAL_INSTRUCTIONS.lower()
        # Should mention switching or changing languages
        assert "switch" in lower_instructions or "เปลี่ยน" in BILINGUAL_INSTRUCTIONS

    def test_agent_has_bilingual_instructions(self) -> None:
        """Test agent has both Thai and English in instructions."""
        # Test using BILINGUAL_INSTRUCTIONS directly (agents package not required)
        # Should have Thai content
        has_thai = any(ord(c) > 127 for c in BILINGUAL_INSTRUCTIONS)  # Non-ASCII chars
        # Should have English content
        has_english = "English" in BILINGUAL_INSTRUCTIONS or "you" in BILINGUAL_INSTRUCTIONS.lower()
        assert has_thai and has_english

    def test_conversation_turn_tracks_language(self) -> None:
        """Test conversation turn can track detected language."""
        turn_thai = ConversationTurn(
            session_id="test-session",
            detected_language=Language.THAI,
        )
        assert turn_thai.detected_language == Language.THAI

        turn_english = ConversationTurn(
            session_id="test-session",
            detected_language=Language.ENGLISH,
        )
        assert turn_english.detected_language == Language.ENGLISH

    def test_language_can_change_between_turns(self) -> None:
        """Test language can change between conversation turns."""
        turn1 = ConversationTurn(
            session_id="test-session",
            detected_language=Language.THAI,
            user_transcript="สวัสดีครับ",
        )

        turn2 = ConversationTurn(
            session_id="test-session",
            detected_language=Language.ENGLISH,
            user_transcript="Hello, how are you?",
        )

        # Both turns should be valid with different languages
        assert turn1.detected_language != turn2.detected_language
        assert turn1.user_transcript is not None
        assert turn2.user_transcript is not None
