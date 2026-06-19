# CareFlow — Autonomous Therapy Intake & Session Management Agent

An autonomous AI agent pipeline that handles the full pre- and post-session workflow for group therapy programs. Built for the Qwen Cloud Global AI Hackathon (Track 4: Autopilot Agent).

**Problem:** Therapists spend hours on intake forms, scheduling, reminders, and session documentation — time that should go to client care.

**Solution:** CareFlow chains five AI agents (Intake → Eligibility → Scheduling → Pre-Session → Post-Session) powered by Qwen Cloud, with a human-in-the-loop checkpoint at the eligibility gate.

## Project Status

- [x] Intake Agent — prototype validated
- [ ] Eligibility Agent
- [ ] Scheduling Agent
- [ ] Pre-Session Agent
- [ ] Post-Session Agent
- [ ] Therapist Dashboard

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
