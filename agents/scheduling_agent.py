import json
import os
from openai import OpenAI

SYSTEM_PROMPT = """You are a scheduling assistant for Anxiety Unplugged, a group therapy program. Given a participant's profile and a list of available cohort slots (with day, time, and current enrollment count), choose the best-fit slot and write a warm, brief confirmation message welcoming them to the group. Respond in JSON with fields: assigned_slot_id, confirmation_message. If no slots are available, set assigned_slot_id to null and write a waitlist message instead."""


def run_scheduling_agent(participant: dict, available_slots: list[dict]) -> dict:
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    user_message = (
        f"Participant:\n{json.dumps(participant, indent=2)}\n\n"
        f"Available cohort slots:\n{json.dumps(available_slots, indent=2)}"
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
