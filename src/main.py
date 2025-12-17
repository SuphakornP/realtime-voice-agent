"""Main entry point for the Thai/English Voice Agent."""

import argparse
import asyncio
import signal
import ssl
import sys
from typing import NoReturn

# Load .env file BEFORE importing agents SDK
from dotenv import load_dotenv
load_dotenv()

# Fix SSL certificate verification on macOS
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

from agents.realtime import RealtimeAgent, RealtimeRunner

from src.agent import create_realtime_agent
from src.audio import AudioInputStream, AudioOutputStream, list_audio_devices
from src.config import Settings, get_settings
from src.events import EventHandler
from src.exceptions import VoiceAgentError
from src.logging_config import setup_logging, get_logger
from src.models.config import SessionConfig
from src.models.session import VoiceSession
from src.models import ConnectionState


class VoiceAgentApp:
    """Main application class for the voice agent."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the voice agent application.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self._running = False
        self._shutdown_event = asyncio.Event()

        # Setup logging
        setup_logging(
            level=settings.log_level,
            log_file=settings.log_file,
            use_json=True,
        )
        self._logger = get_logger()

    async def run(self) -> None:
        """Run the voice agent."""
        self._running = True

        # Create agent
        agent = create_realtime_agent()
        self._logger.info(f"Created agent: {agent.name}")

        # Create session config
        session_config = SessionConfig(
            voice=self.settings.voice,
            input_audio_format=self.settings.audio_format,
            output_audio_format=self.settings.audio_format,
        )
        session_config.turn_detection.type = self.settings.vad_type

        # Create voice session for tracking
        voice_session = VoiceSession(
            agent_name=agent.name,
        )

        try:
            # Build runner config
            runner_config = session_config.to_runner_config()

            self._logger.info(
                "Initializing voice session",
                extra={
                    "event_type": "session_init",
                    "payload": {"agent_name": agent.name, "config": runner_config},
                },
            )

            # Create runner
            runner = RealtimeRunner(
                starting_agent=agent,
                config=runner_config,
            )

            voice_session.transition_to(ConnectionState.CONNECTED)

            # Start the session and use async with to keep it alive
            session = await runner.run()

            voice_session.transition_to(ConnectionState.ACTIVE)

            self._logger.info(
                "Voice session active",
                extra={
                    "event_type": "session_active",
                    "payload": {"session_id": voice_session.session_id},
                },
            )

            # Use async with to keep the session connection alive
            async with session:
                # Setup audio streams
                audio_input = AudioInputStream(
                    device=self.settings.input_device,
                    correlation_id=voice_session.correlation_id,
                )
                audio_output = AudioOutputStream(
                    device=self.settings.output_device,
                    correlation_id=voice_session.correlation_id,
                )

                # Setup event handler
                event_handler = EventHandler(
                    session_id=voice_session.session_id,
                    correlation_id=voice_session.correlation_id,
                    on_audio_output=audio_output.play,
                    on_audio_interrupted=audio_output.clear,
                )

                # Start audio streams
                audio_input.start()
                audio_output.start()

                print("\n" + "=" * 50)
                print("🎤 Voice Agent Ready!")
                print("=" * 50)
                print("Speak in Thai or English. Press Ctrl+C to exit.")
                print("=" * 50 + "\n")

                try:
                    # Main event loop - runs inside async with session
                    await self._event_loop(
                        session,
                        voice_session,
                        audio_input,
                        audio_output,
                        event_handler,
                    )
                finally:
                    # Cleanup audio streams
                    audio_input.stop()
                    audio_output.stop()

            # Session closed after exiting async with
            voice_session.transition_to(ConnectionState.CLOSING)
            voice_session.transition_to(ConnectionState.CLOSED)

            self._logger.info(
                "Voice session closed",
                extra={
                    "event_type": "session_closed",
                    "payload": {
                        "session_id": voice_session.session_id,
                        "duration_seconds": voice_session.duration_seconds(),
                    },
                },
            )

        except VoiceAgentError as e:
            self._logger.error(f"Voice agent error: {e.message}", extra={"payload": e.to_dict()})
            print(f"\n❌ Error: {e.message}")
            sys.exit(1)

        except Exception as e:
            self._logger.error(f"Unexpected error: {e}")
            print(f"\n❌ Unexpected error: {e}")
            sys.exit(1)

        finally:
            self._running = False

    async def _event_loop(
        self,
        session,
        voice_session: VoiceSession,
        audio_input: AudioInputStream,
        audio_output: AudioOutputStream,
        event_handler: EventHandler,
    ) -> None:
        """Main event loop for processing audio and events.

        Args:
            session: The active RealtimeSession (inside async with context)
            voice_session: The VoiceSession tracking object
            audio_input: Audio input stream
            audio_output: Audio output stream
            event_handler: Event handler instance
        """
        # Create tasks for input and event processing
        input_task = asyncio.create_task(
            self._process_audio_input(session, audio_input)
        )
        event_task = asyncio.create_task(
            self._process_events(session, event_handler)
        )
        shutdown_task = asyncio.create_task(self._shutdown_event.wait())

        # Wait for shutdown or error
        done, pending = await asyncio.wait(
            [input_task, event_task, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Cancel pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def _process_audio_input(
        self,
        session,
        audio_input: AudioInputStream,
    ) -> None:
        """Process audio input and send to session.

        Args:
            session: The active RealtimeSession
            audio_input: Audio input stream
        """
        chunks_sent = 0
        while self._running and not self._shutdown_event.is_set():
            audio_data = await audio_input.get_audio_async(timeout=0.1)
            if audio_data:
                await session.send_audio(audio_data)
                chunks_sent += 1
                if chunks_sent % 50 == 0:
                    self._logger.info(f"Audio chunks sent: {chunks_sent}")

    async def _process_events(
        self,
        session,
        event_handler: EventHandler,
    ) -> None:
        """Process events from the realtime session.

        Args:
            session: The active RealtimeSession
            event_handler: Event handler instance
        """
        event_count = 0
        async for event in session:
            if self._shutdown_event.is_set():
                break
            event_count += 1
            event_type = getattr(event, "type", type(event).__name__)
            if event_count <= 10 or event_count % 50 == 0:
                self._logger.info(f"Event #{event_count}: {event_type}")
            await event_handler.handle_event(event)

    def shutdown(self) -> None:
        """Signal shutdown of the voice agent."""
        print("\n\n👋 Shutting down...")
        self._running = False
        self._shutdown_event.set()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Thai/English Realtime Voice Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--voice",
        choices=["alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse", "marin", "cedar"],
        help="Voice selection for agent responses",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    parser.add_argument(
        "--input-device",
        type=int,
        help="Input audio device index",
    )

    parser.add_argument(
        "--output-device",
        type=int,
        help="Output audio device index",
    )

    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio devices and exit",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Handle --list-devices
    if args.list_devices:
        print("\nAvailable Audio Devices:")
        print("-" * 60)
        for device in list_audio_devices():
            device_type = []
            if device["is_input"]:
                device_type.append("INPUT")
            if device["is_output"]:
                device_type.append("OUTPUT")

            print(f"[{device['index']}] {device['name']}")
            print(f"    Type: {', '.join(device_type)}")
            print(f"    Sample Rate: {device['default_sample_rate']} Hz")
            print()
        return

    # Load settings
    try:
        settings = get_settings()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("Make sure OPENAI_API_KEY is set in .env or environment")
        sys.exit(1)

    # Override settings with CLI args
    if args.voice:
        settings.voice = args.voice
    if args.log_level:
        settings.log_level = args.log_level
    if args.input_device is not None:
        settings.input_device = args.input_device
    if args.output_device is not None:
        settings.output_device = args.output_device

    # Create and run app
    app = VoiceAgentApp(settings)

    # Setup signal handlers
    def signal_handler(sig, frame):
        app.shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the app
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        pass

    print("✅ Voice agent stopped")


if __name__ == "__main__":
    main()
