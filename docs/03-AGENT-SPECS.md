# CareFlow — Agent Specifications

Detailed design spec for each agent in the pipeline: purpose, system prompt, expected
input/output, and edge cases to handle. Use this as the source of truth when building
each `agents/*.py` file.

---

## Agent 1: Intake Agent

**File:** `agents/intake_agent.py`
**Status:** ✅ Prototype validated

### Purpose
Convert a free-text inquiry (WhatsApp, email, or form) into structured participant data.

### Input
```python
run_intake_agent(message: str) -> dict
```
A raw string, e.g.:
> "Hi, I've been struggling with anxiety for months now and I can't sleep at night. My name is Tunde."

### System Prompt (validated working version)
```
You are an intake assistant for a mental health group therapy program called
Anxiety Unplugged. Extract the following from the user's message: name (if given),
presenting concern, urgency level (low/medium/high), and suggested next question to
ask. Respond in JSON.
```

### Expected Output
```json
{
  "name": "Tunde",
  "presenting_concern": "Struggling with anxiety for several months and experiencing insomnia.",
  "urgency_level": "medium",
  "suggested_next_question": "Thank you for reaching out, Tunde. To help us find the best group fit for you, could you tell me a little more about how your anxiety and lack of sleep are impacting your daily life?"
}
```

### Edge Cases to Handle
- No name given → `"name": null`, agent should ask for it in the next question
- Crisis language (suicidal ideation, self-harm mentions) → `urgency_level: "high"` AND
  a flag field `"requires_immediate_escalation": true` — this should bypass the normal
  pipeline and alert the therapist directly, NOT proceed through normal scheduling
- Multiple concerns mentioned → capture the primary one, note others in a
  `"secondary_concerns"` array

### Improvement for Production
Add a second field `"language_detected"` if you want to support multilingual intake
later (relevant given Yoruba-speaking participants).

---

## Agent 2: Eligibility Agent

**File:** `agents/eligibility_agent.py`
**Status:** Not yet built

### Purpose
Decide whether a participant is a fit for the current Anxiety Unplugged cohort, based
on intake data and defined group criteria (see `content/eligibility_criteria.md`).

### Input
```python
run_eligibility_agent(intake_data: dict, criteria: str) -> dict
```

### System Prompt (draft — refine once criteria doc is written)
```
You are an eligibility screening assistant for a 6-week group therapy program called
Anxiety Unplugged, focused on anxiety recovery. Given a participant's intake data and
the program's eligibility criteria, decide one of three outcomes: "approved",
"flagged_for_review", or "declined". Always explain your reasoning in one sentence.
If the participant mentions any crisis indicators (suicidal ideation, self-harm,
active psychosis), always return "flagged_for_review" regardless of other criteria,
and set urgent_flag to true. Respond in JSON.
```

### Expected Output
```json
{
  "decision": "approved",
  "reasoning": "Participant's primary concern (anxiety, insomnia) matches the group's core focus with no crisis indicators present.",
  "urgent_flag": false
}
```

### Edge Cases to Handle
- Crisis indicators → ALWAYS flag, regardless of other matching criteria. Never let
  the agent auto-approve a crisis case.
- Participant concern is adjacent but not a clean match (e.g., grief rather than
  anxiety) → `flagged_for_review` with reasoning explaining the mismatch, so the
  therapist can decide whether to redirect them to a different resource.
- Missing key data from intake (e.g., no age given, if age matters for your criteria)
  → `flagged_for_review`, never silently approve with incomplete data.

### Human-in-the-Loop Gate
This is the critical checkpoint. Any `flagged_for_review` or `declined` result should
NOT proceed automatically to the Scheduling Agent. Build this as an explicit pause in
`pipeline/run_pipeline.py` — e.g., write the flagged case to a `pending_review` table
and require a manual function call or dashboard click to release it forward.

---

## Agent 3: Scheduling Agent

**File:** `agents/scheduling_agent.py`
**Status:** Not yet built

### Purpose
Assign an approved participant to an available cohort slot and generate a
confirmation message.

### Input
```python
run_scheduling_agent(participant: dict, available_slots: list[dict]) -> dict
```

