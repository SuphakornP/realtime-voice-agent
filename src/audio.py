"""Audio input/output handling using sounddevice."""

import asyncio
import queue
import threading
from typing import Callable

import numpy as np
import sounddevice as sd

from src.exceptions import AudioDeviceError
from src.logging_config import get_logger


# Audio constants
SAMPLE_RATE = 24000  # 24kHz for OpenAI Realtime API
CHANNELS = 1  # Mono
DTYPE = np.int16  # 16-bit PCM
CHUNK_DURATION_MS = 100  # 100ms chunks
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000)


class AudioInputStream:
    """Handles audio input from microphone."""

    def __init__(
        self,
        device: int | None = None,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
        chunk_size: int = CHUNK_SIZE,
        correlation_id: str | None = None,
    ) -> None:
        """Initialize audio input stream.

        Args:
            device: Input device index (None for default)
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            chunk_size: Samples per chunk
            correlation_id: Correlation ID for logging
        """
        self.device = device
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.correlation_id = correlation_id

        self._stream: sd.InputStream | None = None
        self._queue: queue.Queue[bytes] = queue.Queue()
        self._running = False
        self._logger = get_logger(correlation_id=correlation_id)

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: dict,
        status: sd.CallbackFlags,
    ) -> None:
        """Callback for audio input stream."""
        if status:
            self._logger.warning(f"Audio input status: {status}")

        if self._running:
            # Convert to bytes and add to queue
            audio_bytes = indata.tobytes()
            self._queue.put(audio_bytes)

    def start(self) -> None:
        """Start the audio input stream."""
        if self._running:
            return

        try:
            self._stream = sd.InputStream(
                device=self.device,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=DTYPE,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
            )
            self._stream.start()
            self._running = True
            self._logger.info("Audio input stream started")

        except Exception as e:
            raise AudioDeviceError(
                message=f"Failed to start audio input: {e}",
                details={"device": self.device},
                correlation_id=self.correlation_id,
            ) from e

    def stop(self) -> None:
        """Stop the audio input stream."""
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            self._logger.info("Audio input stream stopped")

    def get_audio(self, timeout: float = 0.1) -> bytes | None:
        """Get audio data from the queue.

        Args:
            timeout: Timeout in seconds

        Returns:
            Audio bytes or None if queue is empty
        """
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    async def get_audio_async(self, timeout: float = 0.1) -> bytes | None:
        """Get audio data asynchronously.

        Args:
            timeout: Timeout in seconds

        Returns:
            Audio bytes or None if queue is empty
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_audio, timeout)

    @property
    def is_running(self) -> bool:
        """Check if stream is running."""
        return self._running


class AudioOutputStream:
    """Handles audio output to speakers."""

    def __init__(
        self,
        device: int | None = None,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
        correlation_id: str | None = None,
    ) -> None:
        """Initialize audio output stream.

        Args:
            device: Output device index (None for default)
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            correlation_id: Correlation ID for logging
        """
        self.device = device
        self.sample_rate = sample_rate
        self.channels = channels
        self.correlation_id = correlation_id

        self._queue: queue.Queue[bytes] = queue.Queue()
        self._stream: sd.OutputStream | None = None
        self._running = False
        self._logger = get_logger(correlation_id=correlation_id)

    def _audio_callback(
        self,
        outdata: np.ndarray,
        frames: int,
        time_info: dict,
        status: sd.CallbackFlags,
    ) -> None:
        """Callback for audio output stream."""
        if status:
            self._logger.warning(f"Audio output status: {status}")

        try:
            data = self._queue.get_nowait()
            audio_array = np.frombuffer(data, dtype=DTYPE)

            # Pad or truncate to match frame size
            if len(audio_array) < frames:
                audio_array = np.pad(audio_array, (0, frames - len(audio_array)))
            elif len(audio_array) > frames:
                audio_array = audio_array[:frames]

            outdata[:, 0] = audio_array

        except queue.Empty:
            # Output silence if no data available
            outdata.fill(0)

    def start(self) -> None:
        """Start the audio output stream."""
        if self._running:
            return

        try:
            self._stream = sd.OutputStream(
                device=self.device,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=DTYPE,
                blocksize=CHUNK_SIZE,
                callback=self._audio_callback,
            )
            self._stream.start()
            self._running = True
            self._logger.info("Audio output stream started")

        except Exception as e:
            raise AudioDeviceError(
                message=f"Failed to start audio output: {e}",
                details={"device": self.device},
                correlation_id=self.correlation_id,
            ) from e

    def stop(self) -> None:
        """Stop the audio output stream."""
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            self._logger.info("Audio output stream stopped")

    def play(self, audio_data: bytes) -> None:
        """Add audio data to playback queue.

        Args:
            audio_data: PCM16 audio bytes
        """
        if self._running:
            self._queue.put(audio_data)

    def clear(self) -> None:
        """Clear the playback queue (for interruption handling)."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
        self._logger.debug("Audio playback queue cleared")

    @property
    def is_running(self) -> bool:
        """Check if stream is running."""
        return self._running

    @property
    def queue_size(self) -> int:
        """Get current queue size."""
        return self._queue.qsize()


def list_audio_devices() -> list[dict]:
    """List available audio devices.

    Returns:
        List of device information dictionaries
    """
    devices = sd.query_devices()
    result = []

    for i, device in enumerate(devices):
        result.append({
            "index": i,
            "name": device["name"],
            "max_input_channels": device["max_input_channels"],
            "max_output_channels": device["max_output_channels"],
            "default_sample_rate": device["default_samplerate"],
            "is_input": device["max_input_channels"] > 0,
            "is_output": device["max_output_channels"] > 0,
        })

    return result


def get_default_devices() -> tuple[int | None, int | None]:
    """Get default input and output device indices.

    Returns:
        Tuple of (input_device_index, output_device_index)
    """
    try:
        default_input = sd.default.device[0]
        default_output = sd.default.device[1]
        return default_input, default_output
    except Exception:
        return None, None


__all__ = [
    "AudioInputStream",
    "AudioOutputStream",
    "list_audio_devices",
    "get_default_devices",
    "SAMPLE_RATE",
    "CHANNELS",
    "CHUNK_SIZE",
    "CHUNK_DURATION_MS",
]
