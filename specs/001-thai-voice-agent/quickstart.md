# Quickstart: Thai/English Realtime Voice Agent

**Feature**: 001-thai-voice-agent  
**Date**: 2025-12-15

## Prerequisites

- **Python**: 3.11 or higher
- **Hardware**: Microphone and speakers/headphones
- **API Access**: OpenAI API key with realtime model permissions
- **OS**: macOS or Linux (Windows with WSL2)

## Installation

### 1. Clone and Setup

```bash
# Navigate to project directory
cd realtime-voice-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional (defaults shown)
VOICE_AGENT_VOICE=nova
VOICE_AGENT_AUDIO_FORMAT=pcm16
VOICE_AGENT_VAD_TYPE=semantic_vad
VOICE_AGENT_LOG_LEVEL=INFO
```

### 3. Verify Audio Devices

```bash
# List available audio devices
python -m src.audio --list-devices
```

Ensure your microphone and speakers are detected.

## Running the Agent

### Basic Usage

```bash
# Start the voice agent
python -m src.main
```

### With Options

```bash
# Specify voice
python -m src.main --voice shimmer

# Enable debug logging
python -m src.main --log-level DEBUG

# Specify audio devices
python -m src.main --input-device 1 --output-device 2
```

## Usage Guide

### Starting a Conversation

1. Run the agent with `python -m src.main`
2. Wait for "Ready. Start speaking..." message
3. Speak in Thai or English
4. The agent will respond in the same language

### Thai Conversation Example

```
You: สวัสดีครับ
Agent: สวัสดีค่ะ ยินดีต้อนรับค่ะ มีอะไรให้ช่วยไหมคะ?

You: ตอนนี้กี่โมงแล้ว
Agent: ตอนนี้เวลา 15:30 น. ค่ะ
```

### English Conversation Example

```
You: Hello, how are you?
Agent: Hello! I'm doing well, thank you for asking. How can I help you today?

You: What time is it?
Agent: The current time is 3:30 PM.
```

### Interrupting the Agent

- Simply start speaking while the agent is responding
- The agent will stop and listen to your new input
- No special command needed

### Ending the Session

- Press `Ctrl+C` to end the session
- Or say "goodbye" / "ลาก่อน"

## Available Tools

| Tool | Description | Example Trigger |
|------|-------------|-----------------|
| `get_current_time` | Returns current time in Thailand timezone | "What time is it?" / "ตอนนี้กี่โมง" |

## Troubleshooting

### No Audio Input Detected

```bash
# Check microphone permissions
# macOS: System Preferences → Security & Privacy → Microphone

# List and verify devices
python -m src.audio --list-devices
```

### Connection Errors

```bash
# Verify API key
echo $OPENAI_API_KEY

# Check network connectivity
curl -I https://api.openai.com
```

### High Latency

- Ensure stable internet connection
- Close bandwidth-heavy applications
- Try wired connection instead of WiFi

### Audio Quality Issues

- Use headphones to prevent echo
- Reduce background noise
- Speak clearly and at normal pace

## Testing

### Run Unit Tests

```bash
pytest tests/unit -v
```

### Run Integration Tests

```bash
pytest tests/integration -v
```

### Run All Tests with Coverage

```bash
pytest --cov=src --cov-report=html
```

## Project Structure

```
realtime-voice-agent/
├── src/
│   ├── __init__.py
│   ├── main.py          # Entry point
│   ├── agent.py         # Agent configuration
│   ├── runner.py        # Session management
│   ├── tools.py         # Function tools
│   ├── events.py        # Event handlers
│   ├── audio.py         # Audio I/O
│   └── config.py        # Configuration
├── tests/
│   ├── unit/
│   └── integration/
├── .env                  # Environment variables (create this)
├── requirements.txt      # Dependencies
└── README.md
```

## Dependencies

```
# requirements.txt
openai-agents[voice]>=0.1.0
sounddevice>=0.4.6
numpy>=1.24.0
python-dotenv>=1.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Development
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
```

## Next Steps

1. **Customize Agent Instructions**: Edit `src/agent.py` to modify agent behavior
2. **Add More Tools**: Implement new tools in `src/tools.py`
3. **Adjust VAD Settings**: Tune turn detection in `src/config.py`
4. **Add Logging**: Configure log output in `src/events.py`
