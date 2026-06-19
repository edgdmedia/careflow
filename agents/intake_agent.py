import json
import os
import re
from openai import OpenAI

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die",
    "self-harm", "self harm", "cutting", "not safe",
    "hurt myself", "hurting myself", "don't want to be here",
]

SYSTEM_PROMPT = """You are an intake assistant for a mental health group therapy program called Anxiety Unplugged. Extract the following from the user's message: name (if given), presenting concern, urgency level (low/medium/high), and suggested next question to ask. Respond in JSON.

If the user mentions suicidal ideation, self-harm, or active crisis, set urgency_level to "high" and set requires_immediate_escalation to true.

If multiple concerns are mentioned, capture the primary one in presenting_concern and list others in a secondary_concerns array.

If no name is given, set name to null and ask for it in the suggested_next_question."""

QC_CRISIS_KEYWORDS = [
    "suicid", "kill myself", "end my life", "want to die",
    "self-harm", "self harm", "cutting", "not safe",
    "hurt myself", "hurting myself", "don't want to be here",
]

def _has_crisis_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in CRISIS_KEYWORDS)


def run_intake_agent(message: str) -> dict:
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen3.7-plus",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        response_format={"type": "json_object"},
    )

    raw = completion.choices[0].message.content
    result = json.loads(raw)

    if _has_crisis_keywords(message):
        result["requires_immediate_escalation"] = True
        result["urgency_level"] = "high"

    if "secondary_concerns" not in result:
        result["secondary_concerns"] = []

    return result
