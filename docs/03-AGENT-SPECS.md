# CareFlow — Agent Specifications

Detailed design spec for each agent in the pipeline: purpose, system prompt, expected
input/output, and edge cases to handle. Use this as the source of truth when building
each `agents/*.py` file.

---

## Agent 1: Intake Agent

**File:** `agents/intake_agent.py`
**Status:** ✅ Built and tested (Phase 1)

### Purpose
Convert a free-text inquiry (WhatsApp, email, or form) into structured participant data.

### Input
```python
run_intake_agent(message: str) -> dict
```
A raw string, e.g.:
> "Hi, I've been struggling with anxiety for months now and I can't sleep at night. My name is Tunde."

### System Prompt (final)
```
You are an intake assistant for a mental health group therapy program called
Anxiety Unplugged. Extract the following from the user's message: name (if given),
presenting concern, urgency level (low/medium/high), and suggested next question to
ask. Respond in JSON.

If the user mentions suicidal ideation, self-harm, or active crisis, set urgency_level
to "high" and set requires_immediate_escalation to true.

If multiple concerns are mentioned, capture the primary one in presenting_concern and
list others in a secondary_concerns array.

If no name is given, set name to null and ask for it in the suggested_next_question.
```

### Expected Output
```json
{
  "name": "Tunde",
  "presenting_concern": "Anxiety",
  "secondary_concerns": ["Sleep difficulties"],
  "urgency_level": "medium",
  "requires_immediate_escalation": false,
  "suggested_next_question": "Hi Tunde, thank you for reaching out... could you share more about how your anxiety is affecting your daily life?"
}
```

### Edge Cases Handled
- **No name given** → `"name": null`, agent asks for it in suggested_next_question
- **Crisis language** → `urgency_level: "high"` + `requires_immediate_escalation: true`
- **Multiple concerns** → primary in `presenting_concern`, rest in `secondary_concerns[]`

### Safety Fallback
A keyword-based crisis detector (`_has_crisis_keywords()`) runs after the Qwen API
call to catch any crisis language the model might miss. If triggered, it overrides
the result with `requires_immediate_escalation: true`.

---

## Agent 2: Eligibility Agent

**File:** `agents/eligibility_agent.py`
**Status:** ✅ Built and tested (Phase 1)

### Purpose
Decide whether a participant is a fit for the current Anxiety Unplugged cohort, based
on intake data and defined group criteria (see `content/eligibility_criteria.md`).

### Input
```python
run_eligibility_agent(intake_data: dict, criteria: str) -> dict
```

### System Prompt (final)
```
You are an eligibility screening assistant for a 6-week group therapy program called
Anxiety Unplugged, focused on anxiety recovery. Given a participant's intake data and
the program's eligibility criteria, decide one of three outcomes: "approved",
"flagged_for_review", or "declined". Always explain your reasoning in one sentence.
If the participant mentions any crisis indicators (suicidal ideation, self-harm,
active psychosis), always return "flagged_for_review" regardless of other criteria,
and set urgent_flag to true. Respond in JSON with fields: decision, reasoning,
urgent_flag.
```

### Expected Output (approved)
```json
{
  "decision": "approved",
  "reasoning": "Participant's primary concern (panic attacks) matches the group's core focus with no crisis indicators present.",
  "urgent_flag": false
}
```

### Expected Output (flagged)
```json
{
  "decision": "flagged_for_review",
  "reasoning": "Participant's primary concern is grief, which is adjacent but not a core focus of the anxiety program. Therapist should assess fit.",
  "urgent_flag": false
}
```

### Expected Output (crisis)
```json
{
  "decision": "flagged_for_review",
  "reasoning": "Suicidal ideation detected — requires immediate therapist review.",
  "urgent_flag": true
}
```

### Edge Cases Handled
- Crisis indicators → ALWAYS flag, never auto-approve
- Adjacent concern (grief, depression without anxiety) → flag for therapist
- Missing key data → flag for review

---

## Agent 3: Scheduling Agent

