import os
from supabase import create_client, Client


def get_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")
    return create_client(url, key)


def insert_participant(data: dict) -> dict:
    supabase = get_client()
    result = supabase.table("participants").insert(data).execute()
    return result.data[0]


def update_participant(participant_id: str, updates: dict) -> dict:
    supabase = get_client()
    result = supabase.table("participants").update(updates).eq("id", participant_id).execute()
    return result.data[0]


def insert_agent_run(agent_name: str, participant_id: str, input_payload: dict, output_payload: dict) -> dict:
    supabase = get_client()
    result = supabase.table("agent_runs").insert({
        "agent_name": agent_name,
        "participant_id": participant_id,
        "input_payload": input_payload,
        "output_payload": output_payload,
    }).execute()
    return result.data[0]


def insert_eligibility_review(participant_id: str, agent_decision: str, agent_reasoning: str, urgent_flag: bool = False) -> dict:
    supabase = get_client()
    result = supabase.table("eligibility_reviews").insert({
        "participant_id": participant_id,
        "agent_decision": agent_decision,
        "agent_reasoning": agent_reasoning,
        "urgent_flag": urgent_flag,
    }).execute()
    return result.data[0]


def approve_participant(participant_id: str, review_id: str, reviewer: str = "therapist") -> dict:
    supabase = get_client()
    supabase.table("eligibility_reviews").update({
        "human_override": "approved",
        "reviewed_by": reviewer,
        "reviewed_at": "now()",
    }).eq("id", review_id).execute()
    return update_participant(participant_id, {"eligibility_status": "approved"})


def get_pending_reviews() -> list[dict]:
    supabase = get_client()
    result = supabase.table("participants") \
        .select("*, eligibility_reviews(*)") \
        .eq("eligibility_status", "flagged_for_review") \
        .execute()
    return result.data


def get_available_cohorts() -> list[dict]:
    supabase = get_client()
    result = supabase.table("cohorts").select("*").execute()
    return [c for c in result.data if c["current_enrollment"] < c["max_capacity"]]


def increment_cohort_enrollment(cohort_id: str) -> dict:
    supabase = get_client()
    cohort = supabase.table("cohorts").select("*").eq("id", cohort_id).execute().data[0]
    new_count = cohort["current_enrollment"] + 1
    result = supabase.table("cohorts").update({"current_enrollment": new_count}).eq("id", cohort_id).execute()
    return result.data[0]


def insert_session_log(data: dict) -> dict:
    supabase = get_client()
    result = supabase.table("session_logs").insert(data).execute()
    return result.data[0]


def get_all_participants() -> list[dict]:
    supabase = get_client()
    result = supabase.table("participants").select("*").order("created_at", desc=True).execute()
    return result.data


def get_all_cohorts() -> list[dict]:
    supabase = get_client()
    result = supabase.table("cohorts").select("*").execute()
    return result.data


def get_all_session_logs() -> list[dict]:
    supabase = get_client()
    result = supabase.table("session_logs").select("*, participants(name)").order("created_at", desc=True).execute()
    return result.data


def get_agent_runs(limit: int = 20) -> list[dict]:
    supabase = get_client()
    result = supabase.table("agent_runs").select("*").order("created_at", desc=True).limit(limit).execute()
    return result.data
