"""
The Judgment Clone (Build 1, Block 05).

An Anthropic-API agent that reads free-text discovery notes and PROPOSES the 7
dimension scores + a one-line evidence quote each, for Rob's review. This is the
block that removes Rob from the critical path: paste call notes, get back a
drafted scorecard you only need to approve.

Design rules straight from the pack:
  - The agent DRAFTS; it never auto-approves. Output is a proposal.
  - It must quote evidence for every score. Where the notes don't support a
    dimension, it returns null (→ the evidence layer flags "insufficient data",
    never a guessed number).
  - It surfaces conflicting evidence rather than averaging it away.

The `anthropic` SDK is an OPTIONAL dependency, imported lazily so the scoring
core runs fully offline (Mini or iPad terminal) with zero network deps.
Model + call shape follow the `claude-api` skill: claude-opus-4-8, adaptive
thinking, structured output via output_config.format.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import DimensionScore, Prospect, Scorecard
from .rubric import Rubric, load_rubric
from .scorer import score_prospect

MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = """\
You are the Node-Readiness judgment clone for Cypher x Remembrance. You read raw
discovery notes about a prospective Remembrance node (a community organization)
and propose a score for each of 7 dimensions, each 1 (weak) / 2 (present) /
3 (strong), plus one direct evidence quote from the notes for each score.

Non-negotiable rules:
- Score ONLY from evidence in the notes. If the notes do not support a dimension,
  set its score to null and its evidence to null — never guess a number.
- The three gates (elder access, consent capacity, reciprocity fit) are the
  studio's non-negotiables: sovereignty, reverence, reciprocity. Be conservative
  on gates — if elder access or genuine reciprocity isn't clearly evidenced, do
  not inflate it.
- If evidence conflicts (e.g. strong community trust but weak reciprocity), score
  each dimension on its own evidence. Do not average the tension away.
You are drafting for human review, not deciding. Rob approves every scorecard."""


def _schema(rubric: Rubric) -> dict:
    """JSON schema for the structured output: one score+evidence per dimension."""
    props = {}
    for spec in rubric.dimensions:
        props[spec.key] = {
            "type": "object",
            "properties": {
                "score": {"type": ["integer", "null"], "enum": [1, 2, 3, None]},
                "evidence": {"type": ["string", "null"]},
            },
            "required": ["score", "evidence"],
            "additionalProperties": False,
        }
    return {
        "type": "object",
        "properties": props,
        "required": [s.key for s in rubric.dimensions],
        "additionalProperties": False,
    }


def draft_scores(notes: str, rubric: Rubric | None = None) -> dict:
    """Call Claude to propose per-dimension scores + evidence from `notes`.

    Returns the parsed dict {dimension_key: {"score": int|None, "evidence": str|None}}.
    Raises SystemExit with an actionable message if the SDK/key is unavailable.
    """
    rubric = rubric or load_rubric()

    try:
        import anthropic
    except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
        raise SystemExit(
            "The judgment-clone agent needs the Anthropic SDK. Install it with:\n"
            "    python3 -m pip install anthropic\n"
            "and set ANTHROPIC_API_KEY (or run `ant auth login`).\n"
            "The scorer itself runs offline without this — only `draft` needs it."
        ) from exc

    client = anthropic.Anthropic()  # resolves ANTHROPIC_API_KEY / ant profile
    dim_list = "\n".join(f"- {s.key}: {s.label}" + (" (GATE)" if s.gate else "")
                         for s in rubric.dimensions)

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high", "format": {
            "type": "json_schema", "schema": _schema(rubric),
        }},
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                f"The 7 dimensions to score (1/2/3, or null if unsupported):\n"
                f"{dim_list}\n\nDiscovery notes:\n\"\"\"\n{notes}\n\"\"\""
            ),
        }],
    )
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def draft_scorecard(prospect: Prospect, rubric: Rubric | None = None) -> Scorecard:
    """Read `prospect.notes` → drafted, scored Scorecard for review (Block 05).

    Populates the prospect's dimensions from the agent proposal, then runs the
    same deterministic scorer used everywhere else so the drafted verdict matches
    what an approved hand-entry would produce.
    """
    rubric = rubric or load_rubric()
    proposed = draft_scores(prospect.notes, rubric)

    prospect.dimensions = [
        DimensionScore(
            key=spec.key,
            label=spec.label,
            is_gate=spec.gate,
            score=proposed.get(spec.key, {}).get("score"),
            evidence=proposed.get(spec.key, {}).get("evidence"),
        )
        for spec in rubric.dimensions
    ]
    return score_prospect(prospect, rubric)
