"""Voice Agent using VoicePipeline - based on OpenAI example."""

import asyncio
import curses
import time

import numpy as np
import numpy.typing as npt
import sounddevice as sd

# Load .env file BEFORE importing agents SDK
from dotenv import load_dotenv
load_dotenv()

# Fix SSL certificate verification on macOS
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

from agents import Agent, function_tool
from agents.voice import (
    AudioInput,
    SingleAgentVoiceWorkflow,
    SingleAgentWorkflowCallbacks,
    VoicePipeline,
)


@function_tool
def get_current_time() -> str:
    """Get the current time in Thailand timezone.
    
    Returns the current time. Use this when the user asks what time it is.
    """
    from datetime import datetime
    import pytz
    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz)
    hour = now.hour
    minute = now.minute
    if hour < 12:
        return f"{hour}:{minute:02d} AM (Thailand time)"
    elif hour == 12:
        return f"12:{minute:02d} PM (Thailand time)"
    else:
        return f"{hour-12}:{minute:02d} PM (Thailand time)"


# Thai agent for Thai speakers
thai_agent = Agent(
    name="Thai Assistant",
    handoff_description="A Thai speaking assistant.",
    instructions="""คุณเป็นผู้ช่วยที่พูดภาษาไทย สุภาพและกระชับ
You are a Thai-speaking assistant. Be polite and concise. Respond in Thai.""",
    model="gpt-4o-mini",
)

# Main bilingual agent
agent = Agent(
    name="Voice Assistant",
    instructions="""คุณเป็นผู้ช่วยเสียงที่พูดภาษาไทยเป็นหลัก และสามารถพูดภาษาอังกฤษได้ด้วย

กฎสำคัญ:
- ตอบเป็นภาษาไทยเสมอ ยกเว้นผู้ใช้พูดภาษาอังกฤษชัดเจน
- สุภาพ เป็นมิตร และกระชับ
- สามารถบอกเวลาปัจจุบันได้เมื่อถูกถาม

You are a Thai voice assistant. Always respond in Thai unless the user clearly speaks English.
Be polite, friendly, and concise.""",
    model="gpt-5-mini-2025-08-07",
    handoffs=[thai_agent],
    tools=[get_current_time],
)


class WorkflowCallbacks(SingleAgentWorkflowCallbacks):
    """Callbacks for the voice workflow."""
    
    def on_run(self, workflow: SingleAgentVoiceWorkflow, transcription: str) -> None:
        """Called when transcription is complete."""
        print(f"\n📝 You said: {transcription}")


def _record_audio(screen: curses.window) -> npt.NDArray[np.float32]:
    """Record audio using curses for keyboard control."""
    screen.nodelay(True)
    screen.clear()
    screen.addstr("=" * 50 + "\n")
    screen.addstr("🎤 Thai/English Voice Agent\n")
    screen.addstr("=" * 50 + "\n\n")
    screen.addstr("Press <SPACEBAR> to start recording.\n")
    screen.addstr("Press <SPACEBAR> again to stop and get response.\n")
    screen.addstr("Press 'q' to quit.\n\n")
    screen.refresh()

    recording = False
    audio_buffer: list[npt.NDArray[np.float32]] = []

    def _audio_callback(indata, frames, time_info, status):
        if status:
            pass  # Ignore status messages
        if recording:
            audio_buffer.append(indata.copy())

    # Record at device's native sample rate (48kHz) then resample to 24kHz for API
    with sd.InputStream(samplerate=48000, channels=1, dtype=np.float32, callback=_audio_callback):
        while True:
            key = screen.getch()
            if key == ord(" "):
                recording = not recording
                if recording:
                    audio_buffer.clear()
                    screen.addstr("🔴 Recording... (press SPACEBAR to stop)\n")
                else:
                    screen.addstr("⏹️  Recording stopped. Processing...\n")
                    break
                screen.refresh()
            elif key == ord("q"):
                screen.addstr("👋 Goodbye!\n")
                screen.refresh()
                return np.empty((0,), dtype=np.float32)
            time.sleep(0.01)

    if audio_buffer:
        audio_data = np.concatenate(audio_buffer, axis=0)
        
        # Resample from 48kHz to 24kHz (required by OpenAI API)
        # Simple decimation by factor of 2
        audio_data = audio_data[::2]
        
        # Debug: show audio stats
        duration = len(audio_data) / 24000
        max_val = np.max(np.abs(audio_data))
        screen.addstr(f"📊 Audio: {duration:.1f}s, max amplitude: {max_val:.3f}\n")
        screen.refresh()
        
    else:
        audio_data = np.empty((0,), dtype=np.float32)

    return audio_data


def record_audio() -> npt.NDArray[np.float32]:
    """Record audio with spacebar control."""
    return curses.wrapper(_record_audio)


class AudioPlayer:
    """Audio player for streaming output."""
    
    def __enter__(self):
        self.stream = sd.OutputStream(samplerate=24000, channels=1, dtype=np.int16)
        self.stream.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.stop()
        self.stream.close()

    def add_audio(self, audio_data: npt.NDArray[np.int16]):
        self.stream.write(audio_data)


async def run_voice_agent():
    """Run a single voice interaction."""
    from agents.voice import VoicePipelineConfig, STTModelSettings, TTSModelSettings
    
    # Create pipeline with Thai language support via config
    # Using gpt-4o-transcribe for best accuracy (latest model from OpenAI)
    config = VoicePipelineConfig(
        stt_settings=STTModelSettings(
            language="th",  # Thai language hint for transcription
            # Note: Don't use prompt as it may interfere with actual transcription
        ),
        tts_settings=TTSModelSettings(
            voice="coral",  # Good voice for Thai
        ),
    )
    
    pipeline = VoicePipeline(
        workflow=SingleAgentVoiceWorkflow(agent, callbacks=WorkflowCallbacks()),
        stt_model="gpt-4o-transcribe",  # Latest, most accurate STT model
        config=config,
    )   

    # Record audio
    audio_data = record_audio()
    
    if len(audio_data) == 0:
        return False  # User quit
    
    print("\n🤔 Thinking...")
    
    # Create audio input
    audio_input = AudioInput(buffer=audio_data)

    # Run pipeline
    result = await pipeline.run(audio_input)

    # Play response
    print("🔊 Speaking...")
    with AudioPlayer() as player:
        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                player.add_audio(event.data)
            elif event.type == "voice_stream_event_lifecycle":
                if event.event == "turn_started":
                    pass
                elif event.event == "turn_ended":
                    print("✅ Done")

        # Add silence at the end to avoid cutoff
        player.add_audio(np.zeros(24000 * 1, dtype=np.int16))
    
    return True


async def main():
    """Main entry point."""
    print("\n" + "=" * 50)
    print("🎤 Thai/English Voice Agent")
    print("=" * 50)
    print("\nThis agent can understand and respond in both Thai and English.")
    print("It can also tell you the current time.\n")
    
    while True:
        try:
            should_continue = await run_voice_agent()
            if not should_continue:
                break
            print("\n" + "-" * 50 + "\n")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break


if __name__ == "__main__":
    asyncio.run(main())
