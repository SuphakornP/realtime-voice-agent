"""Event handlers for voice session events."""

from datetime import datetime
from typing import Any, Callable

from src.logging_config import get_logger
from src.models import EventType
from src.models.events import SessionEvent


class EventHandler:
    """Handles events from the voice session."""

    def __init__(
        self,
        session_id: str,
        correlation_id: str,
        on_audio_output: Callable[[bytes], None] | None = None,
        on_audio_interrupted: Callable[[], None] | None = None,
    ) -> None:
        """Initialize event handler.

        Args:
            session_id: Voice session ID
            correlation_id: Correlation ID for logging
            on_audio_output: Callback for audio output data
            on_audio_interrupted: Callback when audio is interrupted
        """
        self.session_id = session_id
        self.correlation_id = correlation_id
        self.on_audio_output = on_audio_output
        self.on_audio_interrupted = on_audio_interrupted

        self._logger = get_logger(
            correlation_id=correlation_id,
            session_id=session_id,
        )

        # Metrics tracking
        self._audio_chunk_count = 0
        self._total_audio_duration_ms = 0
        self._session_start_time = datetime.now()

    def _create_event(
        self,
        event_type: EventType,
        payload: dict[str, Any] | None = None,
    ) -> SessionEvent:
        """Create a session event."""
        return SessionEvent(
            session_id=self.session_id,
            event_type=event_type,
            payload=payload or {},
            correlation_id=self.correlation_id,
        )

    def _log_event(self, event: SessionEvent) -> None:
        """Log a session event."""
        self._logger.info(
            f"Event: {event.event_type.value}",
            extra={
                "event_type": event.event_type.value,
                "payload": event.payload,
            },
        )

    async def handle_event(self, event: Any) -> None:
        """Handle an event from the realtime session.

        Args:
            event: Event from RealtimeSession
        """
        event_type_str = getattr(event, "type", str(type(event).__name__))

        # Map SDK event types to handlers
        if event_type_str == "agent_start":
            agent = getattr(event, "agent", None)
            agent_name = getattr(agent, "name", "Unknown") if agent else "Unknown"
            self._logger.info(f"Agent started: {agent_name}")
        
        elif event_type_str == "agent_end":
            agent = getattr(event, "agent", None)
            agent_name = getattr(agent, "name", "Unknown") if agent else "Unknown"
            self._logger.info(f"Agent ended: {agent_name}")
        
        elif event_type_str == "audio":
            # This is the main audio event from the SDK
            audio_data = getattr(event, "data", None)
            if audio_data and self.on_audio_output:
                self._audio_chunk_count += 1
                # Audio data should be raw bytes
                if isinstance(audio_data, (bytes, bytearray)):
                    self.on_audio_output(bytes(audio_data))
                elif hasattr(audio_data, "tobytes"):
                    self.on_audio_output(audio_data.tobytes())
                
                if self._audio_chunk_count % 20 == 0:
                    self._logger.info(f"Playing audio chunk #{self._audio_chunk_count}")
        
        elif event_type_str == "audio_end":
            self._logger.info(f"Audio ended, total chunks: {self._audio_chunk_count}")
            self._audio_chunk_count = 0
        
        elif event_type_str == "audio_interrupted":
            self._logger.info("Audio interrupted")
            if self.on_audio_interrupted:
                self.on_audio_interrupted()
            self._audio_chunk_count = 0
        
        elif event_type_str == "tool_start":
            tool = getattr(event, "tool", None)
            tool_name = getattr(tool, "name", "unknown") if tool else "unknown"
            self._logger.info(f"Tool started: {tool_name}")
        
        elif event_type_str == "tool_end":
            tool = getattr(event, "tool", None)
            tool_name = getattr(tool, "name", "unknown") if tool else "unknown"
            output = getattr(event, "output", None)
            self._logger.info(f"Tool ended: {tool_name}, output: {output}")
        
        elif event_type_str == "error":
            error = getattr(event, "error", event)
            self._logger.error(f"Error event: {error}")
        
        elif event_type_str == "handoff":
            from_agent = getattr(event, "from_agent", None)
            to_agent = getattr(event, "to_agent", None)
            self._logger.info(f"Handoff: {getattr(from_agent, 'name', '?')} -> {getattr(to_agent, 'name', '?')}")
        
        elif event_type_str in ["history_updated", "history_added"]:
            # Skip these frequent events
            pass
        
        elif event_type_str == "raw_model_event":
            # Handle raw model events from the Realtime API
            # The structure is: event.data.data (dict with 'type' and other fields)
            try:
                data = getattr(event, "data", None)
                if not data:
                    return
                    
                nested = getattr(data, "data", None)
                if not nested:
                    return
                
                # Handle dict or object
                if isinstance(nested, dict):
                    evt_type = nested.get("type", "")
                else:
                    evt_type = getattr(nested, "type", "")
                
                # Speech detection
                if evt_type == "input_audio_buffer.speech_started":
                    self._logger.info("🎤 Speech detected...")
                elif evt_type == "input_audio_buffer.speech_stopped":
                    self._logger.info("🎤 Speech ended, processing...")
                
                # Response events
                elif evt_type == "response.created":
                    self._logger.info("💭 Generating response...")
                elif evt_type == "response.done":
                    self._logger.info("✅ Response complete")
                
                # Audio output
                elif evt_type == "response.audio.delta":
                    delta = nested.get("delta", "") if isinstance(nested, dict) else getattr(nested, "delta", "")
                    if delta and self.on_audio_output:
                        import base64
                        decoded = base64.b64decode(delta)
                        self.on_audio_output(decoded)
                        self._audio_chunk_count += 1
                        if self._audio_chunk_count == 1:
                            self._logger.info("🔊 Playing audio response...")
                
                elif evt_type == "response.audio.done":
                    if self._audio_chunk_count > 0:
                        self._logger.info(f"🔊 Audio complete ({self._audio_chunk_count} chunks)")
                    self._audio_chunk_count = 0
                    
            except Exception as e:
                self._logger.debug(f"Error parsing raw event: {e}")

    async def _handle_agent_start(self, event: Any) -> None:
        """Handle agent start event."""
        agent_name = getattr(event, "agent_name", "Unknown")
        session_event = self._create_event(
            EventType.AGENT_START,
            {"agent_name": agent_name},
        )
        self._log_event(session_event)

    async def _handle_agent_end(self, event: Any) -> None:
        """Handle agent end event."""
        reason = getattr(event, "reason", "completed")
        session_event = self._create_event(
            EventType.AGENT_END,
            {"reason": reason},
        )
        self._log_event(session_event)

    async def _handle_audio(self, event: Any) -> None:
        """Handle audio output event."""
        audio_data = getattr(event, "data", None) or getattr(event, "audio", None)

        self._audio_chunk_count += 1

        # Debug: Log audio data info
        self._logger.info(
            f"Audio chunk #{self._audio_chunk_count}: data={type(audio_data).__name__}, size={len(audio_data) if audio_data else 0}",
            extra={
                "event_type": "audio_debug",
                "payload": {"chunk": self._audio_chunk_count, "has_data": audio_data is not None},
            },
        )

        if audio_data and self.on_audio_output:
            # Convert to bytes if needed
            if isinstance(audio_data, (bytes, bytearray)):
                self.on_audio_output(bytes(audio_data))
            elif hasattr(audio_data, "tobytes"):
                self.on_audio_output(audio_data.tobytes())
            else:
                self._logger.warning(f"Unknown audio data type: {type(audio_data)}")

    async def _handle_audio_end(self, event: Any) -> None:
        """Handle audio end event."""
        session_event = self._create_event(
            EventType.AUDIO_END,
            {
                "total_chunks": self._audio_chunk_count,
            },
        )
        self._log_event(session_event)
        # Reset chunk count for next response
        self._audio_chunk_count = 0

    async def _handle_audio_interrupted(self, event: Any) -> None:
        """Handle audio interrupted event."""
        session_event = self._create_event(
            EventType.AUDIO_INTERRUPTED,
            {"chunks_at_interrupt": self._audio_chunk_count},
        )
        self._log_event(session_event)

        # Call interrupt callback
        if self.on_audio_interrupted:
            self.on_audio_interrupted()

        # Reset chunk count
        self._audio_chunk_count = 0

    async def _handle_tool_start(self, event: Any) -> None:
        """Handle tool start event."""
        tool_name = getattr(event, "tool_name", getattr(event, "name", "unknown"))
        arguments = getattr(event, "arguments", {})
        session_event = self._create_event(
            EventType.TOOL_START,
            {"tool_name": tool_name, "arguments": arguments},
        )
        self._log_event(session_event)

    async def _handle_tool_end(self, event: Any) -> None:
        """Handle tool end event."""
        tool_name = getattr(event, "tool_name", getattr(event, "name", "unknown"))
        result = getattr(event, "result", None)
        success = getattr(event, "success", True)
        session_event = self._create_event(
            EventType.TOOL_END,
            {"tool_name": tool_name, "result": str(result), "success": success},
        )
        self._log_event(session_event)

    async def _handle_error(self, event: Any) -> None:
        """Handle error event."""
        error_code = getattr(event, "code", "UNKNOWN_ERROR")
        error_message = getattr(event, "message", str(event))
        session_event = self._create_event(
            EventType.ERROR,
            {"code": error_code, "message": error_message},
        )
        self._logger.error(
            f"Error event: {error_message}",
            extra={
                "event_type": "error",
                "payload": {"code": error_code, "message": error_message},
            },
        )


__all__ = ["EventHandler"]
