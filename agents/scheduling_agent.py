import json

from shared.client import get_qwen_client

SYSTEM_PROMPT = """You are a scheduling assistant for Anxiety Unplugged, a group therapy program. Given a participant's profile and a list of available cohort slots (with day, time, and current enrollment count), choose the best-fit slot and write a warm, brief confirmation message welcoming them to the group. Respond in JSON with fields: assigned_slot_id, confirmation_message. If no slots are available, set assigned_slot_id to null and write a waitlist message instead."""


def run_scheduling_agent(participant: dict, available_slots: list[dict]) -> dict:
    if not available_slots:
        name = participant.get("name", "there")
        return {
            "assigned_slot_id": None,
            "confirmation_message": (
                f"Hi {name}, thank you for your interest in Anxiety Unplugged. "
                "All current cohorts are full. We've added you to our waitlist and "
                "will reach out as soon as a spot opens."
            ),
        }

    try:
        client = get_qwen_client()
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
    except Exception as e:
        return {
            "error": str(e),
            "assigned_slot_id": None,
            "confirmation_message": "We're working on your placement. We'll follow up with a confirmed slot soon.",
        }
