import os
import sys
from datetime import datetime

import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["SUPABASE_URL"] = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL", "")
os.environ["SUPABASE_KEY"] = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY", "")

from db.db_client import (
    get_all_participants,
    get_all_cohorts,
    get_all_session_logs,
    get_agent_runs,
    get_pending_reviews,
    approve_participant,
    get_available_cohorts,
)

st.set_page_config(page_title="CareFlow Dashboard", page_icon="🧠", layout="wide")

st.title("🧠 CareFlow")
st.markdown("*Autonomous Therapy Intake & Session Management*")

tab_overview, tab_participants, tab_reviews, tab_cohorts, tab_logs, tab_agents = st.tabs(
    ["Overview", "Participants", "Pending Reviews", "Cohorts", "Session Logs", "Agent Runs"]
)

participants = get_all_participants()
cohorts = get_all_cohorts()
logs = get_all_session_logs()
pending = get_pending_reviews()
agent_runs = get_agent_runs(50)

with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Participants", len(participants))
    col2.metric("Pending Reviews", len(pending))
    col3.metric("Active Cohorts", len(cohorts))
    col4.metric("Sessions Logged", len(logs))

    st.subheader("Recent Agent Activity")
    if agent_runs:
        df = pd.DataFrame([
            {"Time": r["created_at"][:19] if r.get("created_at") else "", "Agent": r["agent_name"], "Success": "✅" if r.get("success") else "❌"}
            for r in agent_runs[:10]
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No agent runs yet. Run the pipeline to see activity here.")

with tab_participants:
    st.subheader(f"All Participants ({len(participants)})")
    if participants:
        df = pd.DataFrame([{
            "Name": p.get("name", "—"),
            "Concern": (p.get("presenting_concern") or "")[:50],
            "Urgency": p.get("urgency_level", "—"),
            "Status": p.get("eligibility_status", "pending"),
            "Crisis": "🚨" if p.get("requires_immediate_escalation") else "—",
            "Cohort": p.get("assigned_cohort_id", "—")[:8] if p.get("assigned_cohort_id") else "—",
            "Created": p.get("created_at", "")[:10] if p.get("created_at") else "",
        } for p in participants])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No participants yet.")

with tab_reviews:
    st.subheader(f"Pending Reviews ({len(pending)})")
    if not pending:
        st.success("No pending reviews — all clear!")
    else:
        for p in pending:
            er = (p.get("eligibility_reviews") or [{}])[0]
            urgent = "🚨 URGENT" if er.get("urgent_flag") else ""
            with st.container(border=True):
                cols = st.columns([3, 1])
                cols[0].markdown(f"**{p.get('name', 'Unknown')}** {urgent}")
                cols[0].caption(f"Concern: {p.get('presenting_concern', '—')}")
                cols[0].markdown(f"*Agent reasoning:* {er.get('agent_reasoning', '—')}")
                if cols[1].button("✅ Approve", key=f"approve_{p['id']}"):
                    approve_participant(p["id"], er["id"])
                    st.rerun()
                if cols[1].button("❌ Decline", key=f"decline_{p['id']}"):
                    st.warning("Decline not yet implemented via dashboard")

with tab_cohorts:
    st.subheader("Cohorts")
    if cohorts:
        df = pd.DataFrame([{
            "Name": c["name"],
            "Program": c.get("program_name", ""),
            "Day": c.get("day_of_week", ""),
            "Time": c.get("time_slot", ""),
            "Start": c.get("start_date", ""),
            "Enrolled": f"{c['current_enrollment']}/{c['max_capacity']}",
            "Available": "✅" if c["current_enrollment"] < c["max_capacity"] else "❌",
        } for c in cohorts])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No cohorts created yet.")

with tab_logs:
    st.subheader(f"Session Logs ({len(logs)})")
    if logs:
        df = pd.DataFrame([{
            "Participant": l.get("participants", {}).get("name", l.get("participant_id", "")[:8]) if l.get("participants") else l.get("participant_id", "")[:8],
            "Session": l.get("session_number", ""),
            "Date": l.get("session_date", ""),
            "Attended": "✅" if l.get("attended") else "❌",
            "Duration": f"{l.get('duration_minutes', 60)}m",
            "Check-in": (l.get("checkin_response") or "")[:30],
        } for l in logs])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No sessions logged yet.")

with tab_agents:
    st.subheader("Agent Run Log")
    if agent_runs:
        df = pd.DataFrame([{
            "Time": r.get("created_at", "")[:19] if r.get("created_at") else "",
            "Agent": r["agent_name"],
            "Participant": r.get("participant_id", "")[:8],
            "Model": r.get("model_used", ""),
            "Status": "✅" if r.get("success") else "❌",
        } for r in agent_runs])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No agent runs recorded.")
