# Anxiety Unplugged — Eligibility Criteria

## Program Focus

Anxiety Unplugged is a 6-week group therapy program for adults managing anxiety. The program uses evidence-based CBT and mindfulness techniques to help participants understand, manage, and reduce anxiety in their daily lives.

---

## Inclusion Criteria

A participant should be considered **eligible** if they meet ALL of the following:

1. **Primary concern is anxiety-related**
   - Generalized Anxiety Disorder (GAD)
   - Social anxiety
   - Panic attacks / panic disorder
   - Health anxiety
   - Performance anxiety
   - Anxiety secondary to life transitions or stress

2. **Age 18+**
   - The program is designed for adults. Participants under 18 should be referred to adolescent-specific services.

3. **Willing to commit to the full 6-week series**
   - Sessions run weekly, same time, same day.
   - Participants should miss no more than one session to benefit.

4. **Accessible via WhatsApp or email**
   - All pre- and post-session communication is automated via these channels.

---

## Exclusion Criteria

A participant should be **declined or flagged for therapist review** if ANY of the following apply:

### Automatic Decline (do not auto-approve — flag for therapist)

- **Active suicidal ideation with plan or intent**
  - Participant expresses wanting to end their life, has a plan, or has made an attempt recently.
- **Active psychosis or mania**
  - Participant is currently experiencing hallucinations, delusions, or manic episode.
- **Acute substance intoxication or severe withdrawal**
  - Participant is under the influence during intake or in active withdrawal requiring medical supervision.

### Flag for Therapist Review

- **Self-harm (non-suicidal)**
  - Participant reports current self-harm behaviors. Requires therapist judgment on appropriateness for group setting.
- **Recent suicide attempt or ideation without current plan**
  - Participant had suicidal thoughts or attempts in the past but does not currently have intent or plan. Therapist must assess stability.
- **Primary concern is not anxiety**
  - E.g., grief, trauma, depression without anxiety, relationship issues as primary. The program focuses on anxiety; adjacent concerns need therapist discretion.
- **Currently in individual therapy**
  - Not an exclusion, but the therapist should know to coordinate care. Flag for awareness.
- **Participant is under 18**
  - Flag and provide referral resources for adolescent mental health services.
- **Incomplete data**
  - If name, presenting concern, or contact method is missing, flag for follow-up rather than auto-approve.

---

## Decision Outcomes

| Outcome | Meaning | Next Step |
|---------|---------|-----------|
| **approved** | Participant clearly meets criteria | Route to Scheduling Agent |
| **flagged_for_review** | Edge case — therapist needs to decide | Write to pending_review queue; send notification to therapist dashboard |
| **declined** | Participant does not meet criteria | Send warm referral message with alternative resources |

---

## Crisis Protocol

If any crisis indicator is detected — regardless of other criteria — the Eligibility Agent must always return `flagged_for_review` with `urgent_flag: true`. Never auto-approve or auto-decline a crisis case. The therapist must be notified immediately.
