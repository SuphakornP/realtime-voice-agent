# Thai/English Realtime Voice Agent POC

A real-time voice-enabled AI agent using OpenAI's Agents SDK with support for **Thai and English languages**.

## Features

- 🎤 **Real-time voice conversations** - Natural speech-to-speech interaction
- 🇹🇭 **Thai language support** - Full Thai speech recognition and response
- 🇬🇧 **English language support** - Seamless English conversations
- 🔄 **Language switching** - Automatically detects and responds in the user's language
- ⚡ **Low latency** - <500ms response time target
- 🛑 **Interruption handling** - Interrupt the agent naturally while it's speaking
- 🔧 **Tool execution** - Execute functions during conversations (e.g., get current time)
- 📝 **Comprehensive logging** - JSON-formatted logs with correlation IDs

## Prerequisites

- **Python 3.11+**
- **Microphone and speakers/headphones**
- **OpenAI API key** with realtime model access
- **macOS or Linux** (Windows with WSL2)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd realtime-voice-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

## Configuration

Create a `.env` file with the following variables:

```bash
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional (for src.main only)
VOICE_AGENT_VOICE=ash           # Voice: alloy, ash, ballad, coral, echo, sage, shimmer, verse
VOICE_AGENT_AUDIO_FORMAT=pcm16  # Format: pcm16, g711_ulaw, g711_alaw
VOICE_AGENT_VAD_TYPE=semantic_vad  # VAD: server_vad, semantic_vad
VOICE_AGENT_LOG_LEVEL=INFO      # Level: DEBUG, INFO, WARNING, ERROR
```

## Usage

### Start the Voice Agent (Recommended)

Use `voice_main.py` for the best Thai language support with the latest OpenAI models:

```bash
python -m src.voice_main
```

**Controls:**
- Press **SPACEBAR** to start recording
- Press **SPACEBAR** again to stop and get response
- Press **'q'** to quit

### Example Session

```
$ python -m src.voice_main

==================================================
🎤 Thai/English Voice Agent
==================================================

Press <SPACEBAR> to start recording.
Press <SPACEBAR> again to stop and get response.
Press 'q' to quit.

🔴 Recording... (press SPACEBAR to stop)
⏹️  Recording stopped. Processing...
📊 Audio: 2.5s, max amplitude: 0.342

🤔 Thinking...
🔊 Speaking...

📝 You said: สวัสดีครับ ตอนนี้กี่โมง
✅ Done

--------------------------------------------------

👋 Goodbye!
```

### Alternative: Realtime Streaming Mode

For continuous conversation mode (experimental):

```bash
python -m src.main
```

### Command Line Options (src.main only)

```bash
python -m src.main --help

Options:
  --voice {alloy,ash,ballad,coral,echo,sage,shimmer,verse}
                        Voice selection for agent responses
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Logging level
  --input-device INT    Input audio device index
  --output-device INT   Output audio device index
  --list-devices        List available audio devices and exit
```

### List Audio Devices

```bash
python -m src.main --list-devices
```

## Project Structure

```
realtime-voice-agent/
├── src/
│   ├── __init__.py          # Package metadata
│   ├── voice_main.py        # ⭐ Recommended entry point (VoicePipeline)
│   ├── main.py              # Alternative entry point (RealtimeRunner)
│   ├── agent.py             # RealtimeAgent configuration
│   ├── runner.py            # Session management
│   ├── audio.py             # Audio I/O handling
│   ├── events.py            # Event handlers
│   ├── tools.py             # Function tools
│   ├── config.py            # Settings
│   ├── exceptions.py        # Custom exceptions
│   ├── logging_config.py    # Logging setup
│   └── models/
│       ├── __init__.py      # Enums
│       ├── config.py        # Config models
│       ├── session.py       # Session model
│       ├── events.py        # Event model
│       ├── audio.py         # Audio model
│       ├── conversation.py  # Turn model
│       └── tools.py         # Tool model
├── tests/
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── specs/                   # Feature specifications
├── documents/               # PRD and documentation
├── requirements.txt         # Dependencies
├── pyproject.toml          # Project config
└── README.md               # This file
```

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v
```

## Available Tools

| Tool | Description | Trigger Examples |
|------|-------------|------------------|
| `get_current_time` | Returns current Thailand time | "What time is it?", "ตอนนี้กี่โมง" |

## Troubleshooting

### No Audio Input

1. Check microphone permissions in system settings
2. List devices: `python -m src.main --list-devices`
3. Specify device: `python -m src.main --input-device <index>`

### Connection Errors

1. Verify API key: `echo $OPENAI_API_KEY`
2. Check network connectivity
3. Ensure API key has realtime model access

### High Latency

1. Use wired internet connection
2. Close bandwidth-heavy applications
3. Check `--log-level DEBUG` for timing info

## Development

### Code Style

```bash
# Lint
ruff check src tests

# Type check
mypy src
```

### Adding New Tools

1. Create function in `src/tools.py`
2. Add `@function_tool` decorator
3. Add to `AVAILABLE_TOOLS` list
4. Register in `src/agent.py`

## License

MIT

## Technical Details

### voice_main.py Architecture

The recommended `voice_main.py` uses the **VoicePipeline** approach:

| Component | Model | Description |
|-----------|-------|-------------|
| **STT** | `gpt-4o-transcribe` | Latest speech-to-text with Thai language hint |
| **LLM** | `gpt-4o-mini` | Agent response generation |
| **TTS** | `gpt-4o-mini-tts` | Text-to-speech with "coral" voice |

**Audio Settings:**
- Sample rate: 48kHz (native) → 24kHz (API)
- Format: PCM16, mono channel
- Microphone: MacBook Pro Microphone (device 4)

### Debugging Audio Issues

If transcription is inaccurate:

1. **Check recorded audio:**
   ```bash
   afplay /tmp/debug_recording.wav
   ```

2. **List available microphones:**
   ```bash
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```

3. **Change microphone in `voice_main.py`:**
   ```python
   # Line ~107: Change device number
   with sd.InputStream(device=4, ...)  # 4 = MacBook Pro Microphone
   ```

## References

- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [Realtime API Guide](https://openai.github.io/openai-agents-python/realtime/guide/)
- [Voice Pipeline Example](https://github.com/openai/openai-agents-python/blob/main/examples/voice/static/main.py)
