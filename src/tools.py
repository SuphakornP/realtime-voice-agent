"""Function tools for the voice agent."""

from datetime import datetime
from typing import Any, Literal

import pytz

try:
    from agents import function_tool
except ImportError:
    # Fallback decorator if agents package not available
    def function_tool(func):
        return func

from src.exceptions import ToolExecutionError
from src.logging_config import get_logger

# Thailand timezone
THAILAND_TZ = pytz.timezone("Asia/Bangkok")


def format_time_thai(dt: datetime) -> str:
    """Format datetime in Thai style.

    Args:
        dt: Datetime to format

    Returns:
        Thai formatted time string
    """
    hour = dt.hour
    minute = dt.minute

    return f"{hour}:{minute:02d} น."


def format_time_english(dt: datetime) -> str:
    """Format datetime in English 12-hour style.

    Args:
        dt: Datetime to format

    Returns:
        English formatted time string with AM/PM
    """
    hour = dt.hour
    minute = dt.minute

    if hour == 0:
        display_hour = 12
        period = "AM"
    elif hour < 12:
        display_hour = hour
        period = "AM"
    elif hour == 12:
        display_hour = 12
        period = "PM"
    else:
        display_hour = hour - 12
        period = "PM"

    return f"{display_hour}:{minute:02d} {period}"


def get_current_time(language: str = "th") -> str:
    """Get the current time in Thailand timezone.

    Args:
        language: Language for formatting ("th" for Thai, "en" for English)

    Returns:
        Formatted current time string
    """
    logger = get_logger()

    try:
        now = datetime.now(THAILAND_TZ)

        if language == "th":
            result = format_time_thai(now)
        else:
            result = format_time_english(now)

        logger.debug(f"get_current_time called, result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error getting current time: {e}")
        raise ToolExecutionError(
            message=f"Failed to get current time: {e}",
            details={"language": language},
        ) from e


# Try to import and use the function_tool decorator from agents SDK
try:
    from agents import function_tool

    @function_tool
    def get_current_time_tool() -> str:
        """Get the current time in Thailand timezone.

        Returns the current time formatted appropriately.
        Use this when the user asks what time it is.
        """
        return get_current_time(language="th")

    AVAILABLE_TOOLS = [get_current_time_tool]

except ImportError:
    # Fallback if agents package not installed
    AVAILABLE_TOOLS = [get_current_time]


def get_tools_for_agent() -> list[Any]:
    """Get list of tools to register with the agent.

    Returns:
        List of function tools
    """
    return AVAILABLE_TOOLS


__all__ = [
    "get_current_time",
    "format_time_thai",
    "format_time_english",
    "get_tools_for_agent",
    "AVAILABLE_TOOLS",
]
