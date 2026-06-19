# CareFlow — Database Schema

PostgreSQL schema for Supabase. Copy the SQL block into Supabase's SQL editor to
create all tables at once, or save it as `db/schema.sql` and run it via your
preferred Postgres client.

---

## Entity Overview

```
participants ──┬──> session_logs
               │
               └──> eligibility_reviews

cohorts ───────┴──> participants (assigned_cohort_id)

agent_runs (audit log of every agent call, for debugging + demo transparency)
```

---

## Full SQL Schema

```sql
-- =========================================
-- PARTICIPANTS
-- =========================================
CREATE TABLE participants (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT,
    contact_method  TEXT,              -- 'whatsapp' | 'email' | 'form'
    contact_value   TEXT,               -- phone number or email address
    presenting_concern TEXT,
    secondary_concerns TEXT[],
    urgency_level   TEXT,                -- 'low' | 'medium' | 'high'
    requires_immediate_escalation BOOLEAN DEFAULT FALSE,
    eligibility_status TEXT DEFAULT 'pending',  -- 'pending' | 'approved' | 'flagged_for_review' | 'declined'
    assigned_cohort_id UUID REFERENCES cohorts(id),
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- =========================================
-- COHORTS
-- =========================================
CREATE TABLE cohorts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,        -- e.g. "Tuesday 6pm - Cohort 3"
    program_name    TEXT DEFAULT 'Anxiety Unplugged',
    start_date      DATE,
    day_of_week     TEXT,
    time_slot       TEXT,
    max_capacity    INTEGER DEFAULT 8,
    current_enrollment INTEGER DEFAULT 0,
    facilitator_id  UUID,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- =========================================
-- ELIGIBILITY REVIEWS (human-in-the-loop log)
-- =========================================
CREATE TABLE eligibility_reviews (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id  UUID REFERENCES participants(id),
    agent_decision  TEXT,                 -- 'approved' | 'flagged_for_review' | 'declined'
    agent_reasoning TEXT,
    urgent_flag     BOOLEAN DEFAULT FALSE,
    human_override  TEXT,                 -- null until therapist reviews; same enum as agent_decision
    reviewed_by     TEXT,
    reviewed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- =========================================
-- SESSION LOGS (powers the training hours tracker)
-- =========================================
CREATE TABLE session_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id  UUID REFERENCES participants(id),
    cohort_id       UUID REFERENCES cohorts(id),
    session_number  INTEGER,
    session_date    DATE,
    attended        BOOLEAN,
    duration_minutes INTEGER DEFAULT 60,
    facilitator_id  UUID,
    checkin_response TEXT,               -- pre-session mood/readiness response
    feedback_response TEXT,              -- post-session feedback response
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- =========================================
-- AGENT RUNS (audit log — useful for demo + debugging)
-- =========================================
CREATE TABLE agent_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name      TEXT NOT NULL,        -- 'intake' | 'eligibility' | 'scheduling' | 'pre_session' | 'post_session'
    participant_id  UUID REFERENCES participants(id),
    input_payload   JSONB,
    output_payload  JSONB,
    model_used      TEXT DEFAULT 'qwen3.7-plus',
    success         BOOLEAN DEFAULT TRUE,
    error_message   TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- =========================================
-- INDEXES (for dashboard query performance)
-- =========================================
CREATE INDEX idx_participants_eligibility_status ON participants(eligibility_status);
CREATE INDEX idx_session_logs_participant ON session_logs(participant_id);
CREATE INDEX idx_agent_runs_agent_name ON agent_runs(agent_name);
```

---

## Field Rationale Notes

- **`requires_immediate_escalation`** on `participants` — a dedicated boolean
  separate from `urgency_level`, so your dashboard can filter for true crisis cases
  with a single simple query, independent of the more nuanced urgency scale.

- **`eligibility_reviews.human_override`** — kept separate from `agent_decision` so
  you always retain the agent's original reasoning even after a therapist overrides
  it. This is valuable both for your demo narrative (showing the human-in-the-loop
  actually working) and for any future audit/compliance need.

- **`agent_runs`** — this table is not strictly necessary for the product to function,
  but it is extremely valuable for:
  1. Debugging during the hackathon build
  2. Demonstrating "Technical Depth" in your demo video — you can literally show this
     table populating live as agents run
  3. Long-term: a foundation for prompt evaluation/improvement once in production

- **`cohorts.current_enrollment`** — denormalized counter rather than always
  `COUNT()`-ing participants. Simpler for a fast solo build; update it manually in
  your scheduling agent's database write rather than building a trigger (triggers
  add complexity you don't need for a hackathon timeline).

---

## Supabase Setup Steps

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Go to the SQL Editor → paste the full schema above → Run
3. Go to Project Settings → API → copy your `Project URL` and `anon public` key
4. Add both to your `.env` file:
   ```
   SUPABASE_URL=your_project_url
   SUPABASE_KEY=your_anon_key
   ```
5. Install the Python client: `pip install supabase`
6. Test the connection with a simple `db_client.py`:

```python
import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Quick test
response = supabase.table("cohorts").select("*").execute()
print(response.data)
```

---

## Seed Data for Demo (Optional but Recommended)

Before recording your demo video, seed at least one cohort so the Scheduling Agent
has something real to assign participants to:

```sql
INSERT INTO cohorts (name, program_name, start_date, day_of_week, time_slot, max_capacity)
VALUES ('Tuesday 6pm - Cohort 3', 'Anxiety Unplugged', '2026-07-15', 'Tuesday', '18:00', 8);
```
