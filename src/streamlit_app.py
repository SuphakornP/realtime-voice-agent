"""Streamlit-based Speech-to-Speech Voice Agent Demo.

This implements the Speech-to-Speech (S2S) architecture using gpt-4o-realtime-preview
for a ChatGPT-like voice interaction experience.
"""

import base64
import io
import json
import os
import threading
from datetime import datetime
from typing import Any

import numpy as np
import streamlit as st
from audio_recorder_streamlit import audio_recorder

# Load .env file BEFORE importing OpenAI
from dotenv import load_dotenv
load_dotenv()

# Fix SSL certificate verification on macOS
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

from openai import OpenAI

# Audio constants for Realtime API
SAMPLE_RATE = 24000  # 24kHz for OpenAI Realtime API
CHANNELS = 1


def convert_audio_to_pcm16(audio_bytes: bytes) -> bytes:
    """Convert recorded audio (WAV) to PCM16 24kHz mono for OpenAI API."""
    try:
        import soundfile as sf
        import scipy.signal as signal
        
        # Read the audio file
        audio_data, orig_sr = sf.read(io.BytesIO(audio_bytes))
        
        # Convert to mono if stereo
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        # Resample to 24kHz if needed
        if orig_sr != SAMPLE_RATE:
            num_samples = int(len(audio_data) * SAMPLE_RATE / orig_sr)
            audio_data = signal.resample(audio_data, num_samples)
        
        # Convert to PCM16
        audio_data = np.clip(audio_data, -1.0, 1.0)
        audio_data = (audio_data * 32767).astype(np.int16)
        
        return audio_data.tobytes()
    except Exception as e:
        st.error(f"Audio conversion error: {e}")
        return b""


# =============================================================================
# Tool Definitions for Demo
# =============================================================================

def get_current_time() -> dict:
    """Get the current time in Thailand timezone."""
    import pytz
    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz)
    return {
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "timezone": "Asia/Bangkok",
        "formatted": now.strftime("%I:%M %p on %A, %B %d, %Y")
    }


def get_weather(location: str = "Bangkok") -> dict:
    """Get mock weather information for demo purposes."""
    # Mock weather data for demo
    weather_data = {
        "Bangkok": {"temp": 32, "condition": "Sunny", "humidity": 65},
        "Chiang Mai": {"temp": 28, "condition": "Partly Cloudy", "humidity": 55},
        "Phuket": {"temp": 30, "condition": "Scattered Showers", "humidity": 75},
    }
    data = weather_data.get(location, {"temp": 25, "condition": "Unknown", "humidity": 50})
    return {
        "location": location,
        "temperature_celsius": data["temp"],
        "condition": data["condition"],
        "humidity_percent": data["humidity"]
    }


def calculate(expression: str) -> dict:
    """Evaluate a simple mathematical expression."""
    try:
        # Safe evaluation of math expressions
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return {"error": "Invalid characters in expression"}
        result = eval(expression)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": str(e)}


# Tool definitions for the Realtime API
TOOLS = [
    {
        "type": "function",
        "name": "get_current_time",
        "description": "Get the current time and date in Thailand timezone. Use this when the user asks about the time or date.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get weather information for a location in Thailand. Use this when the user asks about weather.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name (e.g., Bangkok, Chiang Mai, Phuket)"
                }
            },
            "required": []
        }
    },
    {
        "type": "function",
        "name": "calculate",
        "description": "Perform a mathematical calculation. Use this when the user asks to calculate something.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate (e.g., '2 + 2', '10 * 5')"
                }
            },
            "required": ["expression"]
        }
    }
]

# Tool execution mapping
TOOL_FUNCTIONS = {
    "get_current_time": get_current_time,
    "get_weather": get_weather,
    "calculate": calculate,
}


# =============================================================================
# Agent Instructions
# =============================================================================

SYSTEM_INSTRUCTIONS = """คุณเป็นผู้ช่วย AI ที่สามารถสื่อสารได้ทั้งภาษาไทยและภาษาอังกฤษ
You are an AI assistant capable of communicating in both Thai and English.

## Language Rules / กฎการใช้ภาษา
- ตอบกลับเป็นภาษาเดียวกับที่ผู้ใช้พูด / Respond in the same language the user speaks
- If the user speaks Thai, respond entirely in Thai
- If the user speaks English, respond in English
- ถ้าผู้ใช้เปลี่ยนภาษา ให้เปลี่ยนตาม / If the user switches languages, switch with them

## Conversation Style / รูปแบบการสนทนา
- Keep responses brief and conversational (this is voice, not text)
- ตอบสั้นๆ และเป็นธรรมชาติ
- Be friendly, helpful, and engaging
- เป็นมิตร ช่วยเหลือ และน่าสนใจ
- Use natural speech patterns - avoid lists, bullet points, or markdown
- ใช้รูปแบบการพูดที่เป็นธรรมชาติ

## Available Tools / เครื่องมือที่มี
- get_current_time: บอกเวลาปัจจุบัน / Tell current time
- get_weather: บอกสภาพอากาศ / Get weather info
- calculate: คำนวณเลข / Do math calculations

## Important Notes / หมายเหตุสำคัญ
- You are a voice assistant - users are speaking to you
- Keep responses concise since they will be spoken aloud
- If you don't understand, politely ask for clarification
"""


