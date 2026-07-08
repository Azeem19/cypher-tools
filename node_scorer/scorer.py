"""
The scoring engine (Build 1, Blocks 02–03) + the router.

Pure functions, no I/O. Given a Prospect and a Rubric, produce a Scorecard:
sum the dimensions, apply the gate override, route to a verdict + drip tier.

The gate override is the same shape as remembrance-pipelines' consent_gate: a
single blocking check that overrides all downstream state. Here, any gate
dimension that reads weak (score 1) OR unknown (no evidence) forces
NURTURE_ONLY regardless of the raw total — sovereignty, reverence, and
reciprocity are never traded for a high number.
"""

from __future__ import annotations

from .evidence import audit, tension_flags
from .models import Prospect, Scorecard
from .rubric import Rubric, load_rubric


def _weak_gates(prospect: Prospect, rubric: Rubric) -> list[str]:
    """Gate dimensions that scored exactly 1 (weak)."""
    by_key = {d.key: d for d in prospect.dimensions}
    weak = []
    for spec in rubric.dimensions:
        if not spec.gate:
            continue
        dim = by_key.get(spec.key)
        if dim is not None and dim.score == 1:
            weak.append(spec.key)
    return weak


def score_prospect(prospect: Prospect, rubric: Rubric | None = None) -> Scorecard:
    """Score one prospect → Scorecard. Loads the default rubric if none given."""
    rubric = rubric or load_rubric()

    result = audit(prospect, rubric)
    scored_dims = result["scored_dims"]
    flags = list(result["flags"])

    # Total is the sum of dimensions that carry a real, evidenced score. A
    # missing dimension contributes nothing (never a guessed number), which
    # conservatively pulls the total toward nurture — the safe direction.
    total = sum(d.score for d in scored_dims)

    weak_gates = _weak_gates(prospect, rubric)
    unknown_gates = result["unknown_gates"]
    triggered_gates = weak_gates + unknown_gates
    gate_triggered = bool(triggered_gates)

    # Surface conflicting-evidence tensions before deciding the verdict.
    flags.extend(tension_flags(prospect, rubric, weak_gates))

    if gate_triggered:
        verdict = rubric.gate_override_verdict
        drip_tier = rubric.gate_override_drip
        routing_note = rubric.gate_override_note
    else:
        band = rubric.route(total)
        verdict = band.verdict
        drip_tier = band.drip_tier
        routing_note = band.note

    # Re-score diff (Block 05 edge case): note what changed vs the prior total.
    diff_note = None
    if prospect.prior_total is not None:
        delta = total - prospect.prior_total
        direction = "up" if delta > 0 else "down" if delta < 0 else "unchanged"
        diff_note = (
            f"Re-score: {prospect.prior_total} → {total} ({direction}"
            + (f" {delta:+d}" if delta else "") + ")."
        )

    return Scorecard(
        org=prospect.org,
        total=total,
        verdict=verdict,
        drip_tier=drip_tier,
        routing_note=routing_note,
        dimensions=scored_dims,
        gate_triggered=gate_triggered,
        triggered_gates=triggered_gates,
        flags=flags,
        diff_note=diff_note,
    )
