"""
Rubric loader — reads rubric.yaml into typed structures.

Kept separate from scorer.py so the scoring logic stays pure and the rubric
stays data. PyYAML is the one third-party dependency; if it's missing we fail
with an actionable message instead of a bare ImportError.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
    raise SystemExit(
        "node_scorer needs PyYAML to read rubric.yaml. Install it with:\n"
        "    python3 -m pip install pyyaml\n"
    ) from exc

DEFAULT_RUBRIC = Path(__file__).with_name("rubric.yaml")


@dataclass(frozen=True)
class DimensionSpec:
    key: str
    label: str
    gate: bool


@dataclass(frozen=True)
class RoutingBand:
    min: int
    max: int
    verdict: str
    drip_tier: str
    note: str


@dataclass(frozen=True)
class Rubric:
    dimensions: tuple[DimensionSpec, ...]
    routing: tuple[RoutingBand, ...]
    gate_override_verdict: str
    gate_override_drip: str
    gate_override_note: str
    scale_min: int
    scale_max: int

    @property
    def gate_keys(self) -> tuple[str, ...]:
        return tuple(d.key for d in self.dimensions if d.gate)

    def route(self, total: int) -> RoutingBand:
        for band in self.routing:
            if band.min <= total <= band.max:
                return band
        # Total below the lowest band floor → treat as the lowest (nurture) band.
        return min(self.routing, key=lambda b: b.min)


def load_rubric(path: str | Path = DEFAULT_RUBRIC) -> Rubric:
    with Path(path).open() as f:
        raw = yaml.safe_load(f)

    dims = tuple(
        DimensionSpec(key=d["key"], label=d["label"], gate=bool(d.get("gate", False)))
        for d in raw["dimensions"]
    )
    routing = tuple(
        RoutingBand(
            min=int(b["min"]),
            max=int(b["max"]),
            verdict=b["verdict"],
            drip_tier=b["drip_tier"],
            note=b.get("note", ""),
        )
        for b in raw["routing"]
    )
    go = raw["gate_override"]
    scale = raw.get("scale", {})
    return Rubric(
        dimensions=dims,
        routing=routing,
        gate_override_verdict=go["verdict"],
        gate_override_drip=go["drip_tier"],
        gate_override_note=go.get("note", ""),
        scale_min=int(scale.get("min", 1)),
        scale_max=int(scale.get("max", 3)),
    )
