"""Intervention catalog schema (roadmap P5.1, ADR 0006), validated with pydantic.

`InterventionCatalog` describes the catalog of candidate street interventions
a planner reviews before any package reaches the optimizer (P7): one
`CatalogEntry` per candidate, carrying its transform type, target edges/
junctions, free-form transform parameters, cost estimate, complexity,
legal/safety/equity notes, expected beneficiaries/losers, and which other
entries it cannot coexist with (`mutual_exclusions`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator

InterventionType = Literal[
    "one_way_conversion",
    "reversible_lane",
    "bus_lane",
    "lane_reallocation",
    "protected_bike_corridor",
    "pedestrian_street",
    "turn_restriction",
    "new_connector",
    "signal_retiming",
    "transit_signal_priority",
]
Complexity = Literal["low", "medium", "high"]


class CatalogEntry(BaseModel):
    id: str
    type: InterventionType
    description: str
    target_edges: list[str] = Field(default_factory=list)
    target_junctions: list[str] = Field(default_factory=list)
    parameters: dict = Field(default_factory=dict)
    cost_estimate_brl: float | None = None
    complexity: Complexity
    legal_constraints: list[str] = Field(default_factory=list)
    safety_notes: str | None = None
    emergency_access_notes: str | None = None
    equity_notes: str | None = None
    expected_beneficiaries: list[str] = Field(default_factory=list)
    expected_losers: list[str] = Field(default_factory=list)
    mutual_exclusions: list[str] = Field(default_factory=list)


class InterventionCatalog(BaseModel):
    entries: list[CatalogEntry] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_mutual_exclusions(self) -> InterventionCatalog:
        ids = {entry.id for entry in self.entries}
        errors: list[str] = []
        for entry in self.entries:
            for excluded_id in entry.mutual_exclusions:
                if excluded_id == entry.id:
                    errors.append(f"entry {entry.id!r} lists itself in mutual_exclusions")
                elif excluded_id not in ids:
                    errors.append(
                        f"entry {entry.id!r} has mutual_exclusions reference to "
                        f"unknown id {excluded_id!r}"
                    )
        if errors:
            raise ValueError("; ".join(errors))
        return self


def load_catalog(path: str | Path) -> InterventionCatalog:
    with open(path, encoding="utf-8") as f:
        return InterventionCatalog.model_validate(yaml.safe_load(f))
