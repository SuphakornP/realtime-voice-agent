"""Unit tests for function tools."""

import pytest
from datetime import datetime
from unittest.mock import patch

from src.tools import get_current_time, format_time_thai, format_time_english


class TestGetCurrentTime:
    """Tests for get_current_time tool."""

    def test_returns_string(self) -> None:
        """Test get_current_time returns a string."""
        result = get_current_time()
        assert isinstance(result, str)

    def test_contains_time_components(self) -> None:
        """Test result contains time information."""
        result = get_current_time()
        # Should contain numbers (hours/minutes)
        assert any(c.isdigit() for c in result)

    def test_thai_format(self) -> None:
        """Test Thai time format."""
        result = get_current_time(language="th")
        # Thai format should contain น. (abbreviation for นาฬิกา)
        assert "น." in result or ":" in result

    def test_english_format(self) -> None:
        """Test English time format."""
        result = get_current_time(language="en")
        # English format should contain AM/PM or colon
        assert "AM" in result or "PM" in result or ":" in result


class TestFormatTimeThai:
    """Tests for Thai time formatting."""

    def test_morning_time(self) -> None:
        """Test morning time formatting."""
        dt = datetime(2025, 12, 15, 9, 30)
        result = format_time_thai(dt)
        assert "9" in result or "๙" in result
        assert "30" in result or "๓๐" in result

    def test_afternoon_time(self) -> None:
        """Test afternoon time formatting."""
        dt = datetime(2025, 12, 15, 15, 45)
        result = format_time_thai(dt)
        assert "15" in result or "3" in result

    def test_midnight(self) -> None:
        """Test midnight formatting."""
        dt = datetime(2025, 12, 15, 0, 0)
        result = format_time_thai(dt)
        assert "0" in result or "เที่ยงคืน" in result


class TestFormatTimeEnglish:
    """Tests for English time formatting."""

    def test_morning_time(self) -> None:
        """Test morning time formatting."""
        dt = datetime(2025, 12, 15, 9, 30)
        result = format_time_english(dt)
        assert "9:30" in result
        assert "AM" in result

    def test_afternoon_time(self) -> None:
        """Test afternoon time formatting."""
        dt = datetime(2025, 12, 15, 15, 45)
        result = format_time_english(dt)
        assert "3:45" in result
        assert "PM" in result

    def test_noon(self) -> None:
        """Test noon formatting."""
        dt = datetime(2025, 12, 15, 12, 0)
        result = format_time_english(dt)
        assert "12:00" in result
        assert "PM" in result

    def test_midnight(self) -> None:
        """Test midnight formatting."""
        dt = datetime(2025, 12, 15, 0, 0)
        result = format_time_english(dt)
        assert "12:00" in result
        assert "AM" in result