**File:** `agents/scheduling_agent.py`
**Status:** ✅ Built and tested (Phase 2)

### Purpose
Assign an approved participant to an available cohort slot and generate a
confirmation message.

### Input
```python
run_scheduling_agent(participant: dict, available_slots: list[dict]) -> dict
```

### System Prompt (final)
```
You are a scheduling assistant for Anxiety Unplugged, a group therapy program. Given
a participant's profile and a list of available cohort slots (with day, time, and
current enrollment count), choose the best-fit slot and write a warm, brief
confirmation message welcoming them to the group. Respond in JSON with fields:
assigned_slot_id, confirmation_message. If no slots are available, set assigned_slot_id
to null and write a waitlist message instead.
```

### Expected Output
```json
{
  "assigned_slot_id": "a201338a-206e-42f1-be5c-d94a434c1a95",
  "confirmation_message": "Hi Chidi, welcome to Anxiety Unplugged! We've secured your spot in the Tuesday 6pm Cohort 3, starting July 15th. We look forward to seeing you there!"
}
```

### Edge Cases Handled
- **No slots available** → `assigned_slot_id: null`, waitlist message
- **Slot at capacity** → filtered out in `pipeline/run_pipeline.py` before agent is called

### Pipeline Integration
After scheduling, the pipeline:
1. Increments `cohorts.current_enrollment`
2. Updates `participants.assigned_cohort_id`
3. Logs the agent run to `agent_runs` table

---

## Agent 4: Pre-Session Agent

**File:** `agents/pre_session_agent.py`
**Status:** ✅ Built and tested (Phase 2)

### Purpose
24 hours before a scheduled session, send a reminder and a short mood/readiness
check-in, and log the participant's response.

### Input
```python
run_pre_session_agent(participant: dict, session_number: int) -> dict
```

### System Prompt (final)
```
You are a pre-session assistant for Anxiety Unplugged, a group therapy program.
Generate a warm, brief reminder message for a participant's upcoming session (session
number provided), including one short check-in question about how they're feeling
today (a 1-10 scale question is ideal). Respond in JSON with fields: reminder_message,
checkin_question.
```

### Expected Output
```json
{
  "reminder_message": "Hi Chidi! Just a quick reminder that your next Anxiety Unplugged session (Session 3) is coming up soon. We're looking forward to seeing you!",
  "checkin_question": "On a scale of 1 to 10, how are you feeling today?"
}
```

### Note
The agent generates the message. The participant's response to the check-in is logged
as plain data in `session_logs.checkin_response` through a separate database write.

---

## Agent 5: Post-Session Agent

**File:** `agents/post_session_agent.py`
**Status:** ✅ Built and tested (Phase 2)

### Purpose
After a session, deliver the week's worksheet, collect feedback, log attendance, and
update the therapist's training hours tracker.

### Input
```python
run_post_session_agent(participant: dict, session_number: int, attended: bool) -> dict
```

### System Prompt (final)
```
You are a post-session assistant for Anxiety Unplugged, a group therapy program.
Generate a warm closing message for a participant after their session (session number
provided), including a reference to that week's worksheet and one open-ended feedback
question. Respond in JSON with fields: closing_message, feedback_question.
```

### Expected Output
```json
{
  "closing_message": "Thank you for joining Session 3 today, Chidi. Here's this week's worksheet: Naming Your Anxiety Triggers.",
  "feedback_question": "What stood out to you the most from today's group discussion?"
}
```

### Logging Requirement
Every call triggers a `session_logs` database write recording: participant_id,
session_number, date, attended, facilitator_id, and duration (default 60 mins).
This powers the training hours tracker.

### Worksheet Index
Session numbers map to worksheet files via `content/worksheets/index.json`:
- Session 1 → Understanding Anxiety
- Session 2 → Naming Your Anxiety Triggers
- Session 3 → Challenging Anxious Thoughts
- Session 4 → Building Coping Strategies *(pending)*
- Session 5 → Exposure & Growth *(pending)*
- Session 6 → Relapse Prevention *(pending)*

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
