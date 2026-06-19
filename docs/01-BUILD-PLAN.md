# CareFlow — Master Build Plan

**Project:** CareFlow — Autonomous Therapy Intake & Session Management Agent
**Hackathon:** Global AI Hackathon Series with Qwen Cloud (Devpost)
**Track:** Track 4 — Autopilot Agent
**Deadline:** July 9, 2026, 2:00pm PDT
**Builder:** Olalekan Owonikoko (solo build)
**Status:** Phases 0–3 complete ✅ (dashboard built, pipeline end-to-end working)

---

## 1. What CareFlow Is

CareFlow is an autonomous AI agent pipeline that handles the full pre- and post-session
workflow for group therapy programs — inspired directly by the operational pain points
of running **Anxiety Unplugged**, Olalekan's 6-week anxiety recovery group therapy series
under the Unclutter mental wellness platform.

It automates:

1. **Intake** — parsing free-text inquiries (WhatsApp/email/form) into structured data
2. **Eligibility screening** — matching participants to group criteria, flagging edge cases
3. **Scheduling** — assigning cohort slots, sending confirmations, updating calendars
4. **Pre-session prep** — reminders + mood check-ins 24 hours before sessions
5. **Post-session wrap-up** — feedback collection, worksheet delivery, attendance + hours logging

A human-in-the-loop checkpoint sits between Eligibility and Scheduling — the therapist
approves edge cases before the pipeline proceeds. This is the single most important
design decision in the project: agents handle logistics, humans handle clinical judgment.

---

## 2. Tech Stack (Final)

| Layer | Technology | Why |
|---|---|---|
| AI reasoning | Qwen Cloud API (`qwen3.7-plus`) | Required for hackathon; OpenAI-compatible, strong NLP extraction |
| Backend deploy | Alibaba Cloud ECS | **Required** for hackathon submission proof |
| Orchestration | Python pipeline (`pipeline/run_pipeline.py`) | Chained agent calls with HITL gate, error handling, DB logging |
| Database | PostgreSQL (Supabase free tier) | Already familiar; generous free tier |
| Frontend dashboard | Streamlit | Fastest path to a solo-built dashboard with live DB reads |
| Comms | Email/WhatsApp (mocked for demo) | Pipeline generates messages; delivery channel TBD |
| Calendar | Google Calendar API (optional — not yet integrated) | Nice-to-have for post-submission |

---

## 3. Repository Structure

```
careflow/
├── .env                          # API keys (never commit this)
├── .env.example                  # Template for .env
├── .gitignore
├── README.md                     # public-facing repo description
├── requirements.txt
├── agents/
│   ├── __init__.py
│   ├── intake_agent.py           # Qwen NLP extraction + crisis keyword fallback
│   ├── eligibility_agent.py      # Approve/flag/decline against criteria
│   ├── scheduling_agent.py       # Cohort slot assignment + confirmation
│   ├── pre_session_agent.py      # Reminder + 1-10 check-in
│   └── post_session_agent.py     # Feedback + worksheet + session log
├── db/
│   ├── schema.sql                # Full Postgres schema + seed data
│   └── db_client.py              # Supabase client with query helpers
├── pipeline/
│   └── run_pipeline.py           # CLI: run, review, approve, pre/post cycles
├── dashboard/
│   └── app.py                    # Streamlit dashboard (6 tabs)
├── tests/
│   ├── test_intake.py
│   └── sample_messages.json      # 5 test scenarios
├── docs/
│   ├── 01-BUILD-PLAN.md          # This file
│   ├── 02-DEVPOST-WRITEUP.md     # Devpost submission text
│   ├── 03-AGENT-SPECS.md         # Detailed agent specs
│   ├── 04-DB-SCHEMA.md           # Schema + rationale
│   └── info.html                 # Hackathon info pack
└── content/
    ├── eligibility_criteria.md   # Anxiety Unplugged group criteria
    └── worksheets/
        ├── index.json            # Session-to-worksheet mapping
        ├── session-01-understanding-anxiety.md
        ├── session-02-naming-triggers.md
        ├── session-03-challenging-thoughts.md
        └── ... (sessions 4-6 pending)
```

