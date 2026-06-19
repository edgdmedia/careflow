import json
import os
from openai import OpenAI

SYSTEM_PROMPT = """You are a post-session assistant for Anxiety Unplugged, a group therapy program. Generate a warm closing message for a participant after their session (session number provided), including a reference to that week's worksheet and one open-ended feedback question. Respond in JSON with fields: closing_message, feedback_question."""


def run_post_session_agent(participant: dict, session_number: int, attended: bool) -> dict:
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    user_message = (
        f"Participant name: {participant.get('name', 'there')}\n"
        f"Session number: {session_number}\n"
        f"Attended: {'yes' if attended else 'no'}"
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
