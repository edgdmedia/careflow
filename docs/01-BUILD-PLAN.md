# CareFlow — Master Build Plan

**Project:** CareFlow — Autonomous Therapy Intake & Session Management Agent
**Hackathon:** Global AI Hackathon Series with Qwen Cloud (Devpost)
**Track:** Track 4 — Autopilot Agent
**Deadline:** July 9, 2026, 2:00pm PDT
**Builder:** Olalekan Owonikoko (solo build)
**Status:** Intake Agent prototype validated ✅ (Day 1 complete)

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
| AI reasoning | Qwen Cloud API (`qwen3.7-plus` or similar) | Required for hackathon; OpenAI-compatible, strong NLP extraction |
| Backend deploy | Alibaba Cloud ECS | **Required** for hackathon submission proof |
| Orchestration | n8n (self-hosted on ECS) or plain Python scripts chained together | n8n = visual, faster for solo demo; Python = more control |
| Database | PostgreSQL (Supabase free tier) | Already familiar to Olalekan; generous free tier |
| Frontend dashboard | Next.js (minimal) or Streamlit (faster for solo) | Streamlit recommended for time constraints |
| Comms | WhatsApp Business API or simple email (SMTP) for demo | WhatsApp ideal but email is faster to wire up solo |
| Calendar | Google Calendar API (optional for MVP — can mock for demo) | Nice-to-have, not core to passing judging criteria |

**Solo-build recommendation:** Skip n8n and Next.js for the first working version.
Build the agent pipeline in plain Python first (faster to debug alone), get it working
end-to-end, THEN wrap it in a dashboard (Streamlit) once the logic is proven. This is
the fastest path to a working demo within 21 days.

---

## 3. Repository Structure

```
careflow/
├── .env                          # API keys (never commit this)
├── .gitignore
├── README.md                     # public-facing repo description
├── opencode.json                 # OpenCode + Qwen Cloud config
├── requirements.txt
├── agents/
│   ├── __init__.py
│   ├── intake_agent.py
│   ├── eligibility_agent.py
│   ├── scheduling_agent.py
│   ├── pre_session_agent.py
│   └── post_session_agent.py
├── db/
│   ├── schema.sql
│   └── db_client.py
├── pipeline/
│   └── run_pipeline.py           # chains all agents together
├── dashboard/
│   └── app.py                    # Streamlit dashboard (Phase 3)
├── tests/
│   ├── test_intake.py
│   ├── test_eligibility.py
│   └── sample_messages.json      # test inquiries for demo
├── docs/
│   ├── architecture-diagram.png  # exported from hackathon pack
│   └── alibaba-deployment-proof.md
└── content/
    ├── eligibility_criteria.md   # Anxiety Unplugged group criteria
    ├── worksheets/                # real worksheet content
    └── message_templates.md      # tone/voice for agent messages
```

---

## 4. Build Phases (21-Day Solo Plan)

### Phase 0 — Setup ✅ (Done)
- [x] Devpost registration
- [x] Qwen Cloud account + API key
- [x] First API call validated (Intake Agent prototype working)
- [ ] GitHub repo created (public, MIT license)
- [ ] OpenCode configured with Qwen Cloud provider

### Phase 1 — Core Agents (Days 2–7)
- [ ] `intake_agent.py` — formalize today's working prototype into a reusable function
- [ ] `eligibility_criteria.md` — write out actual Anxiety Unplugged group criteria
- [ ] `eligibility_agent.py` — reasoning agent that approves/flags/declines
- [ ] `db/schema.sql` — participants, sessions, cohorts, agent_logs tables
- [ ] Supabase project created, schema applied
- [ ] `db_client.py` — simple connection + insert/query functions

