import json
import os

from shared.client import get_qwen_client

SYSTEM_PROMPT = """You are a post-session assistant for Anxiety Unplugged, a group therapy program. Generate a warm closing message for a participant after their session (session number provided), including a reference to that week's worksheet and one open-ended feedback question. Respond in JSON with fields: closing_message, feedback_question."""


WORKSHEET_INDEX_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "content",
    "worksheets",
    "index.json",
)


def _get_worksheet(session_number: int) -> dict | None:
    with open(WORKSHEET_INDEX_PATH) as f:
        index = json.load(f)
    return index.get("worksheets", {}).get(str(session_number))


def run_post_session_agent(participant: dict, session_number: int, attended: bool) -> dict:
    worksheet = _get_worksheet(session_number)
    try:
        client = get_qwen_client()
        user_message = (
            f"Participant name: {participant.get('name', 'there')}\n"
            f"Session number: {session_number}\n"
            f"Attended: {'yes' if attended else 'no'}\n"
            f"Worksheet title: {(worksheet or {}).get('title', 'Session worksheet')}\n"
            f"Worksheet theme: {(worksheet or {}).get('theme', 'Session reflection and practice')}\n"
            f"Worksheet file: {(worksheet or {}).get('file', '')}"
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
        result = json.loads(raw)
    except Exception as e:
        result = {
            "error": str(e),
            "closing_message": f"Thank you for attending Session {session_number}. We hope you found it valuable. Your worksheet and next session details will follow.",
            "feedback_question": "What's one thing from today's session that stood out to you?",
        }

    result["worksheet"] = worksheet or {
        "title": f"Session {session_number} Worksheet",
        "file": None,
        "theme": "Session reflection and practice",
    }
    return result
