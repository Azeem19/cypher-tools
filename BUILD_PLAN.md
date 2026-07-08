# Cypher Build Spec Pack — Build Plan (Command Center)

> **This file is the durable, retrievable plan.** It lives in the `cypher-tools`
> repo (github.com/Azeem19/cypher-tools) so it's reachable from anywhere: `git
> pull` over the Blink/Tailscale terminal on the iPad, or read it on GitHub web.
> The Mac Mini is where building happens; this page is the blueprint room.

*"The future is built on the stories we choose to remember." — Robert Azeem Jackson III*

---

## The move (why these five builds exist)

Every build is the same act at a different scale: **encode a pattern Rob already
runs by hand, so it runs without him.** African Fractals as operating system —
one generative rule replicating from a single prospect to 38 grants. The
priority order is revenue-first, not interest-first: **Rob is the bottleneck in
the revenue path**, so Builds 1 & 2 (which clone judgment and labor on that path)
come first; 3 & 4 sharpen consistency; 5 is a captured stub.

## Roadmap

| # | Build | Path | Home repo | Status |
|---|-------|------|-----------|--------|
| 1 | **Node-Readiness Scorer** | low-code → Python | `cypher-tools/node_scorer/` | ✅ **BUILT** — validated on Silence Kills |
| 2 | **Grant RFA Decomposer** | low-code → Code | `cypher-tools/grant_decomposer/` | 🟡 scaffolded (spec + deps captured) |
| 3 | Speaker-Bio Composer | Code | `cypher-tools/` (planned) | ⚪ roadmap |
| 4 | Lineage-to-Content Mapper | Code | `cypher-tools/` (planned) | ⚪ roadmap |
| 5 | Ancestor Search RAG | Code + Ollama | `remembrance-pipelines/rag_stub/` | 🔒 STUB — do not build until 1–2 earn |

---

## Build 1 — Node-Readiness Scorer ✅

*Prospect in → score, routing, drip-tier out.* The first clone of Rob's judgment.
7 dimensions (1/2/3), 3 gates (elder access, consent capacity, reciprocity fit —
any at 1 → NURTURE), routing 16–21 / 11–15 / <11. Evidence required per score;
gaps flagged "insufficient data", never guessed.

- Code + docs: [`node_scorer/`](node_scorer/) · run `python -m node_scorer score node_scorer/prospects/silence_kills.json`
- Portable Python core (offline, iPad-terminal friendly) + optional Anthropic
  judgment-clone agent (Block 05) + optional Airtable sync adapter.
- **Done-when met:** correct total/verdict/drip + per-dimension evidence; gates
  override; `silence_kills.json` → `STAND_UP_NODE`; `draft` returns a scorecard
  to approve. Tests: `python -m pytest tests/ -q`.

## Build 2 — Grant RFA Decomposer 🟡

*Grant guidelines in → role-split work plan out, across the 38-grant playbook.*
Turns the hand-built 74-row PABC role-split into a generator. Spec + Lego blocks:
[`grant_decomposer/README.md`](grant_decomposer/README.md).

**Blocked on source docs not yet in-repo** (see that README): the Logic Model,
the existing 74-row role-split, and `Cypher_Grant_Playbook_Feb2026.docx`. Nearby
and usable for the angle layer: the Silence Kills SOW/MOU and the TheSweet
Partnership Canvas under `~/Documents/Claude/Projects/`. Run one = **PABC
FY2027** (eligibility GREEN — Silence Kills is confirmed 501(c)(3)).

## Build 3 — Speaker-Bio Composer ⚪

Versioned, dated fact base → portal-tailored bios. **Block 02 is the point:** a
tense guardrail that refuses to state a Vision-2031 roadmap claim in the present
tense. Length cuts (2-line / 75w / 120w / full), per-portal framing, auto-lineage
line. Full Code, small agent over a facts file.

## Build 4 — Lineage-to-Content Mapper ⚪

Pantheon file (topic → 2–3 ancestors) → tagger → consistency check → paste-ready
citation line. Keeps intellectual lineage self-similar across every surface.

## Build 5 — Ancestor Search RAG 🔒 STUB

Local, consent-gated RAG over the elder archive: Mini + Ollama + Tailscale,
nothing leaves the machine. Architecture only:
[`../remembrance-pipelines/rag_stub/ARCHITECTURE.md`]. **Revisit only after Builds
1–2 are live and generating revenue.**

---

## Working discipline

- **Architect from the page; build in the terminal.** Every build/debug/commit
  happens in Claude Code on the Mini (directly or over Tailscale).
- **Portability:** anything that must survive the Mini↔dad's-iPad move is committed
  and pushed here. This plan is retrievable via `git pull` or GitHub web.
- **Mandate:** no client PII / secrets in commit history; check `consent.yaml`
  before any audio/text processing; synthetic data documented as such.
