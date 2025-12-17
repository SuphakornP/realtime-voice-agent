"""Unit tests for audio handling."""

import pytest
from unittest.mock import MagicMock, patch
import queue

from src.audio import AudioOutputStream, SAMPLE_RATE, CHANNELS, CHUNK_SIZE


class TestAudioOutputStream:
    """Tests for AudioOutputStream class."""

    def test_queue_starts_empty(self) -> None:
        """Test playback queue starts empty."""
        with patch("src.audio.sd"):
            output = AudioOutputStream()
            assert output.queue_size == 0

    def test_play_adds_to_queue(self) -> None:
        """Test play() adds audio to queue."""
        with patch("src.audio.sd"):
            output = AudioOutputStream()
            output._running = True  # Simulate started state

            audio_data = b"\x00" * 1000
            output.play(audio_data)

            assert output.queue_size == 1

    def test_clear_empties_queue(self) -> None:
        """Test clear() empties the playback queue."""
        with patch("src.audio.sd"):
            output = AudioOutputStream()
            output._running = True

            # Add multiple chunks
            for _ in range(5):
                output.play(b"\x00" * 1000)

            assert output.queue_size == 5

            # Clear queue
            output.clear()

            assert output.queue_size == 0

    def test_clear_on_empty_queue(self) -> None:
        """Test clear() works on empty queue."""
        with patch("src.audio.sd"):
            output = AudioOutputStream()
            output.clear()  # Should not raise
            assert output.queue_size == 0

    def test_play_ignored_when_not_running(self) -> None:
        """Test play() is ignored when stream not running."""
        with patch("src.audio.sd"):
            output = AudioOutputStream()
            # _running is False by default

            output.play(b"\x00" * 1000)

            assert output.queue_size == 0

    def test_is_running_property(self) -> None:
        """Test is_running property."""
        with patch("src.audio.sd"):
            output = AudioOutputStream()
            assert output.is_running is False

            output._running = True
            assert output.is_running is True


class TestAudioConstants:
    """Tests for audio constants."""

    def test_sample_rate(self) -> None:
        """Test sample rate is 24kHz for OpenAI API."""
        assert SAMPLE_RATE == 24000

    def test_channels_mono(self) -> None:
        """Test channels is mono."""
        assert CHANNELS == 1

    def test_chunk_size_calculation(self) -> None:
        """Test chunk size is correct for 100ms at 24kHz."""
        expected = int(24000 * 100 / 1000)  # 2400 samples
        assert CHUNK_SIZE == expected
