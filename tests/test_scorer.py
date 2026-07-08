"""
Tests for the Node-Readiness Scorer (Build 1).

Mirrors the pack's "done when" bar (pp. 2–3):
  - Silence Kills → STAND_UP_NODE (the first-test fixture).
  - Any gate = 1 forces NURTURE_ONLY regardless of a high raw total.
  - A missing evidence line → "insufficient data" flag, never a guessed number.
  - Boundary totals (10/11/15/16) route to the correct band.

Fixtures are built in-memory (no network, no PII) except the one test that
loads the repo's silence_kills.json.
"""

from __future__ import annotations

import json
from pathlib import Path

from node_scorer.models import DimensionScore, Prospect
from node_scorer.rubric import load_rubric
from node_scorer.scorer import score_prospect

RUBRIC = load_rubric()
FIXTURE = Path(__file__).parent.parent / "node_scorer" / "prospects" / "silence_kills.json"


def make_prospect(scores: dict[str, int | None], org: str = "Test Org") -> Prospect:
    """Build a prospect where every rubric dimension gets `scores[key]` with a
    boilerplate evidence line (None score → no evidence, i.e. insufficient)."""
    dims = []
    for spec in RUBRIC.dimensions:
        s = scores.get(spec.key)
        dims.append(DimensionScore(
            key=spec.key, label=spec.label, is_gate=spec.gate,
            score=s, evidence=(f"evidence for {spec.key}" if s is not None else None),
        ))
    return Prospect(org=org, dimensions=dims)


def all_scores(value: int) -> dict[str, int]:
    return {spec.key: value for spec in RUBRIC.dimensions}


# ── The rubric is encoded as the pack specifies ─────────────────────────────

def test_seven_dimensions_three_gates():
    assert len(RUBRIC.dimensions) == 7
    assert set(RUBRIC.gate_keys) == {"elder_access", "consent_capacity", "reciprocity_fit"}


# ── Routing bands ───────────────────────────────────────────────────────────

def test_all_threes_stands_up_node():
    card = score_prospect(make_prospect(all_scores(3)), RUBRIC)
    assert card.total == 21
    assert card.verdict == "STAND_UP_NODE"
    assert card.drip_tier == "Engaged"


def test_boundary_16_stands_up():
    # 16 total, gates all >= 2 → STAND_UP_NODE (band floor).
    scores = {"community_trust": 3, "gathering_space": 2, "elder_access": 2,
              "consent_capacity": 2, "funding_alignment": 3, "cobranding_will": 2,
              "reciprocity_fit": 2}
    assert sum(scores.values()) == 16
    card = score_prospect(make_prospect(scores), RUBRIC)
    assert card.verdict == "STAND_UP_NODE"


def test_boundary_15_refines():
    # 15 total, no gate at 1 → REFINE_DRIP (top of the middle band).
    scores = {"community_trust": 3, "gathering_space": 2, "elder_access": 2,
              "consent_capacity": 2, "funding_alignment": 2, "cobranding_will": 2,
              "reciprocity_fit": 2}
    assert sum(scores.values()) == 15
    card = score_prospect(make_prospect(scores), RUBRIC)
    assert card.verdict == "REFINE_DRIP"
    assert card.drip_tier == "Warm"


def test_boundary_11_refines():
    scores = {"community_trust": 2, "gathering_space": 2, "elder_access": 2,
              "consent_capacity": 2, "funding_alignment": 1, "cobranding_will": 1,
              "reciprocity_fit": 1}
    # reciprocity_fit is a gate at 1 → this would override; bump it to isolate the band.
    scores["reciprocity_fit"] = 2
    scores["community_trust"] = 1  # keep total at 11
    assert sum(scores.values()) == 11
    card = score_prospect(make_prospect(scores), RUBRIC)
    assert card.verdict == "REFINE_DRIP"


def test_low_total_nurtures():
    scores = all_scores(1)  # every dimension weak; gates at 1 also override
    card = score_prospect(make_prospect(scores), RUBRIC)
    assert card.verdict == "NURTURE_ONLY"
    assert card.drip_tier == "Cold"


# ── Gate override: a weak gate beats a high total ───────────────────────────

def test_gate_one_overrides_high_total():
    scores = all_scores(3)
    scores["elder_access"] = 1          # a single weak gate
    card = score_prospect(make_prospect(scores), RUBRIC)
    assert card.total == 19             # raw total is still high
    assert card.verdict == "NURTURE_ONLY"   # ...but the gate overrides
    assert "elder_access" in card.triggered_gates
    assert card.gate_triggered is True


def test_nongate_one_does_not_override():
    scores = all_scores(3)
    scores["community_trust"] = 1       # weak NON-gate dimension
    card = score_prospect(make_prospect(scores), RUBRIC)
    assert card.gate_triggered is False
    assert card.verdict == "STAND_UP_NODE"


# ── Evidence layer: gaps are flagged, never faked ───────────────────────────

def test_missing_evidence_flags_insufficient_not_guessed():
    scores = all_scores(3)
    scores["gathering_space"] = None    # unscored, no evidence
    card = score_prospect(make_prospect(scores), RUBRIC)
    # The missing dimension is not in the scored set...
    assert all(d.key != "gathering_space" for d in card.dimensions)
    # ...and it's flagged as insufficient data, never assigned a number.
    assert any("insufficient data" in f for f in card.flags)


def test_missing_gate_evidence_routes_to_nurture_with_question():
    scores = all_scores(3)
    scores["elder_access"] = None       # gate with no evidence → unknown
    card = score_prospect(make_prospect(scores), RUBRIC)
    assert card.verdict == "NURTURE_ONLY"
    assert "elder_access" in card.triggered_gates
    assert any("Ask next contact" in f for f in card.flags)


# ── Conflicting evidence is surfaced, not averaged ──────────────────────────

def test_conflict_surfaces_tension_flag():
    scores = all_scores(3)
    scores["reciprocity_fit"] = 1       # strong everywhere, weak gate
    card = score_prospect(make_prospect(scores), RUBRIC)
    assert any("TENSION" in f for f in card.flags)


# ── Re-score diff ───────────────────────────────────────────────────────────

def test_rescore_diff_note():
    p = make_prospect(all_scores(3))
    p.prior_total = 15
    card = score_prospect(p, RUBRIC)
    assert card.diff_note is not None
    assert "15" in card.diff_note and "21" in card.diff_note


# ── First test from the pack: Silence Kills ─────────────────────────────────

def test_silence_kills_stands_up_node():
    """The pack's run-one: Silence Kills (DC), 501(c)(3) confirmed, gates strong."""
    from node_scorer.cli import load_prospect

    card = score_prospect(load_prospect(FIXTURE, RUBRIC), RUBRIC)
    assert card.verdict == "STAND_UP_NODE", (
        f"Expected STAND_UP_NODE; got {card.verdict} at total {card.total}. "
        "If the scorer disagrees with Rob's gut, THAT gap is the valuable output."
    )
    assert not card.gate_triggered
    # Every scored dimension carries an evidence line (Block 04).
    assert all(d.evidence for d in card.dimensions)


def test_fixture_has_no_pii_contact_value():
    """Guardrail: the committed fixture must not carry a real contact detail."""
    data = json.loads(FIXTURE.read_text())
    assert "@" not in data["contact"]
    assert "omitted" in data["contact"].lower()
