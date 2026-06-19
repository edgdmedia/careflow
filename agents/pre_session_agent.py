import json

from shared.client import get_qwen_client

SYSTEM_PROMPT = """You are a pre-session assistant for Anxiety Unplugged, a group therapy program. Generate a warm, brief reminder message for a participant's upcoming session (session number provided), including one short check-in question about how they're feeling today (a 1-10 scale question is ideal). Respond in JSON with fields: reminder_message, checkin_question."""


def run_pre_session_agent(participant: dict, session_number: int) -> dict:
    try:
        client = get_qwen_client()
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
    except Exception as e:
        return {
            "error": str(e),
            "reminder_message": f"Hi {participant.get('name', 'there')}, this is a reminder that Session {session_number} is coming up. We look forward to seeing you!",
            "checkin_question": "On a scale of 1-10, how are you feeling today?",
        }
