# CareFlow — Devpost Submission Write-Up

Copy each section directly into the corresponding Devpost submission field.

---

## Project Name

**CareFlow**

---

## Track

**Track 4: Autopilot Agent**

---

## Tagline / Short Description

CareFlow is an autonomous AI agent that handles the full therapy intake and session
management workflow — from first message to session log — so therapists can focus
entirely on their clients.

---

## Inspiration

Mental health therapists spend a significant portion of their working time on
administrative work that never helps a single client: chasing intake forms, manually
scheduling cohort groups, sending reminders, collecting session feedback, and updating
training logs for licensing compliance. For therapists in training — who need to
document every client hour to meet licensing requirements — this burden is especially
acute.

We built CareFlow because we experienced this problem firsthand. Running a group
therapy program called *Anxiety Unplugged* — a six-week anxiety recovery series — we
found that the logistics of intake, scheduling, and post-session follow-up consumed
hours that should have gone toward preparation and presence. CareFlow automates that
entire operational layer, so a therapist can take on more clients, document hours
accurately, and deliver better care without drowning in admin.

---

## What It Does

CareFlow is a multi-step autonomous agent pipeline that manages the complete pre- and
post-session workflow for group or individual therapists:

- **Intake Agent** — Receives free-text inquiries via WhatsApp, web form, or email.
  Uses Qwen NLP to extract presenting concern, name, and availability through a
  natural conversation — no rigid forms.
- **Eligibility Agent** — Screens participants against group therapy criteria. Flags
  edge cases for therapist review before any scheduling occurs (human-in-the-loop
  checkpoint).
- **Scheduling Agent** — Assigns participants to available cohort slots, sends
  confirmation messages with onboarding info, and updates cohort enrollment
  automatically.
- **Pre-Session Agent** — Sends reminders and short check-in questions 24 hours before
  each session. Surfaces participant mood data to the therapist before the session
  starts.
- **Post-Session Agent** — Delivers session worksheets, collects feedback, logs
  attendance, and updates the therapist's training hours tracker for licensing
  compliance.
- **Therapist Dashboard** — A clean Streamlit interface showing participant progress,
  cohort overview, session logs, pending reviews, and training hours — with all
  data populated by the agents, never manually entered.

---

## How We Built It

CareFlow is built on **Qwen Cloud infrastructure**, with Qwen-Max (`qwen3.7-plus`)
powering the NLP reasoning across all five agent steps. Each agent is a discrete Qwen
API call with a carefully designed system prompt and structured JSON output, chained
together into a Python pipeline.

Participant data and session logs are stored in **PostgreSQL via Supabase**. The
pipeline runner orchestrates Intake → Eligibility → (human-in-the-loop gate) →
Scheduling, with CLI commands for pending review management, pre-session reminders,
and post-session logging. The therapist dashboard is built with **Streamlit** and
reads directly from Supabase.

A crisis keyword detection fallback runs alongside the Qwen-powered intake to ensure
suicidal ideation and self-harm mentions are never missed by the model alone. The
pipeline auto-escalates crisis cases to the therapist and blocks scheduling until
human review.

Each agent in the pipeline is designed so that any single agent can be paused,
overridden, or extended without rebuilding the pipeline. This modularity means
CareFlow can be adapted to individual therapy, peer support groups, or institutional
mental health services.

---

## Challenges We Ran Into

- **Ambiguous free-text intake** — Real inquiries are messy; people describe mental
  health concerns in personal, sometimes vague language. Prompt engineering the
  Intake Agent to extract structured data without being clinical or cold required
  significant iteration.
- **Eligibility edge cases** — Some participants present with concerns adjacent to
  the group's focus but not a clean match. Building an agent that reasons about these
  cases probabilistically — and knows when to escalate — was the most technically
  nuanced part of the build.
- **State management across sessions** — Because the workflow spans days (intake →
  session 1 → session 6), maintaining coherent participant state across pipeline runs
  required careful schema design.

---

## Accomplishments We're Proud Of

- A fully end-to-end pipeline from raw inquiry message to confirmed session booking,
  requiring zero therapist input for standard cases.
- A human-in-the-loop checkpoint architecture that keeps the therapist in control of
  clinical decisions without burdening them with operational ones.
- A training hours tracker that automatically generates documentation
  therapists-in-training need for licensing — a genuine time-saver with real
  professional stakes.
- A culturally-grounded intake experience: the agent's conversational style was
  calibrated for warmth and accessibility, not clinical distance — reflecting the
  values of the Unclutter mental wellness platform it's built for.

---

## What We Learned

Building CareFlow taught us that the hardest part of agentic AI for sensitive domains
isn't the AI capability — it's the design of escalation. Knowing when an agent should
proceed autonomously and when it must pause for a human is a product decision as much
as a technical one. Getting that boundary right in a mental health context required
careful thinking about risk, consent, and clinical responsibility.

We also learned how strong Qwen's reasoning models are for structured extraction from
conversational text — the quality of intake parsing significantly exceeded
expectations.

---

## What's Next for CareFlow

- Integration with the full **Unclutter app suite** as the operational backbone for
  all group therapy programs
- **Voice intake** using Qwen's multimodal capabilities — so participants can leave a
  voice note rather than typing
- **Outcome tracking** — longitudinal mood and progress data across a participant's
  full program journey
- An **open-source release** of the core agent pipeline, enabling other therapists
  and mental health organisations to deploy CareFlow for their own programs

---

## Built With (Devpost Tags)

```
qwen-cloud, qwen-api, alibaba-cloud, python, postgresql, supabase, streamlit
```

---

## Submission Checklist Reminder

- [ ] Public GitHub repo with MIT license
- [ ] Alibaba Cloud deployment proof (recording + code file)
- [ ] Architecture diagram (PNG/PDF)
- [ ] 3-minute demo video (YouTube, public)
- [ ] This write-up pasted into Devpost fields
- [ ] Track selected: Track 4 — Autopilot Agent