# =============================================================================
# Streamlit App
# =============================================================================

def init_session_state():
    """Initialize Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []


def add_message(role: str, content: str, audio_data: bytes | None = None):
    """Add a message to the chat history."""
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "audio": audio_data,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })


def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool and return the result."""
    if name in TOOL_FUNCTIONS:
        try:
            result = TOOL_FUNCTIONS[name](**arguments)
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})
    return json.dumps({"error": f"Unknown tool: {name}"})


def process_audio_with_realtime_api(audio_bytes: bytes) -> tuple[str, bytes | None, list[dict]]:
    """
    Process audio using OpenAI Realtime API (Speech-to-Speech).
    
    This is the core S2S implementation using gpt-4o-realtime-preview.
    The model directly processes audio input and generates audio output.
    
    Returns:
        tuple: (transcript, audio_response, tool_calls)
    """
    import websocket
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Error: OPENAI_API_KEY not set", None, []
    
    # WebSocket URL for Realtime API
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    transcript = ""
    audio_chunks = []
    tool_calls = []
    response_complete = threading.Event()
    
    def on_message(ws, message):
        nonlocal transcript, audio_chunks, tool_calls
        try:
            event = json.loads(message)
            event_type = event.get("type", "")
            
            # Handle different event types
            if event_type == "response.audio_transcript.delta":
                transcript += event.get("delta", "")
            
            elif event_type == "response.audio.delta":
                # Decode base64 audio chunk
                delta = event.get("delta", "")
                if delta:
                    audio_chunks.append(base64.b64decode(delta))
            
            elif event_type == "response.function_call_arguments.done":
                # Tool call completed
                tool_calls.append({
                    "call_id": event.get("call_id"),
                    "name": event.get("name"),
                    "arguments": json.loads(event.get("arguments", "{}"))
                })
            
            elif event_type == "response.done":
                response_complete.set()
            
            elif event_type == "error":
                st.error(f"API Error: {event.get('error', {}).get('message', 'Unknown error')}")
                response_complete.set()
                
        except Exception as e:
            st.error(f"Error processing message: {e}")
    
    def on_error(ws, error):
        st.error(f"WebSocket error: {error}")
        response_complete.set()
    
    def on_close(ws, close_status_code, close_msg):
        response_complete.set()
    
    def on_open(ws):
        # Configure session
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": SYSTEM_INSTRUCTIONS,
                "voice": "coral",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500
                },
                "tools": TOOLS,
                "tool_choice": "auto"
            }
        }
        ws.send(json.dumps(session_config))
        
        # Send audio data
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        ws.send(json.dumps({
            "type": "input_audio_buffer.append",
            "audio": audio_base64
        }))
        
        # Commit the audio buffer and request response
        ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
        ws.send(json.dumps({"type": "response.create"}))
    
    # Create WebSocket connection
    ws = websocket.WebSocketApp(
        url,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # Run WebSocket in a thread
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.start()
    
    # Wait for response with timeout
    response_complete.wait(timeout=30)
    ws.close()
    ws_thread.join(timeout=5)
    
    # Combine audio chunks
    audio_response = b"".join(audio_chunks) if audio_chunks else None
    
    return transcript, audio_response, tool_calls


def handle_tool_calls_and_continue(tool_calls: list[dict], ws_url: str, headers: dict) -> tuple[str, bytes | None]:
    """Handle tool calls and get continued response."""
    import websocket
    
    transcript = ""
    audio_chunks = []
    response_complete = threading.Event()
    
    def on_message(ws, message):
        nonlocal transcript, audio_chunks
        try:
            event = json.loads(message)
            event_type = event.get("type", "")
            
            if event_type == "response.audio_transcript.delta":
                transcript += event.get("delta", "")
            elif event_type == "response.audio.delta":
                delta = event.get("delta", "")
                if delta:
                    audio_chunks.append(base64.b64decode(delta))
            elif event_type == "response.done":
                response_complete.set()
        except Exception as e:
            pass
    
    def on_open(ws):
        # Configure session
        ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": SYSTEM_INSTRUCTIONS,
                "voice": "coral",
                "output_audio_format": "pcm16",
                "tools": TOOLS
            }
        }))
        
        # Send tool results
        for tool_call in tool_calls:
            result = execute_tool(tool_call["name"], tool_call["arguments"])
            ws.send(json.dumps({
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": tool_call["call_id"],
                    "output": result
                }
            }))
        
        # Request response
        ws.send(json.dumps({"type": "response.create"}))
    
    ws = websocket.WebSocketApp(
        ws_url,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_close=lambda ws, code, msg: response_complete.set()
    )
    
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.start()
    response_complete.wait(timeout=30)
    ws.close()
    ws_thread.join(timeout=5)
    
    audio_response = b"".join(audio_chunks) if audio_chunks else None
    return transcript, audio_response


