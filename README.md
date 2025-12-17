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

# Optional
VOICE_AGENT_VOICE=nova          # Voice: alloy, echo, fable, onyx, nova, shimmer, ash
VOICE_AGENT_AUDIO_FORMAT=pcm16  # Format: pcm16, g711_ulaw, g711_alaw
VOICE_AGENT_VAD_TYPE=semantic_vad  # VAD: server_vad, semantic_vad
VOICE_AGENT_LOG_LEVEL=INFO      # Level: DEBUG, INFO, WARNING, ERROR
```

## Usage

### Start the Voice Agent

```bash
python -m src.main
```

### Command Line Options

```bash
python -m src.main --help

Options:
  --voice {alloy,echo,fable,onyx,nova,shimmer,ash}
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

### Example Session

```
$ python -m src.main

==================================================
🎤 Voice Agent Ready!
==================================================
Speak in Thai or English. Press Ctrl+C to exit.
==================================================

You: สวัสดีครับ
Agent: สวัสดีค่ะ ยินดีต้อนรับค่ะ มีอะไรให้ช่วยไหมคะ?

You: What time is it?
Agent: The current time is 3:30 PM.

You: ขอบคุณครับ
Agent: ยินดีค่ะ มีอะไรให้ช่วยอีกไหมคะ?

^C
👋 Shutting down...
✅ Voice agent stopped
```

## Project Structure

```
realtime-voice-agent/
├── src/
│   ├── __init__.py          # Package metadata
│   ├── main.py              # Entry point, CLI
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

## References

- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [Realtime API Guide](https://openai.github.io/openai-agents-python/realtime/guide/)
