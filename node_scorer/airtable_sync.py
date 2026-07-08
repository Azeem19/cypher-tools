"""
Optional Airtable sync adapter (Build 1, Block 01 mapping).

Pushes a scored Scorecard to the "Cypher 2026" Airtable base's Node Prospects
table. IMPORT-GUARDED: the scoring core never imports `requests`, so it runs
fully offline on the Mini or over the iPad terminal. This adapter is only used
when Rob chooses to sync — live Airtable provisioning is deferred.

Config via environment (never hard-code keys — no PII/secrets in the repo):
    AIRTABLE_API_KEY   personal access token
    AIRTABLE_BASE_ID   the "Cypher 2026" base id (app...)
    AIRTABLE_TABLE     table name (default: "Node Prospects")

The field mapping mirrors models.Scorecard / the pack's Block 01 schema so the
Python core and the Airtable table never drift.
"""

from __future__ import annotations

import os

from .models import Scorecard

API_ROOT = "https://api.airtable.com/v0"


def scorecard_to_fields(card: Scorecard) -> dict:
    """Map a Scorecard to Airtable field names (Block 01 schema)."""
    fields = {
        "org": card.org,
        "total": card.total,
        "verdict": card.verdict,
        "drip-tier": card.drip_tier,
        "notes": card.routing_note,
    }
    # Per-dimension score columns + a rolled-up evidence/flag note.
    for d in card.dimensions:
        fields[d.key] = d.score
    note_bits = [f"{d.label}: {d.evidence}" for d in card.dimensions if d.evidence]
    note_bits += card.flags
    if card.opener:
        note_bits.append(f"First-touch: {card.opener}")
    fields["evidence"] = "\n".join(note_bits)
    return fields


def push(card: Scorecard, base_id: str | None = None, table: str | None = None) -> dict:
    """Create a Node Prospects record in Airtable from a Scorecard.

    Returns the created record dict. Raises SystemExit with an actionable
    message if `requests` or the env config is missing.
    """
    try:
        import requests
    except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
        raise SystemExit(
            "Airtable sync needs `requests`. Install it with:\n"
            "    python3 -m pip install requests\n"
            "The scorer itself runs offline without this."
        ) from exc

    api_key = os.environ.get("AIRTABLE_API_KEY")
    base_id = base_id or os.environ.get("AIRTABLE_BASE_ID")
    table = table or os.environ.get("AIRTABLE_TABLE", "Node Prospects")
    if not api_key or not base_id:
        raise SystemExit(
            "Set AIRTABLE_API_KEY and AIRTABLE_BASE_ID (the Cypher 2026 base id) "
            "in the environment before syncing."
        )

    resp = requests.post(
        f"{API_ROOT}/{base_id}/{table}",
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"},
        json={"fields": scorecard_to_fields(card)},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
