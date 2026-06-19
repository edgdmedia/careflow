# CareFlow — Autonomous Therapy Intake & Session Management Agent

An autonomous AI agent pipeline that handles the full pre- and post-session workflow for group therapy programs. Built for the Qwen Cloud Global AI Hackathon (Track 4: Autopilot Agent).

**Problem:** Therapists spend hours on intake forms, scheduling, reminders, and session documentation — time that should go to client care.

**Solution:** CareFlow chains five AI agents (Intake → Eligibility → Scheduling → Pre-Session → Post-Session) powered by Qwen Cloud, with a human-in-the-loop checkpoint at the eligibility gate.

## Project Status

- [x] Intake Agent — Qwen NLP extraction + crisis keyword fallback
- [x] Eligibility Agent — approve/flag/decline against group criteria
- [x] Scheduling Agent — cohort slot assignment + warm confirmation
- [x] Pre-Session Agent — 24hr reminder + 1-10 mood check-in
- [x] Post-Session Agent — worksheet delivery + feedback + session log
- [x] Therapist Dashboard — Streamlit (6 tabs: overview, participants, pending reviews, cohorts, session logs, agent runs)
- [x] Human-in-the-Loop Gate — crisis escalation + eligibility review queue
- [x] E2E Pipeline — `python pipeline/run_pipeline.py "message"`

## Tech Stack

- **AI Reasoning:** Qwen Cloud API (qwen3.7-plus)
- **Backend:** Alibaba Cloud ECS
- **Database:** PostgreSQL (Supabase)
- **Orchestration:** Python pipeline
- **Dashboard:** Streamlit

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your Qwen Cloud API key and Supabase credentials
```

## License

MIT
