"""Shared test fixtures for Voice Agent tests."""

import pytest
from unittest.mock import MagicMock, patch

from src.config import Settings
from src.models.config import SessionConfig, TurnDetectionConfig
from src.models.session import VoiceSession
from src.models import ConnectionState, EventType


@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing."""
    with patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "sk-test-key-12345",
            "VOICE_AGENT_VOICE": "nova",
            "VOICE_AGENT_AUDIO_FORMAT": "pcm16",
            "VOICE_AGENT_VAD_TYPE": "semantic_vad",
            "VOICE_AGENT_LOG_LEVEL": "DEBUG",
        },
    ):
        return Settings()


@pytest.fixture
def sample_turn_detection_config() -> TurnDetectionConfig:
    """Create sample turn detection config."""
    return TurnDetectionConfig(
        type="semantic_vad",
        threshold=0.5,
        silence_duration_ms=500,
        prefix_padding_ms=300,
        interrupt_response=True,
    )


@pytest.fixture
def sample_session_config(
    sample_turn_detection_config: TurnDetectionConfig,
) -> SessionConfig:
    """Create sample session config."""
    return SessionConfig(
        model_name="gpt-realtime",
        voice="nova",
        modalities=["audio"],
        input_audio_format="pcm16",
        output_audio_format="pcm16",
        turn_detection=sample_turn_detection_config,
        transcription_model="gpt-4o-mini-transcribe",
    )


@pytest.fixture
def sample_voice_session() -> VoiceSession:
    """Create sample voice session."""
    return VoiceSession(
        agent_name="Test Voice Assistant",
        connection_state=ConnectionState.CONNECTING,
    )


@pytest.fixture
def active_voice_session() -> VoiceSession:
    """Create an active voice session."""
    session = VoiceSession(
        agent_name="Test Voice Assistant",
        connection_state=ConnectionState.CONNECTING,
    )
    session.transition_to(ConnectionState.CONNECTED)
    session.transition_to(ConnectionState.ACTIVE)
    return session


@pytest.fixture
def sample_audio_data() -> bytes:
    """Create sample PCM16 audio data."""
    # 100ms of silence at 24kHz, 16-bit mono
    sample_rate = 24000
    duration_ms = 100
    num_samples = int(sample_rate * duration_ms / 1000)
    return bytes(num_samples * 2)  # 2 bytes per sample for 16-bit


@pytest.fixture
def mock_realtime_session() -> MagicMock:
    """Create mock RealtimeSession for testing."""
    mock = MagicMock()
    mock.send_audio = MagicMock()
    mock.send_message = MagicMock()
    return mock


@pytest.fixture
def mock_realtime_runner() -> MagicMock:
    """Create mock RealtimeRunner for testing."""
    mock = MagicMock()
    mock.run = MagicMock()
    return mock
