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


def insert_agent_run(agent_name: str, participant_id: str, input_payload: dict, output_payload: dict) -> dict:
    supabase = get_client()
    result = supabase.table("agent_runs").insert({
        "agent_name": agent_name,
        "participant_id": participant_id,
        "input_payload": input_payload,
        "output_payload": output_payload,
    }).execute()
    return result.data[0]


def get_pending_reviews() -> list[dict]:
    supabase = get_client()
    result = supabase.table("participants") \
        .select("*, eligibility_reviews(*)") \
        .eq("eligibility_status", "flagged_for_review") \
        .execute()
    return result.data


def get_available_cohorts() -> list[dict]:
    supabase = get_client()
    result = supabase.table("cohorts") \
        .select("*") \
        .lt("current_enrollment", supabase.column("max_capacity")) \
        .execute()
    return result.data
