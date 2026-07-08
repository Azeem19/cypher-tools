# cypher-tools

Grant pipeline intelligence and client-facing tools for Cypher LLC — the
command center for the **Cypher Build Spec Pack** (five agentic builds that clone
Rob's judgment and labor off the revenue path).

## Start here

- **[BUILD_PLAN.md](BUILD_PLAN.md)** — the durable 5-build roadmap and status.
  This is the retrievable plan: `git pull` it over the iPad/Tailscale terminal or
  read it on GitHub.

## Builds living here

| Build | Dir | Status |
|-------|-----|--------|
| 1 · Node-Readiness Scorer | [`node_scorer/`](node_scorer/) | ✅ built + tested |
| 2 · Grant RFA Decomposer | [`grant_decomposer/`](grant_decomposer/) | 🟡 scaffolded |
| 3 · Speaker-Bio Composer | (planned) | ⚪ roadmap |
| 4 · Lineage-to-Content Mapper | (planned) | ⚪ roadmap |

Build 5 (Ancestor Search RAG) is a stub in `remembrance-pipelines/rag_stub/`.

## Quick start (Build 1)

```bash
python3 -m pip install -r requirements.txt
python -m node_scorer score node_scorer/prospects/silence_kills.json
python -m pytest tests/ -q
```

## Standards
Python 3.11 · Claude API (`claude-opus-4-8` for agent work — latest/most capable;
override per tool if needed) · Airtable API. No client data or secrets in this
repo — use env vars. Brand: Du Bois teal `#215244` · gold `#B37602`.