def audio_to_base64(audio_data: bytes) -> str:
    """Convert audio bytes to base64 for HTML audio player."""
    return base64.b64encode(audio_data).decode("utf-8")


def render_audio_player(audio_data: bytes, autoplay: bool = False):
    """Render an HTML audio player for the audio data."""
    audio_b64 = audio_to_base64(audio_data)
    autoplay_attr = "autoplay" if autoplay else ""
    
    # PCM16 needs to be wrapped in WAV format for browser playback
    wav_data = pcm_to_wav(audio_data)
    wav_b64 = base64.b64encode(wav_data).decode("utf-8")
    
    st.markdown(
        f'<audio controls {autoplay_attr} style="width: 100%;"><source src="data:audio/wav;base64,{wav_b64}" type="audio/wav"></audio>',
        unsafe_allow_html=True
    )


def pcm_to_wav(pcm_data: bytes, sample_rate: int = 24000, channels: int = 1, bits_per_sample: int = 16) -> bytes:
    """Convert raw PCM data to WAV format."""
    import struct
    
    # WAV header
    data_size = len(pcm_data)
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + data_size,
        b'WAVE',
        b'fmt ',
        16,  # Subchunk1Size
        1,   # AudioFormat (PCM)
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        data_size
    )
    
    return header + pcm_data


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="🎤 Voice Agent Demo",
        page_icon="🎤",
        layout="wide"
    )
    
    init_session_state()
    
    # Header
    st.title("🎤 Speech-to-Speech Voice Agent")
    st.markdown("""
    **Architecture**: `gpt-4o-realtime-preview` (Direct Speech-to-Speech)
    
    This demo uses OpenAI's Realtime API for direct audio-to-audio processing.
    The model hears your voice and responds with speech - no text intermediary!
    """)
    
    # Sidebar with info
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        ### Speech-to-Speech Architecture
        
        Unlike the chained approach (STT → LLM → TTS), 
        this uses a **single multimodal model** that:
        
        - 🎧 Hears emotion and intent
        - 🧠 Thinks in speech
        - 🔊 Responds directly in voice
        
        ### Available Tools
        - ⏰ **Time**: Ask "What time is it?"
        - 🌤️ **Weather**: Ask about weather
        - 🔢 **Calculator**: Ask to calculate
        
        ### Languages
        - 🇹🇭 Thai
        - 🇬🇧 English
        """)
        
        st.divider()
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat messages
        chat_container = st.container()
        
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    if msg.get("audio"):
                        render_audio_player(msg["audio"])
    
    with col2:
        st.subheader("🎙️ Voice Input")
        
        # =================================================================
        # Option 1: Browser Microphone (Primary)
        # =================================================================
        st.markdown("**🎤 Click to Record**")
        st.caption("Click the microphone icon, speak, then click again to stop.")
        
        # Browser-based audio recorder (works on macOS without crashes)
        audio_bytes = audio_recorder(
            text="",
            recording_color="#e74c3c",
            neutral_color="#3498db",
            icon_name="microphone",
            icon_size="3x",
            pause_threshold=2.0,
            sample_rate=48000,
        )
        
        # Process recorded audio
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            
            if st.button("🚀 Send to AI", type="primary", use_container_width=True):
                with st.spinner("🎧 Processing with gpt-4o-realtime-preview..."):
                    # Convert to PCM16 24kHz
                    pcm_bytes = convert_audio_to_pcm16(audio_bytes)
                    
                    if pcm_bytes:
                        # Process with Realtime API
                        transcript, audio_response, tool_calls = process_audio_with_realtime_api(pcm_bytes)
                        
                        # Add user message
                        if transcript:
                            add_message("user", f"🎤 {transcript}")
                        else:
                            add_message("user", "🎤 [Audio message]")
                        
                        # Handle tool calls if any
                        if tool_calls:
                            tool_info = ", ".join([f"{tc['name']}({tc['arguments']})" for tc in tool_calls])
                            st.info(f"🔧 Tool calls: {tool_info}")
                            
                            for tc in tool_calls:
                                result = execute_tool(tc["name"], tc["arguments"])
                                st.success(f"✅ {tc['name']}: {result}")
                        
                        # Add assistant response
                        if audio_response:
                            add_message("assistant", transcript or "[Voice response]", audio_response)
                            st.success("✅ Response received!")
                        else:
                            add_message("assistant", transcript or "I couldn't generate a response.")
                        
                        st.rerun()
        
        st.divider()
        
        # =================================================================
        # Option 2: File Upload
        # =================================================================
        st.markdown("**📁 Upload Audio File**")
        uploaded_file = st.file_uploader(
            "Upload audio file",
            type=["wav", "mp3", "m4a", "webm"],
            key="audio_upload",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.audio(uploaded_file)
            
            if st.button("🚀 Process Upload", use_container_width=True):
                with st.spinner("🎧 Processing with gpt-4o-realtime-preview..."):
                    # Read and convert audio to PCM16
                    audio_bytes = uploaded_file.read()
                    
                    try:
                        import soundfile as sf
                        import io
                        
                        # Read audio file
                        audio_data, orig_sr = sf.read(io.BytesIO(audio_bytes))
                        
                        # Resample to 24kHz if needed
                        if orig_sr != SAMPLE_RATE:
                            import scipy.signal as signal
                            num_samples = int(len(audio_data) * SAMPLE_RATE / orig_sr)
                            audio_data = signal.resample(audio_data, num_samples)
                        
                        # Convert to mono if stereo
                        if len(audio_data.shape) > 1:
                            audio_data = audio_data.mean(axis=1)
                        
                        # Convert to PCM16
                        audio_data = (audio_data * 32767).astype(np.int16)
                        pcm_bytes = audio_data.tobytes()
                        
                    except ImportError:
                        st.warning("soundfile not installed, using raw audio")
                        pcm_bytes = audio_bytes
                    
                    # Process with Realtime API
                    transcript, audio_response, tool_calls = process_audio_with_realtime_api(pcm_bytes)
                    
                    # Add user message
                    if transcript:
                        add_message("user", f"🎤 {transcript}")
                    else:
                        add_message("user", "🎤 [Audio message]")
                    
                    # Handle tool calls if any
                    if tool_calls:
                        tool_info = ", ".join([f"{tc['name']}({tc['arguments']})" for tc in tool_calls])
                        st.info(f"🔧 Tool calls: {tool_info}")
                        
                        for tc in tool_calls:
                            result = execute_tool(tc["name"], tc["arguments"])
                            st.success(f"✅ {tc['name']}: {result}")
                    
                    # Add assistant response
                    if audio_response:
                        add_message("assistant", transcript or "[Voice response]", audio_response)
                        st.success("✅ Response received!")
                    else:
                        add_message("assistant", transcript or "I couldn't generate a response.")
                    
                    st.rerun()
        
        st.divider()
        
        # =================================================================
        # Option 3: Text Input
        # =================================================================
        st.markdown("**⌨️ Text Input**")
        text_input = st.text_input("Type a message", key="text_input")
        
        if st.button("📤 Send Text"):
            if text_input:
                # For text input, we'll use the regular Chat API
                # and then TTS for audio response
                add_message("user", text_input)
                
                with st.spinner("💭 Thinking..."):
                    client = OpenAI()
                    
                    # Get text response
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                            {"role": "user", "content": text_input}
                        ],
                        tools=[{"type": "function", "function": {k: v for k, v in t.items() if k != "type"}} for t in TOOLS],
                        tool_choice="auto"
                    )
                    
                    assistant_message = response.choices[0].message
                    
                    # Handle tool calls
                    if assistant_message.tool_calls:
                        tool_results = []
                        for tc in assistant_message.tool_calls:
                            result = execute_tool(tc.function.name, json.loads(tc.function.arguments))
                            tool_results.append({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": result
                            })
                            st.info(f"🔧 {tc.function.name}: {result}")
                        
                        # Get final response with tool results
                        messages = [
                            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                            {"role": "user", "content": text_input},
                            assistant_message,
                            *tool_results
                        ]
                        
                        final_response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=messages
                        )
                        response_text = final_response.choices[0].message.content
                    else:
                        response_text = assistant_message.content
                    
                    # Generate TTS
                    tts_response = client.audio.speech.create(
                        model="tts-1",
                        voice="coral",
                        input=response_text,
                        response_format="pcm"
                    )
                    
                    audio_data = tts_response.content
                    add_message("assistant", response_text, audio_data)
                
                st.rerun()
    
    # Footer
    st.divider()
    st.caption("Built with OpenAI Realtime API (gpt-4o-realtime-preview) • Speech-to-Speech Architecture")


if __name__ == "__main__":
    main()
