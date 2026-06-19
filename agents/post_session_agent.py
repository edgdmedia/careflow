import json

from shared.client import get_qwen_client

SYSTEM_PROMPT = """You are a post-session assistant for Anxiety Unplugged, a group therapy program. Generate a warm closing message for a participant after their session (session number provided), including a reference to that week's worksheet and one open-ended feedback question. Respond in JSON with fields: closing_message, feedback_question."""


def run_post_session_agent(participant: dict, session_number: int, attended: bool) -> dict:
    try:
        client = get_qwen_client()
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
    except Exception as e:
        return {
            "error": str(e),
            "closing_message": f"Thank you for attending Session {session_number}. We hope you found it valuable. Your worksheet and next session details will follow.",
            "feedback_question": "What's one thing from today's session that stood out to you?",
        }
