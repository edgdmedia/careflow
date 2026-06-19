import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.intake_agent import run_intake_agent
from agents.eligibility_agent import run_eligibility_agent
from agents.scheduling_agent import run_scheduling_agent
from agents.pre_session_agent import run_pre_session_agent
from agents.post_session_agent import run_post_session_agent

from db.db_client import (
    insert_participant,
    update_participant,
    insert_agent_run,
    insert_eligibility_review,
    insert_session_log,
    get_available_cohorts,
    increment_cohort_enrollment,
    get_pending_reviews,
    approve_participant,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def log(step: str, msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{step}] {msg}")


def load_criteria() -> str:
    path = os.path.join(PROJECT_ROOT, "content", "eligibility_criteria.md")
    with open(path) as f:
        return f.read()


def run_intake_step(message: str) -> dict:
    log("INTAKE", "Processing message...")
    result = run_intake_agent(message)
    log("INTAKE", f"Extracted: {result.get('name')} | urgency={result.get('urgency_level')}")
    return result


def run_eligibility_step(intake_data: dict) -> dict:
    log("ELIGIBILITY", "Running eligibility check...")
    criteria = load_criteria()
    result = run_eligibility_agent(intake_data, criteria)
    log("ELIGIBILITY", f"Decision: {result.get('decision')}")
    return result


def run_scheduling_step(intake_data: dict) -> dict:
    log("SCHEDULING", "Checking available cohorts...")
    slots = get_available_cohorts()
    if not slots:
        log("SCHEDULING", "No slots available")
        return {"assigned_slot_id": None, "confirmation_message": None}
    log("SCHEDULING", f"{len(slots)} slot(s) available")
    result = run_scheduling_agent(intake_data, slots)
    log("SCHEDULING", f"Assigned: {result.get('assigned_slot_id')}")
    return result


def run_pipeline(message: str) -> dict:
    intake_result = run_intake_step(message)

    participant = insert_participant({
        "name": intake_result.get("name"),
        "presenting_concern": intake_result.get("presenting_concern"),
        "secondary_concerns": intake_result.get("secondary_concerns", []),
        "urgency_level": intake_result.get("urgency_level"),
        "requires_immediate_escalation": intake_result.get("requires_immediate_escalation", False),
    })
    insert_agent_run("intake", participant["id"], {"message": message}, intake_result)
    log("PIPELINE", f"Participant {participant['id'][:8]} saved")

    if intake_result.get("requires_immediate_escalation"):
        update_participant(participant["id"], {"eligibility_status": "flagged_for_review"})
        insert_eligibility_review(
            participant["id"], "flagged_for_review",
            "Crisis indicators detected during intake — immediate therapist review required",
            urgent_flag=True,
        )
        log("PIPELINE", "⚠ CRISIS — escalated to therapist, bypassing normal flow")
        return {"participant": participant, "intake": intake_result, "crisis_escalated": True}

    eligibility_result = run_eligibility_step(intake_result)
    insert_agent_run("eligibility", participant["id"], intake_result, eligibility_result)

    decision = eligibility_result.get("decision", "flagged_for_review")
    urgent = eligibility_result.get("urgent_flag", False)

    if decision in ("flagged_for_review", "declined"):
        update_participant(participant["id"], {"eligibility_status": decision})
        insert_eligibility_review(
            participant["id"], decision,
            eligibility_result.get("reasoning", ""),
            urgent_flag=urgent,
        )
        log("PIPELINE", f"⏸ {decision} — pausing for HITL review")
        return {
            "participant": participant,
            "intake": intake_result,
            "eligibility": eligibility_result,
            "needs_review": True,
        }

    update_participant(participant["id"], {"eligibility_status": "approved"})
    scheduling_result = run_scheduling_step(intake_result)
    insert_agent_run("scheduling", participant["id"], {"available_slots": get_available_cohorts()}, scheduling_result)

    slot_id = scheduling_result.get("assigned_slot_id")
    if slot_id:
        increment_cohort_enrollment(slot_id)
        update_participant(participant["id"], {"assigned_cohort_id": slot_id})
        log("PIPELINE", f"Cohort enrollment incremented for {slot_id[:8]}")

    return {
        "participant": participant,
        "intake": intake_result,
        "eligibility": eligibility_result,
        "scheduling": scheduling_result,
        "needs_review": False,
    }


def run_pre_session_cycle(participant_id: str, session_number: int):
    from db.db_client import get_client
    supabase = get_client()
    p = supabase.table("participants").select("*").eq("id", participant_id).execute().data[0]
    result = run_pre_session_agent(p, session_number)
    log("PRE-SESSION", f"Reminder + check-in generated for session {session_number}")
    print(json.dumps(result, indent=2))


def run_post_session_cycle(participant_id: str, session_number: int, attended: bool):
    from db.db_client import get_client
    supabase = get_client()
    p = supabase.table("participants").select("*").eq("id", participant_id).execute().data[0]
    result = run_post_session_agent(p, session_number, attended)
    cohort_id = p.get("assigned_cohort_id")
    insert_session_log({
        "participant_id": participant_id,
        "cohort_id": cohort_id,
        "session_number": session_number,
        "session_date": datetime.now().date().isoformat(),
        "attended": attended,
        "duration_minutes": 60,
    })
    log("POST-SESSION", f"Session {session_number} logged for {participant_id[:8]}")
    print(json.dumps(result, indent=2))


def list_pending():
    reviews = get_pending_reviews()
    if not reviews:
        log("REVIEW", "No pending reviews")
        return
    for r in reviews:
        er = (r.get("eligibility_reviews") or [{}])[0]
        print(f"  {r['id'][:8]} | {r.get('name', '?')} | {er.get('agent_decision', '?')} | {er.get('agent_reasoning', '')[:80]}")
        print(f"    Approve with: --approve {r['id']} {er.get('id', '')}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CareFlow Pipeline")
    parser.add_argument("message", nargs="?", help="Inquiry message")
    parser.add_argument("--pre-session", metavar="PARTICIPANT_ID", help="Run pre-session cycle")
    parser.add_argument("--post-session", metavar="PARTICIPANT_ID", help="Run post-session cycle")
    parser.add_argument("--session-num", type=int, default=1, help="Session number")
    parser.add_argument("--attended", action="store_true", default=True, help="Mark attended")
    parser.add_argument("--pending", action="store_true", help="List pending reviews")
    parser.add_argument("--approve", nargs=2, metavar=("PARTICIPANT_ID", "REVIEW_ID"), help="Approve a flagged participant")

    args = parser.parse_args()

    if args.pending:
        list_pending()
    elif args.approve:
        pid, rid = args.approve
        result = approve_participant(pid, rid)
        log("REVIEW", f"Participant {pid[:8]} approved — now run scheduling")
    elif args.pre_session:
        run_pre_session_cycle(args.pre_session, args.session_num)
    elif args.post_session:
        run_post_session_cycle(args.post_session, args.session_num, args.attended)
    elif args.message:
        result = run_pipeline(args.message)
        print(f"\n{'='*50}")
        print("PIPELINE RESULT")
        print(f"{'='*50}")
        print(json.dumps({k: v for k, v in result.items() if k != "participant"}, indent=2, default=str))
    else:
        parser.print_help()
