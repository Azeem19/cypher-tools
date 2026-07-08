# Node-Readiness Scorer — Build 1

*Prospect in → score, routing, and drip-tier out. No Rob required to judge.*

This is the first literal clone of Rob's prospect judgment (Cypher Build Spec
Pack, Build 1). The scoring logic is **not invented here** — it's the Cypher
Logic Model §06, encoded verbatim (7 dimensions, 3 gates, routing bands) in
[`rubric.yaml`](rubric.yaml) so it runs without Rob reading each prospect.

## The rubric (from the pack, pp. 2–3)

- **7 dimensions**, each scored 1 (weak) / 2 (present) / 3 (strong):
  community trust · gathering space · elder access\* · consent capacity\* ·
  funding alignment · co-branding will · reciprocity fit\*
- **3 gates** (`*`) — sovereignty, reverence, reciprocity. **Any gate at 1
  overrides the total → NURTURE.** The gates are the things the studio never trades.
- **Routing:** 16–21 → `STAND_UP_NODE` · 11–15 → `REFINE_DRIP` ·
  <11 or any gate=1 → `NURTURE_ONLY`.
- **Evidence layer:** every score needs a one-line quote. No evidence →
  `insufficient data` flag, **never a guessed number**.

## Portable by design

The core is standard-library + `pyyaml` only, so it runs offline on the Mac Mini
or over the iPad/Tailscale terminal. The Anthropic agent and the Airtable sync
are optional, import-guarded add-ons — the scorer never needs the network.

## Install

```bash
python3 -m pip install pyyaml            # core
python3 -m pip install anthropic         # optional: the `draft` agent (Block 05)
python3 -m pip install requests          # optional: Airtable sync
```

## Use

Score a prospect (offline):

```bash
python -m node_scorer score node_scorer/prospects/silence_kills.json
```

Draft a scorecard from raw call notes for review (needs `ANTHROPIC_API_KEY` or
`ant auth login`) — this is the block that removes Rob:

```bash
python -m node_scorer draft call_notes.txt --org "New Org" --city "DC"
```

Sync a score to the "Cypher 2026" Airtable base (optional):

```python
from node_scorer import load_rubric, score_prospect
from node_scorer.cli import load_prospect
from node_scorer.airtable_sync import push   # needs AIRTABLE_* env vars

r = load_rubric()
push(score_prospect(load_prospect("node_scorer/prospects/silence_kills.json", r), r))
```

## Files → Lego blocks

| File | Block |
|------|-------|
| `rubric.yaml` / `rubric.py` | 01/02 — the table + the rubric, encoded |
| `scorer.py` | 02/03 — scoring engine + router |
| `evidence.py` | 04 — evidence layer (no faked scores) |
| `agent.py` | 05 — the judgment clone (drafts for review) |
| `drip.py` | 06 — drip handoff + brand-voice opener |
| `airtable_sync.py` | 01 — optional Airtable adapter |
| `prospects/silence_kills.json` | first test → expected `STAND_UP_NODE` |

## Test

```bash
cd cypher-tools && python -m pytest tests/ -q
```

Brand palette: Du Bois teal `#215244` · gold `#B37602` · red `#A63228`.
No client PII in this repo — the Silence Kills fixture uses public 501(c)(3)
status and already-shared context only.
