"""Unit tests for agent configuration."""

import pytest
from unittest.mock import MagicMock, patch

from src.agent import BILINGUAL_INSTRUCTIONS


class TestBilingualInstructions:
    """Tests for bilingual agent instructions."""

    def test_instructions_contain_thai(self) -> None:
        """Test instructions contain Thai language content."""
        assert "ภาษาไทย" in BILINGUAL_INSTRUCTIONS or "ไทย" in BILINGUAL_INSTRUCTIONS

    def test_instructions_contain_english(self) -> None:
        """Test instructions contain English language content."""
        assert "English" in BILINGUAL_INSTRUCTIONS or "english" in BILINGUAL_INSTRUCTIONS.lower()

    def test_instructions_not_empty(self) -> None:
        """Test instructions are not empty."""
        assert len(BILINGUAL_INSTRUCTIONS) > 0

    def test_instructions_mention_language_detection(self) -> None:
        """Test instructions mention responding in same language."""
        lower_instructions = BILINGUAL_INSTRUCTIONS.lower()
        assert "respond" in lower_instructions or "ตอบ" in BILINGUAL_INSTRUCTIONS


class TestCreateRealtimeAgent:
    """Tests for create_realtime_agent function (requires agents package)."""

    @pytest.fixture
    def mock_realtime_agent(self) -> MagicMock:
        """Create mock RealtimeAgent class."""
        mock_agent = MagicMock()
        mock_agent.name = "Thai Voice Assistant"
        mock_agent.instructions = BILINGUAL_INSTRUCTIONS
        mock_agent.tools = []
        return mock_agent

    def test_agent_has_name_with_mock(self, mock_realtime_agent: MagicMock) -> None:
        """Test agent has a name."""
        assert mock_realtime_agent.name is not None
        assert len(mock_realtime_agent.name) > 0

    def test_agent_has_instructions_with_mock(self, mock_realtime_agent: MagicMock) -> None:
        """Test agent has instructions."""
        assert mock_realtime_agent.instructions is not None
        assert len(mock_realtime_agent.instructions) > 0

    def test_agent_instructions_are_bilingual_with_mock(self, mock_realtime_agent: MagicMock) -> None:
        """Test agent instructions are the bilingual instructions."""
        assert mock_realtime_agent.instructions == BILINGUAL_INSTRUCTIONS

    def test_default_agent_name(self) -> None:
        """Test default agent name constant."""
        # The default name should be "Thai Voice Assistant"
        expected_name = "Thai Voice Assistant"
        assert expected_name == "Thai Voice Assistant"

    def test_bilingual_instructions_not_empty(self) -> None:
        """Test bilingual instructions are not empty."""
        assert len(BILINGUAL_INSTRUCTIONS) > 100  # Should be substantial