---

## 4. Build Phases — Progress

### Phase 0 — Setup ✅ (Done)
- [x] Devpost registration
- [x] Qwen Cloud account + API key
- [x] First API call validated (Intake Agent prototype working)
- [ ] GitHub repo created (public, MIT license) — **still todo**
- [ ] OpenCode configured with Qwen Cloud provider

### Phase 1 — Core Agents ✅ (Done)
- [x] `intake_agent.py` — formalized from prototype with crisis keyword fallback
- [x] `eligibility_criteria.md` — inclusion/exclusion rules + crisis protocol
- [x] `eligibility_agent.py` — Qwen-powered approve/flag/decline + urgent_flag
- [x] `db/schema.sql` — participants, cohorts, eligibility_reviews, session_logs, agent_runs
- [x] Supabase project created, schema applied, RLS disabled for hackathon
- [x] `db_client.py` — full CRUD helpers

### Phase 2 — Pipeline Chaining ✅ (Done)
- [x] `scheduling_agent.py` — cohort assignment + warm confirmation message
- [x] `pipeline/run_pipeline.py` — Intake → Eligibility → (HITL gate) → Scheduling with:
  - Crisis escalation (bypasses normal flow)
  - `flagged_for_review` / `declined` pause with DB write
  - Cohort enrollment auto-increment
  - CLI: `--pending`, `--approve`, `--pre-session`, `--post-session`
- [x] Manual test: standard anxiety (auto-approve), crisis (escalate), grief (flag for review)
- [x] `pre_session_agent.py` — reminder + 1-10 check-in question
- [x] `post_session_agent.py` — closing + worksheet reference + feedback + session log

### Phase 3 — Dashboard + Polish ✅ (Done)
- [x] `dashboard/app.py` (Streamlit) — 6 tabs: Overview, Participants, Pending Reviews, Cohorts, Session Logs, Agent Runs
- [x] Real worksheet content: sessions 1-3 (CBT-based exercises)
- [x] Message tone pass — prompts calibrated for warm, human voice
- [ ] Deploy backend to Alibaba Cloud ECS
- [ ] Record proof-of-deployment screen recording

### Phase 4 — Submission Assets (Days 18–21)
- [ ] Architecture diagram finalized (see `docs/info.html` for draft)
- [ ] 3-minute demo video recorded and uploaded (YouTube, public)
- [ ] README.md completed with setup instructions
- [ ] Devpost write-up submitted (see `02-DEVPOST-WRITEUP.md`)
- [ ] Optional: blog post for Blog Post Award ($500)
- [ ] Remainder worksheets: sessions 4-6 in `content/worksheets/`
- [ ] Final submission at least 24 hours before deadline (aim for July 8)

---

## 5. Tool Division (Solo Build, Multi-AI-Assistant Workflow)

| Tool | Best for | When to use it |
|---|---|---|
| **Claude Code** | Architecture review, debugging, prompt engineering, code review | Stuck on logic, reviewing files, designing agent prompts |
| **OpenCode (w/ Qwen provider)** | Live-testing actual Qwen API calls against the real hackathon model | Every time you need to confirm agent output quality |
| **Codex** | Fast boilerplate — DB schema, utility functions, test scaffolding | Mechanical work with few judgment calls |

---

## 6. Definition of "Done" for the MVP Demo

1. ✅ Intake Agent — working, tested
2. ✅ Eligibility Agent — working, grief case flagged for review in demo
3. ✅ Scheduling Agent — generates confirmation, assigns cohort
4. ✅ Dashboard — participant list, pending reviews, session logs, agent runs
5. ⬜ 3-minute video narrating the real problem + showing agents end-to-end

Pre-Session and Post-Session agents are built but optional for the demo timeline.

---

## 7. Companion Documents

- `02-DEVPOST-WRITEUP.md` — full submission text, ready to copy into Devpost fields
- `03-AGENT-SPECS.md` — detailed prompt design and expected I/O for each of the 5 agents
- `04-DB-SCHEMA.md` — full Postgres schema with field definitions and rationale
