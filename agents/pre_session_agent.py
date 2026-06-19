import json
import os
from openai import OpenAI

SYSTEM_PROMPT = """You are a pre-session assistant for Anxiety Unplugged, a group therapy program. Generate a warm, brief reminder message for a participant's upcoming session (session number provided), including one short check-in question about how they're feeling today (a 1-10 scale question is ideal). Respond in JSON with fields: reminder_message, checkin_question."""


def run_pre_session_agent(participant: dict, session_number: int) -> dict:
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    user_message = (
        f"Participant name: {participant.get('name', 'there')}\n"
        f"Session number: {session_number}"
    )

    completion = client.chat.completions.create(
        model="qwen3.7-plus",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )

    raw = completion.choices[0].message.content
    return json.loads(raw)
