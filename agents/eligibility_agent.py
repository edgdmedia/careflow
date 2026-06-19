import json

from shared.client import get_qwen_client

SYSTEM_PROMPT = """You are an eligibility screening assistant for a 6-week group therapy program called Anxiety Unplugged, focused on anxiety recovery. Given a participant's intake data and the program's eligibility criteria, decide one of three outcomes: "approved", "flagged_for_review", or "declined". Always explain your reasoning in one sentence. If the participant mentions any crisis indicators (suicidal ideation, self-harm, active psychosis), always return "flagged_for_review" regardless of other criteria, and set urgent_flag to true. Respond in JSON with fields: decision, reasoning, urgent_flag."""


def run_eligibility_agent(intake_data: dict, criteria: str) -> dict:
    try:
        client = get_qwen_client()
        user_message = (
            f"Participant intake data:\n{json.dumps(intake_data, indent=2)}\n\n"
            f"Eligibility criteria:\n{criteria}"
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
            "decision": "flagged_for_review",
            "reasoning": "Eligibility check failed due to a technical error. A human review is required.",
            "urgent_flag": False,
        }
