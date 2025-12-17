"""Logging configuration with JSON formatter and correlation ID support."""

import json
import logging
import sys
from datetime import datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """JSON log formatter with correlation ID support."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add correlation ID if present
        if hasattr(record, "correlation_id") and record.correlation_id:
            log_data["correlation_id"] = record.correlation_id

        # Add session ID if present
        if hasattr(record, "session_id") and record.session_id:
            log_data["session_id"] = record.session_id

        # Add event type if present
        if hasattr(record, "event_type") and record.event_type:
            log_data["event_type"] = record.event_type

        # Add extra payload if present
        if hasattr(record, "payload") and record.payload:
            log_data["payload"] = record.payload

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class CorrelationLogAdapter(logging.LoggerAdapter):
    """Logger adapter that adds correlation ID to all log messages."""

    def process(
        self, msg: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Add correlation ID to log record."""
        extra = kwargs.get("extra", {})
        extra["correlation_id"] = self.extra.get("correlation_id")
        extra["session_id"] = self.extra.get("session_id")
        kwargs["extra"] = extra
        return msg, kwargs


def setup_logging(
    level: str = "INFO",
    log_file: str | None = None,
    use_json: bool = True,
) -> logging.Logger:
    """Configure logging for the voice agent.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output
        use_json: Whether to use JSON formatting

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("voice_agent")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create formatter
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(
    correlation_id: str | None = None,
    session_id: str | None = None,
) -> logging.LoggerAdapter:
    """Get a logger adapter with correlation context.

    Args:
        correlation_id: Request tracing ID
        session_id: Voice session ID

    Returns:
        Logger adapter with context
    """
    logger = logging.getLogger("voice_agent")
    return CorrelationLogAdapter(
        logger,
        {"correlation_id": correlation_id, "session_id": session_id},
    )


__all__ = [
    "JSONFormatter",
    "CorrelationLogAdapter",
    "setup_logging",
    "get_logger",
]
