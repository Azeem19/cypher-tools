"""
Record shapes for the Node-Readiness Scorer.

Single source of truth for the prospect + scorecard structure. These fields
mirror the Airtable "Node Prospects" table (Build 1, Block 01) so the portable
Python core and the optional Airtable sync adapter never drift.

Stdlib-only (dataclasses) — keeps the core runnable offline on the Mini or over
the iPad terminal with no third-party imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional

# Sentinel used when a dimension has no supporting evidence. Per the pack
# (Block 04): an unscored dimension is "insufficient data", never a guessed
# number.
INSUFFICIENT = "insufficient data"


@dataclass
class DimensionScore:
    """One rubric dimension: its 1/2/3 score and the one-line evidence quote.

    `score` is None when there is no evidence — the scorer treats that as
    insufficient data and flags it rather than inventing a number.
    """

    key: str
    label: str
    is_gate: bool
    score: Optional[int] = None          # 1, 2, 3, or None (insufficient)
    evidence: Optional[str] = None       # one-line justifying quote from notes

    @property
    def has_evidence(self) -> bool:
        return bool(self.evidence and self.evidence.strip())

    @property
    def is_scored(self) -> bool:
        return self.score is not None and self.has_evidence


@dataclass
class Prospect:
    """A node prospect entered by hand (Block 01) or drafted by the agent (Block 05)."""

    org: str
    city: str = ""
    contact: str = ""
    source: str = ""                     # speaking gig, referral, inbound
    notes: str = ""                      # free-text discovery notes
    dimensions: list[DimensionScore] = field(default_factory=list)
    # Optional prior scorecard total, used by the re-score diff (Block 05 edge case).
    prior_total: Optional[int] = None

    def dimension(self, key: str) -> Optional[DimensionScore]:
        for d in self.dimensions:
            if d.key == key:
                return d
        return None


@dataclass
class Scorecard:
    """The scorer's output for one prospect (Blocks 02–04, 06)."""

    org: str
    total: int
    verdict: str                         # STAND_UP_NODE | REFINE_DRIP | NURTURE_ONLY
    drip_tier: str                       # Engaged | Warm | Cold
    routing_note: str
    dimensions: list[DimensionScore] = field(default_factory=list)
    gate_triggered: bool = False         # True when a gate override fired
    triggered_gates: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)   # insufficient-data + tensions
    diff_note: Optional[str] = None      # re-score delta vs prior_total
    opener: Optional[str] = None         # drafted first-touch line (Block 06)

    def to_dict(self) -> dict:
        return asdict(self)
