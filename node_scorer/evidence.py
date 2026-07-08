"""
The Evidence Layer (Build 1, Block 04).

Non-negotiable rule from the pack: no score exists without a justifying line;
gaps are flagged, never faked. A dimension with no one-line evidence quote is
reported as "insufficient data" and added to the flag list — it is never
assigned a guessed number.

This module also encodes the p.3 edge cases:
  - Missing gate evidence  → the gate reads "unknown", which the scorer routes
    to nurture, and we attach the specific question to ask the next contact.
  - Conflicting evidence   → surface the tension (strong elsewhere, weak gate);
    do not average it away.
"""

from __future__ import annotations

from .models import INSUFFICIENT, Prospect
from .rubric import Rubric

# The specific next-question to ask when a gate lacks evidence. Phrased so Rob
# (or the drip) can drop it straight into the follow-up.
GATE_QUESTIONS = {
    "elder_access": "Who are the elders in this community, and would they sit with us?",
    "consent_capacity": "Does the org have the capacity and will to run consent-first intake?",
    "reciprocity_fit": "What does this community get back — is the exchange genuinely mutual?",
}


def _valid_score(score, rubric: Rubric) -> bool:
    return isinstance(score, int) and rubric.scale_min <= score <= rubric.scale_max


def audit(prospect: Prospect, rubric: Rubric) -> dict:
    """Audit a prospect's dimensions against the rubric.

    Returns a dict with:
      scored_dims       — list[DimensionScore] that carry a valid score + evidence
      insufficient      — list of dimension keys with no usable score/evidence
      unknown_gates     — list of gate keys missing evidence (route to nurture)
      flags             — human-readable flag strings (insufficient data + questions)
    """
    scored, insufficient, unknown_gates, flags = [], [], [], []
    by_key = {d.key: d for d in prospect.dimensions}

    for spec in rubric.dimensions:
        dim = by_key.get(spec.key)
        usable = (
            dim is not None
            and dim.has_evidence
            and _valid_score(dim.score, rubric)
        )
        if usable:
            scored.append(dim)
            continue

        insufficient.append(spec.key)
        flags.append(f"{spec.label}: {INSUFFICIENT} — no scored evidence line.")
        if spec.gate:
            unknown_gates.append(spec.key)
            q = GATE_QUESTIONS.get(spec.key)
            if q:
                flags.append(f"Ask next contact ({spec.label}): {q}")

    return {
        "scored_dims": scored,
        "insufficient": insufficient,
        "unknown_gates": unknown_gates,
        "flags": flags,
    }


def tension_flags(prospect: Prospect, rubric: Rubric, weak_gates: list[str]) -> list[str]:
    """Surface conflicting evidence rather than averaging it away.

    When a gate reads weak (1) while the non-gate dimensions read strong, that
    tension is the signal — name it explicitly.
    """
    flags: list[str] = []
    by_key = {d.key: d for d in prospect.dimensions}
    non_gate_scores = [
        by_key[s.key].score
        for s in rubric.dimensions
        if not s.gate and s.key in by_key and isinstance(by_key[s.key].score, int)
    ]
    strong_elsewhere = non_gate_scores and (sum(non_gate_scores) / len(non_gate_scores)) >= 2.5
    for gk in weak_gates:
        label = next((s.label for s in rubric.dimensions if s.key == gk), gk)
        if strong_elsewhere:
            flags.append(
                f"TENSION: {label} reads weak while the rest reads strong — "
                f"do not average it away; the gate governs."
            )
    return flags
