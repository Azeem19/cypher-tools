# Grant RFA Decomposer — Build 2 (scaffold)

*Grant guidelines in → role-split work plan out, across the 38-grant playbook.*

Born from the Silence Kills PABC work: Rob hand-built a **74-row role-split** for
one grant. This build turns that manual labor into a generator — feed it any
grant RFA, get back a structured, role-assigned work plan. **This is the labor
clone that removes Rob from grant prep.**

> **Status: scaffold only.** The spec and Lego breakdown are captured here;
> implementation waits on the source docs listed below. Priority is Build 1
> (done) then this — both are on the revenue path.

## The Lego breakdown

| Block | What it is | Done when |
|-------|-----------|-----------|
| 01 · Parser | Ingest a grant RFA (PDF/doc); extract every required section — title, type, word/char limit, attachments, eligibility gates. | Any RFA PDF → a clean structured list of sections + constraints. |
| 02 · Role-Split Rule | Tag each section **Applicant** (org docs, budget, permits, artistic content) / **Cypher** (data storytelling, MEL, impact narrative, engagement) / **Joint**, with a reason. | Each section auto-tagged with a rationale. |
| 03 · Angle Layer | Per Cypher/Joint section, pull a suggested angle from the Partnership Canvas + RNN doc + the $350K proof; draft a first move. | Every Cypher/Joint row carries a one-line strategic angle. |
| 04 · Gate Check | Verify eligibility gates before any narrative work (PABC: 501(c)(3)/(c)(6) letter, DC incorporation, board, 990). A RED gate halts narrative generation. | Agent refuses to draft against an unmet gate and names it. |
| 05 · Output | Render a color-coded Word table (Applicant = gold, Cypher = teal, Joint = warm neutral) + an Airtable tracker row per section. | One paste-ready Word doc + a live tracker. |
| 06 · Generalizer | Point it at the 38-grant playbook — same parser, rule, output → 38 work plans from one generator. | Any playbook grant yields a role-split without Rob reading the RFA line by line. |

## Role-split ownership rule

- **Applicant of record** owns: org docs, budget, permits, artistic content.
- **Cypher** owns: data storytelling, MEL framework, impact narrative, community
  engagement strategy.
- **Joint** where both touch — and flagged for a human call when ownership is
  arguable.

## Runs

- **Run one (validation): PABC FY2027** — DC Public Art Building Communities,
  CAH-administered, up to $125K. Applicant of record: **Silence Kills**, confirmed
  501(c)(3) → **eligibility gate GREEN**. Validate the generator against the
  existing 74-row / 8-section-group split.
- **Run two: the 38-grant playbook** (`Cypher_Grant_Playbook_Feb2026.docx`, five
  tiers incl. international — ADSI Nigeria, NAMIL Egypt).

## Edge cases to spec into the agent

- Ambiguous ownership → tag **Joint** and flag for a human call.
- Missing limit/constraint in the RFA → "confirm with funder", never invent one.
- International grants → flag currency, language, and local-entity requirements as
  separate gates.

## Dependencies (needed before full build)

Not yet in-repo — provide these to build Blocks 01–03/06:

1. **Logic Model** (role-split logic source).
2. The existing **74-row role-split** for PABC (training/validation case).
3. `Cypher_Grant_Playbook_Feb2026.docx` (run two).

Found nearby and usable for the angle layer (Block 03):
`~/Documents/Claude/Projects/Biz: Cypher X Remembrance 2026/Cypher_x_SilenceKills_{SOW,MOU}_Summer2026.pdf`
and `~/Documents/Claude/Projects/Cypher Brand Build/Cypher_x_TheSweet_PartnershipCanvas.pdf`.

## Reuse

- Parser can reuse the PDF-reading approach already used across the repos; the
  gate check follows the same blocking-override pattern as
  `node_scorer/scorer.py` (a RED gate halts downstream work) and
  `remembrance-pipelines/pipeline/consent_gate.py`.
- The agent should use `claude-opus-4-8` with structured output, same shape as
  `node_scorer/agent.py`.
