import json

from shared.client import get_qwen_client

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die",
    "self-harm", "self harm", "cutting", "not safe",
    "hurt myself", "hurting myself", "don't want to be here",
]

SYSTEM_PROMPT = """You are an intake assistant for a mental health group therapy program called Anxiety Unplugged. Extract the following from the user's message: name (if given), presenting concern, urgency level (low/medium/high), and suggested next question to ask. Respond in JSON.

If the user mentions suicidal ideation, self-harm, or active crisis, set urgency_level to "high" and set requires_immediate_escalation to true.

If multiple concerns are mentioned, capture the primary one in presenting_concern and list others in a secondary_concerns array.

If no name is given, set name to null and ask for it in the suggested_next_question."""


def _has_crisis_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(pattern in text_lower for pattern in CRISIS_KEYWORDS)


def run_intake_agent(message: str) -> dict:
    try:
        client = get_qwen_client()
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
    except Exception as e:
        return {
            "error": str(e),
            "name": None,
            "presenting_concern": None,
            "urgency_level": "unknown",
            "requires_immediate_escalation": False,
            "secondary_concerns": [],
            "suggested_next_question": "I'm sorry, we're experiencing a technical issue. Please try again or contact us directly.",
        }

    if _has_crisis_keywords(message):
        result["requires_immediate_escalation"] = True
        result["urgency_level"] = "high"

    if "secondary_concerns" not in result:
        result["secondary_concerns"] = []

    return result
