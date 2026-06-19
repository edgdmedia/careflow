-- =========================================
-- CareFlow — PostgreSQL Schema (Supabase)
-- =========================================

-- PARTICIPANTS
CREATE TABLE participants (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT,
    contact_method  TEXT,
    contact_value   TEXT,
    presenting_concern TEXT,
    secondary_concerns TEXT[],
    urgency_level   TEXT,
    requires_immediate_escalation BOOLEAN DEFAULT FALSE,
    eligibility_status TEXT DEFAULT 'pending',
    assigned_cohort_id UUID REFERENCES cohorts(id),
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- COHORTS
CREATE TABLE cohorts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    program_name    TEXT DEFAULT 'Anxiety Unplugged',
    start_date      DATE,
    day_of_week     TEXT,
    time_slot       TEXT,
    max_capacity    INTEGER DEFAULT 8,
    current_enrollment INTEGER DEFAULT 0,
    facilitator_id  UUID,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- ELIGIBILITY REVIEWS (human-in-the-loop log)
CREATE TABLE eligibility_reviews (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id  UUID REFERENCES participants(id),
    agent_decision  TEXT,
    agent_reasoning TEXT,
    urgent_flag     BOOLEAN DEFAULT FALSE,
    human_override  TEXT,
    reviewed_by     TEXT,
    reviewed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- SESSION LOGS (powers training hours tracker)
CREATE TABLE session_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id  UUID REFERENCES participants(id),
    cohort_id       UUID REFERENCES cohorts(id),
    session_number  INTEGER,
    session_date    DATE,
    attended        BOOLEAN,
    duration_minutes INTEGER DEFAULT 60,
    facilitator_id  UUID,
    checkin_response TEXT,
    feedback_response TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- AGENT RUNS (audit log)
CREATE TABLE agent_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name      TEXT NOT NULL,
    participant_id  UUID REFERENCES participants(id),
    input_payload   JSONB,
    output_payload  JSONB,
    model_used      TEXT DEFAULT 'qwen3.7-plus',
    success         BOOLEAN DEFAULT TRUE,
    error_message   TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- INDEXES
CREATE INDEX idx_participants_eligibility_status ON participants(eligibility_status);
CREATE INDEX idx_session_logs_participant ON session_logs(participant_id);
CREATE INDEX idx_agent_runs_agent_name ON agent_runs(agent_name);
