# CareFlow — Autonomous Therapy Operations Agent

CareFlow is an autonomous AI agent that reduces therapist admin across the full care journey — from first inquiry to follow-up — with near-zero manual coordination for standard cases.

This version is built and demonstrated through **Anxiety Unplugged**, a live group therapy program, as the reference implementation. That gives the product a concrete real-world workflow today, while the underlying architecture is designed to extend to individual therapy, support groups, and other therapist-led programs.

Built for the Qwen Cloud Global AI Hackathon (Track 4: Autopilot Agent).

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