### Phase 2 — Pipeline Chaining (Days 8–12)
- [ ] `scheduling_agent.py` — cohort assignment + confirmation message generation
- [ ] `pipeline/run_pipeline.py` — runs Intake → Eligibility → (approval gate) → Scheduling
- [ ] Manual test: simulate 3–5 different inquiry types through the full pipeline
- [ ] `pre_session_agent.py` — reminder + check-in message generator
- [ ] `post_session_agent.py` — feedback collection + worksheet delivery + hours logging

### Phase 3 — Dashboard + Polish (Days 13–17)
- [ ] `dashboard/app.py` (Streamlit) — shows participant list, pending approvals, session logs
- [ ] Real worksheet content added to `content/worksheets/`
- [ ] Message tone pass — ensure all agent-generated text matches Unclutter's warm voice
- [ ] Deploy backend to Alibaba Cloud ECS
- [ ] Record proof-of-deployment screen recording

### Phase 4 — Submission Assets (Days 18–21)
- [ ] Architecture diagram finalized (already drafted — see `docs/architecture-diagram.png`)
- [ ] 3-minute demo video recorded and uploaded (YouTube, public)
- [ ] README.md completed with setup instructions
- [ ] Devpost write-up submitted (content already drafted — see `02-DEVPOST-WRITEUP.md`)
- [ ] Optional: blog post written for Blog Post Award ($500)
- [ ] Final submission at least 24 hours before deadline (aim for July 8)

---

## 5. Tool Division (Solo Build, Multi-AI-Assistant Workflow)

You're using three AI coding tools. Here's how to split work so they don't collide:

| Tool | Best for | When to use it |
|---|---|---|
| **Claude Code** | Architecture review, debugging, prompt engineering for agents, code review, refactoring | Whenever you're stuck, reviewing a finished file, or designing agent prompt logic |
| **OpenCode (w/ Qwen provider)** | Live-testing actual Qwen API calls, validating agent outputs against the real hackathon model | Every time you need to confirm an agent's prompt actually produces good Qwen output |
| **Codex** | Fast boilerplate — DB schema, utility functions, repetitive CRUD, test scaffolding | Anything mechanical that doesn't need judgment calls |

**Suggested workflow per agent file:**
1. Use Claude Code to design the agent's prompt + logic structure
2. Use Codex to scaffold the Python function shell + error handling boilerplate
3. Use OpenCode to actually run it against Qwen Cloud and see real output
4. Use Claude Code again to review/refine based on what Qwen actually returned

---

## 6. Definition of "Done" for the MVP Demo

You do NOT need all five agents fully production-ready. For a winning hackathon demo,
you need:

1. ✅ Intake Agent — working, tested (done)
2. Eligibility Agent — working, with one human-approval flagged example in the demo
3. Scheduling Agent — at minimum, generates a confirmation message (calendar API optional)
4. A simple log/dashboard showing the data the agents created (even a clean printed table counts)
5. A 3-minute video that narrates the real problem (your own experience running Anxiety Unplugged)
   and shows these three agents working end-to-end

Pre-Session and Post-Session agents are valuable additions if time allows, but are not
required to score well on the judging criteria (Technical Depth 30%, Innovation 30%,
Problem Value 25%, Presentation 15%).

---

## 7. Companion Documents

This plan references three other markdown files you should keep alongside it in VS Code:

- `02-DEVPOST-WRITEUP.md` — full submission text, ready to copy into Devpost fields
- `03-AGENT-SPECS.md` — detailed prompt design and expected I/O for each of the 5 agents
- `04-DB-SCHEMA.md` — full Postgres schema with field definitions and rationale

---

## 8. Immediate Next Action

Open VS Code in your `careflow` project folder and:

1. Create the folder structure above
2. Move your working `hello_qwen.py` logic into `agents/intake_agent.py`, wrapped as a
   function `run_intake_agent(message: str) -> dict`
3. Write `content/eligibility_criteria.md` with your real Anxiety Unplugged criteria
   (this unblocks the Eligibility Agent build)
4. Initialize git, create `.gitignore` (must exclude `.env`), push to GitHub as a public repo
