"""Unit tests for logging configuration."""

import pytest
import json
import logging
from unittest.mock import MagicMock, patch

from src.logging_config import (
    JSONFormatter,
    CorrelationLogAdapter,
    setup_logging,
    get_logger,
)


class TestJSONFormatter:
    """Tests for JSONFormatter class."""

    def test_format_returns_json(self) -> None:
        """Test formatter returns valid JSON."""
        formatter = JSONFormatter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should be valid JSON
        parsed = json.loads(result)
        assert "message" in parsed
        assert parsed["message"] == "Test message"

    def test_format_includes_level(self) -> None:
        """Test formatter includes log level."""
        formatter = JSONFormatter()

        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Warning message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        parsed = json.loads(result)

        assert parsed["level"] == "WARNING"

    def test_format_includes_correlation_id(self) -> None:
        """Test formatter includes correlation ID when present."""
        formatter = JSONFormatter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.correlation_id = "test-correlation-123"

        result = formatter.format(record)
        parsed = json.loads(result)

        assert parsed["correlation_id"] == "test-correlation-123"

    def test_format_includes_session_id(self) -> None:
        """Test formatter includes session ID when present."""
        formatter = JSONFormatter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.session_id = "test-session-456"

        result = formatter.format(record)
        parsed = json.loads(result)

        assert parsed["session_id"] == "test-session-456"

    def test_format_includes_event_type(self) -> None:
        """Test formatter includes event type when present."""
        formatter = JSONFormatter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.event_type = "agent_start"

        result = formatter.format(record)
        parsed = json.loads(result)

        assert parsed["event_type"] == "agent_start"


class TestCorrelationLogAdapter:
    """Tests for CorrelationLogAdapter class."""

    def test_adapter_adds_correlation_id(self) -> None:
        """Test adapter adds correlation ID to log records."""
        logger = logging.getLogger("test_adapter")
        adapter = CorrelationLogAdapter(
            logger,
            {"correlation_id": "test-correlation", "session_id": "test-session"},
        )

        msg, kwargs = adapter.process("Test message", {})

        assert "extra" in kwargs
        assert kwargs["extra"]["correlation_id"] == "test-correlation"
        assert kwargs["extra"]["session_id"] == "test-session"


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_returns_logger(self) -> None:
        """Test setup_logging returns a logger."""
        logger = setup_logging(level="INFO")
        assert isinstance(logger, logging.Logger)

    def test_setup_sets_level(self) -> None:
        """Test setup_logging sets correct level."""
        logger = setup_logging(level="DEBUG")
        assert logger.level == logging.DEBUG

        logger = setup_logging(level="WARNING")
        assert logger.level == logging.WARNING


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_adapter(self) -> None:
        """Test get_logger returns a LoggerAdapter."""
        # First setup logging
        setup_logging()

        adapter = get_logger(
            correlation_id="test-correlation",
            session_id="test-session",
        )

        assert isinstance(adapter, logging.LoggerAdapter)

    def test_get_logger_stores_context(self) -> None:
        """Test get_logger stores correlation context."""
        setup_logging()

        adapter = get_logger(
            correlation_id="my-correlation",
            session_id="my-session",
        )

        assert adapter.extra["correlation_id"] == "my-correlation"
        assert adapter.extra["session_id"] == "my-session"
