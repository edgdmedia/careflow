import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.intake_agent import run_intake_agent
from agents.eligibility_agent import run_eligibility_agent
from agents.scheduling_agent import run_scheduling_agent
from db.db_client import insert_participant, insert_agent_run, get_available_cohorts


def run_pipeline(message: str) -> dict:
    eligibility_criteria_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "content", "eligibility_criteria.md"
    )
    with open(eligibility_criteria_path) as f:
        criteria = f.read()

    intake_result = run_intake_agent(message)
    print(f"[INTAKE] {json.dumps(intake_result, indent=2)}")

    participant_record = {
        "name": intake_result.get("name"),
        "presenting_concern": intake_result.get("presenting_concern"),
        "secondary_concerns": intake_result.get("secondary_concerns", []),
        "urgency_level": intake_result.get("urgency_level"),
        "requires_immediate_escalation": intake_result.get("requires_immediate_escalation", False),
    }
    participant = insert_participant(participant_record)
    insert_agent_run("intake", participant["id"], {"message": message}, intake_result)

    if intake_result.get("requires_immediate_escalation"):
        print("[PIPELINE] Crisis detected — escalating to therapist, bypassing normal flow")
        return {"participant": participant, "intake": intake_result, "crisis_escalated": True}

    eligibility_result = run_eligibility_agent(intake_result, criteria)
    print(f"[ELIGIBILITY] {json.dumps(eligibility_result, indent=2)}")
    insert_agent_run("eligibility", participant["id"], intake_result, eligibility_result)

    decision = eligibility_result.get("decision", "flagged_for_review")

    if decision == "flagged_for_review" or decision == "declined":
        print(f"[PIPELINE] Participant {decision} — pausing for human review")
        return {
            "participant": participant,
            "intake": intake_result,
            "eligibility": eligibility_result,
            "needs_review": True,
        }

    available_slots = get_available_cohorts()
    print(f"[PIPELINE] Available slots: {len(available_slots)}")

    scheduling_result = run_scheduling_agent(intake_result, available_slots)
    print(f"[SCHEDULING] {json.dumps(scheduling_result, indent=2)}")
    insert_agent_run("scheduling", participant["id"], {
        "available_slots": available_slots
    }, scheduling_result)

    return {
        "participant": participant,
        "intake": intake_result,
        "eligibility": eligibility_result,
        "scheduling": scheduling_result,
        "needs_review": False,
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = sys.argv[1]
    else:
        message = input("Enter inquiry message: ")

    result = run_pipeline(message)
    print(f"\n[PIPELINE COMPLETE]\n{json.dumps(result, indent=2)}")
