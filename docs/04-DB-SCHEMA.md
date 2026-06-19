# CareFlow — Database Schema

PostgreSQL schema for Supabase. Copy the SQL block into Supabase's SQL editor to
create all tables at once. **(Note: `cohorts` must be created before `participants`
due to the foreign key reference.)**

> ✅ Supabase project is live. Schema has been applied. RLS is disabled for the
> hackathon (re-enable before production).

---

## Entity Overview

```
cohorts ──────────────────> participants (assigned_cohort_id)
                              │
participants ──┬──> session_logs
               │
               └──> eligibility_reviews

agent_runs (audit log of every agent call)
```

---

## Full SQL Schema

```sql
-- =========================================
-- COHORTS (must exist first)
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
-- ELIGIBILITY REVIEWS (human-in-the-loop log)
-- =========================================
CREATE TABLE eligibility_reviews (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id  UUID REFERENCES participants(id),
    agent_decision  TEXT,                 -- 'approved' | 'flagged_for_review' | 'declined'
    agent_reasoning TEXT,
    urgent_flag     BOOLEAN DEFAULT FALSE,
    human_override  TEXT,                 -- null until therapist reviews
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
    agent_name      TEXT NOT NULL,        -- 'intake' | 'eligibility' | 'scheduling'
    participant_id  UUID REFERENCES participants(id),
    input_payload   JSONB,
    output_payload  JSONB,
    model_used      TEXT DEFAULT 'qwen3.7-plus',
    success         BOOLEAN DEFAULT TRUE,
    error_message   TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- =========================================
-- INDEXES
-- =========================================
CREATE INDEX idx_participants_eligibility_status ON participants(eligibility_status);
CREATE INDEX idx_session_logs_participant ON session_logs(participant_id);
CREATE INDEX idx_agent_runs_agent_name ON agent_runs(agent_name);

-- =========================================
-- SEED DATA
-- =========================================
INSERT INTO cohorts (name, program_name, start_date, day_of_week, time_slot, max_capacity)
VALUES ('Tuesday 6pm - Cohort 3', 'Anxiety Unplugged', '2026-07-15', 'Tuesday', '18:00', 8);
```

---

## Field Rationale Notes

- **`requires_immediate_escalation`** on `participants` — a dedicated boolean
  separate from `urgency_level`, so your dashboard can filter for true crisis cases
  with a single simple query.

- **`eligibility_reviews.human_override`** — kept separate from `agent_decision` so
  you always retain the agent's original reasoning even after a therapist overrides
  it. Used in the dashboard approve/decline workflow.

- **`agent_runs`** — audit log table. Populated live by `pipeline/run_pipeline.py`.
  Valuable for debugging, demo transparency, and future prompt evaluation.

- **`cohorts.current_enrollment`** — denormalized counter. Updated by the pipeline
  after scheduling. Simpler than a trigger for a hackathon timeline.

- **Cohort table order** — defined before `participants` in the SQL to avoid
  `relation "cohorts" does not exist` errors on the foreign key.

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
5. Disable RLS for hackathon:
   ```sql
   ALTER TABLE cohorts DISABLE ROW LEVEL SECURITY;
   ALTER TABLE participants DISABLE ROW LEVEL SECURITY;
   ALTER TABLE eligibility_reviews DISABLE ROW LEVEL SECURITY;
   ALTER TABLE session_logs DISABLE ROW LEVEL SECURITY;
   ALTER TABLE agent_runs DISABLE ROW LEVEL SECURITY;
   ```
6. Install the Python client: `pip install supabase`
7. Test: `from db.db_client import get_all_cohorts; print(get_all_cohorts())`