### System Prompt (draft)
```
You are a scheduling assistant for Anxiety Unplugged, a group therapy program. Given
a participant's profile and a list of available cohort slots (with day, time, and
current enrollment count), choose the best-fit slot and write a warm, brief
confirmation message welcoming them to the group. Respond in JSON with fields:
assigned_slot_id, confirmation_message.
```

### Expected Output
```json
{
  "assigned_slot_id": "cohort_3_tuesdays_6pm",
  "confirmation_message": "Hi Tunde, welcome to Anxiety Unplugged! You've been placed in our Tuesday 6pm cohort starting [date]. We'll send you a reminder and a short check-in the day before each session. Looking forward to having you with us."
}
```

### Edge Cases to Handle
- No slots available → return `"assigned_slot_id": null` and a waitlist message
  instead of a confirmation
- Slot at capacity → never assign past a defined max cohort size (store this in your
  `cohorts` table, check it before calling the agent, not the agent's job to know
  arbitrary capacity numbers)

### Calendar Integration (Optional for MVP)
For the hackathon demo, you can mock calendar booking with a simple database write.
Google Calendar API integration is a "nice to have" — do not let it block your
submission timeline.

---

## Agent 4: Pre-Session Agent

**File:** `agents/pre_session_agent.py`
**Status:** Not yet built

### Purpose
24 hours before a scheduled session, send a reminder and a short mood/readiness
check-in, and log the participant's response.

### Input
```python
run_pre_session_agent(participant: dict, session_number: int) -> dict
```

### System Prompt (draft)
```
You are a pre-session assistant for Anxiety Unplugged. Generate a warm, brief
reminder message for a participant's upcoming session (session number provided),
including one short check-in question about how they're feeling today (a 1-10 scale
question is ideal). Respond in JSON with fields: reminder_message, checkin_question.
```

### Expected Output
```json
{
  "reminder_message": "Hi Tunde, just a reminder that Session 3 of Anxiety Unplugged is tomorrow at 6pm. We're looking forward to seeing you.",
  "checkin_question": "On a scale of 1-10, how would you rate your anxiety level today?"
}
```

### Note
This agent's *output* (the message) is generated by Qwen, but the actual *response*
to the check-in question comes back from the participant later — that response
should be logged as plain data (a number/text), not re-processed by another agent
call unless you want sentiment analysis on it (optional enhancement).

---

## Agent 5: Post-Session Agent

**File:** `agents/post_session_agent.py`
**Status:** Not yet built

### Purpose
After a session, deliver the week's worksheet, collect feedback, log attendance, and
update the therapist's training hours tracker.

### Input
```python
run_post_session_agent(participant: dict, session_number: int, attended: bool) -> dict
```

### System Prompt (draft)
```
You are a post-session assistant for Anxiety Unplugged. Generate a warm closing
message for a participant after their session (session number provided), including
a link/reference to that week's worksheet and one open-ended feedback question.
Respond in JSON with fields: closing_message, feedback_question.
```

### Expected Output
```json
{
  "closing_message": "Thank you for joining Session 3 today, Tunde. Here's your worksheet for this week's theme: Naming Your Anxiety Triggers.",
  "feedback_question": "What's one thing from today's session that you want to remember this week?"
}
```

### Logging Requirement (Important for Olalekan's licensing hours)
Every call to this agent should trigger a database write to a `session_logs` table
recording: participant_id, session_number, date, attended (boolean), facilitator_id,
and duration. This is what powers the training hours tracker — a genuine real-world
value-add beyond the hackathon demo.

---

## Shared Design Principles Across All Agents

1. **Always respond in JSON.** Never let an agent return free-form prose as its
   primary output — wrap the human-readable message inside a JSON field instead, so
   your pipeline code can reliably parse it.
2. **Crisis language always escalates.** Any agent that touches participant-facing
   text should be designed to detect and flag crisis language, never minimize or
   auto-resolve it.
3. **Warmth over efficiency in tone.** Every generated message should read like it
   came from Unclutter's actual voice — warm, human, never clinical-cold. This is a
   judged criterion (Innovation, Presentation) as much as a clinical one.
4. **Idempotency.** Each agent function should be safe to re-run without creating
   duplicate database records — check for existing records before inserting.
