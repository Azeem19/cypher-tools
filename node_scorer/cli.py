"""
Terminal-first CLI for the Node-Readiness Scorer (Build 1).

Works over the Blink/Tailscale tunnel from the iPad, or locally on the Mini:

    python -m node_scorer score node_scorer/prospects/silence_kills.json
    python -m node_scorer draft call_notes.txt --org "Silence Kills" --city DC

`score` runs fully offline. `draft` needs the Anthropic SDK + a key (Block 05).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .drip import handoff
from .models import DimensionScore, Prospect, Scorecard
from .rubric import Rubric, load_rubric
from .scorer import score_prospect

# Du Bois palette (brand standard) — used only for terminal cues, no hard dep.
_TEAL, _GOLD, _RED, _RESET = "\033[36m", "\033[33m", "\033[31m", "\033[0m"


def load_prospect(path: str | Path, rubric: Rubric) -> Prospect:
    """Load a prospect JSON file into a Prospect with rubric-aligned dimensions.

    Expected shape (see prospects/silence_kills.json):
      {org, city, contact, source, notes, prior_total?,
       dimensions: {<key>: {score: 1|2|3|null, evidence: str|null}, ...}}
    Dimensions absent from the file are left unscored (→ insufficient data).
    """
    data = json.loads(Path(path).read_text())
    dims_in = data.get("dimensions", {})
    dimensions = [
        DimensionScore(
            key=spec.key,
            label=spec.label,
            is_gate=spec.gate,
            score=dims_in.get(spec.key, {}).get("score"),
            evidence=dims_in.get(spec.key, {}).get("evidence"),
        )
        for spec in rubric.dimensions
    ]
    return Prospect(
        org=data.get("org", "(unnamed)"),
        city=data.get("city", ""),
        contact=data.get("contact", ""),
        source=data.get("source", ""),
        notes=data.get("notes", ""),
        dimensions=dimensions,
        prior_total=data.get("prior_total"),
    )


def _verdict_color(verdict: str) -> str:
    return {"STAND_UP_NODE": _TEAL, "REFINE_DRIP": _GOLD}.get(verdict, _RED)


def render(card: Scorecard, use_color: bool = True) -> str:
    """Human-readable scorecard for the terminal."""
    def c(code: str, text: str) -> str:
        return f"{code}{text}{_RESET}" if use_color else text

    lines = [
        f"Node-Readiness Scorecard — {card.org}",
        "=" * 48,
    ]
    for d in card.dimensions:
        gate = " [gate]" if d.is_gate else ""
        lines.append(f"  {d.label:<18} {d.score}{gate}")
        if d.evidence:
            lines.append(f"      ↳ \"{d.evidence}\"")
    lines.append("-" * 48)
    lines.append(f"  Total:     {card.total} / 21")
    lines.append(f"  Verdict:   {c(_verdict_color(card.verdict), card.verdict)}")
    lines.append(f"  Drip tier: {card.drip_tier}")
    lines.append(f"  {card.routing_note}")
    if card.gate_triggered:
        lines.append(c(_RED, f"  GATE OVERRIDE: {', '.join(card.triggered_gates)}"))
    if card.diff_note:
        lines.append(f"  {card.diff_note}")
    if card.flags:
        lines.append("  Flags:")
        lines.extend(f"    - {f}" for f in card.flags)
    if card.opener:
        lines.append("-" * 48)
        lines.append("  Drafted first-touch (for Richard):")
        lines.append(f"    {card.opener}")
    return "\n".join(lines)


def _cmd_score(args: argparse.Namespace) -> int:
    rubric = load_rubric()
    card = handoff(score_prospect(load_prospect(args.prospect, rubric), rubric))
    if args.json:
        print(json.dumps(card.to_dict(), indent=2))
    else:
        print(render(card, use_color=sys.stdout.isatty()))
    return 0


def _cmd_draft(args: argparse.Namespace) -> int:
    # Import here so `score` never pulls in the optional agent path.
    from .agent import draft_scorecard

    rubric = load_rubric()
    notes = Path(args.notes).read_text()
    prospect = Prospect(org=args.org, city=args.city, source=args.source, notes=notes)
    card = handoff(draft_scorecard(prospect, rubric))
    print("[DRAFT — review before approving]\n")
    if args.json:
        print(json.dumps(card.to_dict(), indent=2))
    else:
        print(render(card, use_color=sys.stdout.isatty()))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="node_scorer", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_score = sub.add_parser("score", help="Score a prospect JSON file (offline)")
    p_score.add_argument("prospect", help="Path to a prospect JSON file")
    p_score.add_argument("--json", action="store_true", help="Emit JSON, not a table")
    p_score.set_defaults(func=_cmd_score)

    p_draft = sub.add_parser("draft", help="Draft a scorecard from call notes (needs API)")
    p_draft.add_argument("notes", help="Path to a free-text notes file")
    p_draft.add_argument("--org", required=True, help="Prospect org name")
    p_draft.add_argument("--city", default="", help="Prospect city")
    p_draft.add_argument("--source", default="", help="Lead source")
    p_draft.add_argument("--json", action="store_true", help="Emit JSON, not a table")
    p_draft.set_defaults(func=_cmd_draft)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
