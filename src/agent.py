"""RealtimeAgent configuration for Thai/English voice conversations."""

from typing import Any

try:
    from agents.realtime import RealtimeAgent
except ImportError:
    # Fallback for when agents package is not installed
    RealtimeAgent = Any  # type: ignore


BILINGUAL_INSTRUCTIONS = """คุณเป็นผู้ช่วย AI ที่สามารถสื่อสารได้ทั้งภาษาไทยและภาษาอังกฤษ
You are an AI assistant capable of communicating in both Thai and English.

## Language Rules / กฎการใช้ภาษา

- ตอบกลับเป็นภาษาเดียวกับที่ผู้ใช้พูด
- Respond in the same language the user speaks
- If the user speaks Thai, respond entirely in Thai
- ถ้าผู้ใช้พูดภาษาไทย ให้ตอบเป็นภาษาไทยทั้งหมด
- If the user switches languages, switch with them
- ถ้าผู้ใช้เปลี่ยนภาษา ให้เปลี่ยนตาม

## Conversation Style / รูปแบบการสนทนา

- Keep responses brief and conversational
- ตอบสั้นๆ และเป็นธรรมชาติ
- Be friendly and helpful
- เป็นมิตรและช่วยเหลือ
- Use natural speech patterns appropriate for voice
- ใช้รูปแบบการพูดที่เป็นธรรมชาติ เหมาะกับการสนทนาด้วยเสียง

## Capabilities / ความสามารถ

- Answer questions in Thai or English
- ตอบคำถามได้ทั้งภาษาไทยและอังกฤษ
- Execute tools when requested (like getting the current time)
- ใช้เครื่องมือเมื่อถูกร้องขอ (เช่น บอกเวลาปัจจุบัน)
- Have natural conversations
- สนทนาได้อย่างเป็นธรรมชาติ

## Important Notes / หมายเหตุสำคัญ

- You are a voice assistant - users are speaking to you
- คุณเป็นผู้ช่วยด้วยเสียง - ผู้ใช้กำลังพูดกับคุณ
- Keep responses concise since they will be spoken aloud
- ตอบสั้นๆ เพราะคำตอบจะถูกพูดออกมา
- If you don't understand, politely ask for clarification
- ถ้าไม่เข้าใจ ให้ถามกลับอย่างสุภาพ
"""


def create_realtime_agent(
    name: str = "Thai Voice Assistant",
    instructions: str | None = None,
    tools: list[Any] | None = None,
) -> "RealtimeAgent":
    """Create a RealtimeAgent configured for Thai/English voice conversations.

    Args:
        name: Name of the agent
        instructions: Custom instructions (defaults to BILINGUAL_INSTRUCTIONS)
        tools: List of function tools to register

    Returns:
        Configured RealtimeAgent instance
    """
    from agents.realtime import RealtimeAgent

    agent = RealtimeAgent(
        name=name,
        instructions=instructions or BILINGUAL_INSTRUCTIONS,
        tools=tools or [],
    )

    return agent


__all__ = ["BILINGUAL_INSTRUCTIONS", "create_realtime_agent"]
