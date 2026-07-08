"""
Node-Readiness Scorer (Cypher Build Spec Pack — Build 1).

Prospect in → score, routing, and drip-tier out. No Rob required to judge.

The scoring logic is encoded verbatim from the Cypher Logic Model §06
(reproduced in the Build Spec Pack, pp. 2–3): 7 dimensions, 3 gates, and the
16–21 / 11–15 / <11 routing bands. This package is the portable Python core;
`airtable_sync` is an optional adapter to the "Cypher 2026" Airtable base.
"""

from .models import DimensionScore, Prospect, Scorecard  # noqa: F401
from .rubric import load_rubric  # noqa: F401
from .scorer import score_prospect  # noqa: F401
from .drip import handoff, draft_opener  # noqa: F401

__all__ = [
    "DimensionScore",
    "Prospect",
    "Scorecard",
    "load_rubric",
    "score_prospect",
    "handoff",
    "draft_opener",
]
