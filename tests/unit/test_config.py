"""Unit tests for configuration models."""

import pytest
from pydantic import ValidationError

from src.models.config import SessionConfig, TurnDetectionConfig


class TestTurnDetectionConfig:
    """Tests for TurnDetectionConfig model."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = TurnDetectionConfig()
        assert config.type == "semantic_vad"
        assert config.threshold == 0.5
        assert config.silence_duration_ms == 500
        assert config.prefix_padding_ms == 300
        assert config.interrupt_response is True

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = TurnDetectionConfig(
            type="server_vad",
            threshold=0.7,
            silence_duration_ms=800,
            prefix_padding_ms=200,
            interrupt_response=False,
        )
        assert config.type == "server_vad"
        assert config.threshold == 0.7
        assert config.silence_duration_ms == 800
        assert config.prefix_padding_ms == 200
        assert config.interrupt_response is False

    def test_threshold_validation_min(self) -> None:
        """Test threshold minimum validation."""
        with pytest.raises(ValidationError):
            TurnDetectionConfig(threshold=-0.1)

    def test_threshold_validation_max(self) -> None:
        """Test threshold maximum validation."""
        with pytest.raises(ValidationError):
            TurnDetectionConfig(threshold=1.1)

    def test_silence_duration_must_be_positive(self) -> None:
        """Test silence duration must be positive."""
        with pytest.raises(ValidationError):
            TurnDetectionConfig(silence_duration_ms=0)

    def test_prefix_padding_can_be_zero(self) -> None:
        """Test prefix padding can be zero."""
        config = TurnDetectionConfig(prefix_padding_ms=0)
        assert config.prefix_padding_ms == 0

    def test_invalid_vad_type(self) -> None:
        """Test invalid VAD type raises error."""
        with pytest.raises(ValidationError):
            TurnDetectionConfig(type="invalid_vad")


class TestSessionConfig:
    """Tests for SessionConfig model."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = SessionConfig()
        assert config.model_name == "gpt-realtime"
        assert config.voice == "nova"
        assert config.modalities == ["audio"]
        assert config.input_audio_format == "pcm16"
        assert config.output_audio_format == "pcm16"
        assert config.transcription_model == "gpt-4o-mini-transcribe"

    def test_all_valid_voices(self) -> None:
        """Test all valid voice options."""
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer", "ash"]
        for voice in valid_voices:
            config = SessionConfig(voice=voice)
            assert config.voice == voice

    def test_invalid_voice(self) -> None:
        """Test invalid voice raises error."""
        with pytest.raises(ValidationError):
            SessionConfig(voice="invalid_voice")

    def test_all_valid_audio_formats(self) -> None:
        """Test all valid audio format options."""
        valid_formats = ["pcm16", "g711_ulaw", "g711_alaw"]
        for fmt in valid_formats:
            config = SessionConfig(
                input_audio_format=fmt,
                output_audio_format=fmt,
            )
            assert config.input_audio_format == fmt
            assert config.output_audio_format == fmt

    def test_invalid_audio_format(self) -> None:
        """Test invalid audio format raises error."""
        with pytest.raises(ValidationError):
            SessionConfig(input_audio_format="mp3")

    def test_modalities_must_not_be_empty(self) -> None:
        """Test modalities list must not be empty."""
        with pytest.raises(ValidationError):
            SessionConfig(modalities=[])

    def test_multiple_modalities(self) -> None:
        """Test multiple modalities can be specified."""
        config = SessionConfig(modalities=["audio", "text"])
        assert "audio" in config.modalities
        assert "text" in config.modalities

    def test_to_runner_config(self) -> None:
        """Test conversion to runner config format."""
        config = SessionConfig(
            model_name="gpt-realtime",
            voice="nova",
            modalities=["audio"],
        )
        runner_config = config.to_runner_config()

        assert "model_settings" in runner_config
        settings = runner_config["model_settings"]
        assert settings["model_name"] == "gpt-realtime"
        assert settings["voice"] == "nova"
        assert settings["modalities"] == ["audio"]
        assert "turn_detection" in settings
        assert settings["turn_detection"]["type"] == "semantic_vad"

    def test_nested_turn_detection_config(self) -> None:
        """Test nested turn detection configuration."""
        turn_config = TurnDetectionConfig(
            type="server_vad",
            interrupt_response=False,
        )
        config = SessionConfig(turn_detection=turn_config)
        assert config.turn_detection.type == "server_vad"
        assert config.turn_detection.interrupt_response is False
