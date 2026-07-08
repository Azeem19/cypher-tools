"""
The Drip Handoff (Build 1, Block 06).

A routed prospect auto-places into the correct drip tier and gets a drafted
first-touch line in brand voice for Richard. Template-based (no API needed) so
it runs offline; the agent layer (agent.py) can later refine the wording.

Brand voice: warm, sovereign, reciprocity-first. Never over-promises; a
STAND-UP opener invites, a REFINE opener stays in relationship, a NURTURE
opener keeps the door open without pushing.
"""

from __future__ import annotations

from .models import Scorecard

# Drafted first-touch openers keyed by verdict. `{org}` is filled per prospect.
# Kept short — these are first touches for Richard to adapt, not final copy.
_OPENERS = {
    "STAND_UP_NODE": (
        "Hi — after our conversation about {org}, I think there's real alignment "
        "here. We'd love to explore standing up a Remembrance node together, on "
        "your community's terms. Could we find 30 minutes to map what that looks like?"
    ),
    "REFINE_DRIP": (
        "Hi — I've been thinking about {org} since we spoke. There's a genuine "
        "foundation here; I'd love to keep the conversation going and understand a "
        "few things better before we talk next steps. Open to a follow-up soon?"
    ),
    "NURTURE_ONLY": (
        "Hi — thank you for the conversation about {org}. I want to make sure "
        "anything we build together is fully on your community's terms, so I'd "
        "rather move at the right pace. I'll stay in touch and share things I "
        "think you'll value."
    ),
}


def draft_opener(scorecard: Scorecard) -> str:
    """Return a brand-voice first-touch line for the scorecard's verdict."""
    template = _OPENERS.get(scorecard.verdict, _OPENERS["NURTURE_ONLY"])
    return template.format(org=scorecard.org or "your organization")


def handoff(scorecard: Scorecard) -> Scorecard:
    """Attach the drafted opener to the scorecard and return it (Block 06 done)."""
    scorecard.opener = draft_opener(scorecard)
    return scorecard
