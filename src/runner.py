"""RealtimeRunner setup and session management."""

import asyncio
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, AsyncIterator

from src.config import Settings, get_settings
from src.exceptions import ConfigValidationError, SessionInitError
from src.logging_config import get_logger
from src.models import ConnectionState
from src.models.config import SessionConfig
from src.models.session import VoiceSession

if TYPE_CHECKING:
    from agents.realtime import RealtimeAgent, RealtimeRunner, RealtimeSession


def build_runner_config(
    settings: Settings,
    session_config: SessionConfig | None = None,
) -> dict[str, Any]:
    """Build configuration dictionary for RealtimeRunner.

    Args:
        settings: Application settings
        session_config: Optional session configuration

    Returns:
        Configuration dictionary for RealtimeRunner
    """
    if session_config is None:
        session_config = SessionConfig(
            voice=settings.voice,
            input_audio_format=settings.audio_format,
            output_audio_format=settings.audio_format,
        )
        session_config.turn_detection.type = settings.vad_type

    # Return config dict directly - RealtimeRunner expects config=RealtimeRunConfig
    # which is a TypedDict with model_settings key
    return session_config.to_runner_config()


def validate_config(settings: Settings) -> None:
    """Validate configuration before starting session.

    Args:
        settings: Application settings

    Raises:
        ConfigValidationError: If configuration is invalid
    """
    if not settings.openai_api_key:
        raise ConfigValidationError(
            message="OpenAI API key is required",
            details={"field": "openai_api_key"},
        )

    if not settings.openai_api_key.startswith("sk-"):
        raise ConfigValidationError(
            message="OpenAI API key appears to be invalid",
            details={"field": "openai_api_key", "hint": "Key should start with 'sk-'"},
        )


async def create_session(
    agent: "RealtimeAgent",
    settings: Settings | None = None,
    session_config: SessionConfig | None = None,
) -> tuple["RealtimeSession", VoiceSession]:
    """Create and initialize a voice session.

    Args:
        agent: The RealtimeAgent to use
        settings: Application settings (uses defaults if not provided)
        session_config: Session configuration (uses defaults if not provided)

    Returns:
        Tuple of (RealtimeSession, VoiceSession)

    Raises:
        SessionInitError: If session initialization fails
    """
    from agents.realtime import RealtimeRunner

    if settings is None:
        settings = get_settings()

    validate_config(settings)

    # Create voice session for tracking
    voice_session = VoiceSession(
        agent_name=agent.name,
        correlation_id=str(uuid.uuid4()),
    )

    logger = get_logger(
        correlation_id=voice_session.correlation_id,
        session_id=voice_session.session_id,
    )

    try:
        # Build runner configuration
        runner_config = build_runner_config(settings, session_config)

        logger.info(
            "Initializing voice session",
            extra={
                "event_type": "session_init",
                "payload": {"agent_name": agent.name, "config": runner_config},
            },
        )

        # Create runner and session
        # RealtimeRunner expects: starting_agent and config=RealtimeRunConfig (TypedDict with model_settings)
        runner = RealtimeRunner(
            starting_agent=agent,
            config=runner_config,
        )

        voice_session.transition_to(ConnectionState.CONNECTED)

        # Run the session
        realtime_session = await runner.run()

        voice_session.transition_to(ConnectionState.ACTIVE)

        logger.info(
            "Voice session active",
            extra={
                "event_type": "session_active",
                "payload": {"session_id": voice_session.session_id},
            },
        )

        return realtime_session, voice_session

    except Exception as e:
        voice_session.transition_to(ConnectionState.CLOSED)
        raise SessionInitError(
            message=f"Failed to initialize session: {e}",
            details={"error": str(e)},
            correlation_id=voice_session.correlation_id,
        ) from e


async def close_session(
    realtime_session: "RealtimeSession",
    voice_session: VoiceSession,
) -> None:
    """Close a voice session gracefully.

    Args:
        realtime_session: The active RealtimeSession
        voice_session: The VoiceSession tracking object
    """
    logger = get_logger(
        correlation_id=voice_session.correlation_id,
        session_id=voice_session.session_id,
    )

    try:
        voice_session.transition_to(ConnectionState.CLOSING)

        logger.info(
            "Closing voice session",
            extra={
                "event_type": "session_closing",
                "payload": {"session_id": voice_session.session_id},
            },
        )

        # Close the realtime session
        if hasattr(realtime_session, "close"):
            await realtime_session.close()

        voice_session.transition_to(ConnectionState.CLOSED)

        duration = voice_session.duration_seconds()
        logger.info(
            "Voice session closed",
            extra={
                "event_type": "session_closed",
                "payload": {
                    "session_id": voice_session.session_id,
                    "duration_seconds": duration,
                },
            },
        )

    except Exception as e:
        logger.error(
            f"Error closing session: {e}",
            extra={
                "event_type": "session_close_error",
                "payload": {"error": str(e)},
            },
        )
        # Force close
        voice_session.connection_state = ConnectionState.CLOSED
        voice_session.end_time = datetime.now()


__all__ = [
    "build_runner_config",
    "validate_config",
    "create_session",
    "close_session",
]
