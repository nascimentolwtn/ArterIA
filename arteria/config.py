"""City config and data-manifest schemas (ADR 0003), validated with pydantic.

`CityConfig` and `DataManifest` describe the two files every `cities/<city>/`
directory carries: `city.yaml` (area, CRS, time windows, SUMO version pin) and
`data-manifest.yaml` (one entry per data source, with license/visibility/status).
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

Visibility = Literal["public", "restricted"]
# `declined` (ADR 0013): a permanent owner policy choice never to request or
# use this source (e.g. real OD survey microdata, for privacy/re-identification
# risk) — unlike `deferred`, it does not expect a future request.
ManifestStatus = Literal[
    "public_available", "deferred", "requested", "received", "unavailable", "declined"
]


class TimeWindow(BaseModel):
    start: str
    end: str


class CityConfig(BaseModel):
    name: str
    crs: str
    sumo_version: str
    bounding_polygon: dict | None = None
    time_windows: dict[str, TimeWindow] = Field(default_factory=dict)
    data_manifest: str = "data-manifest.yaml"
    # IBGE municipality code (7 digits) and state abbreviation, for joining
    # Censo data (roadmap P3.2, ADR 0017) — optional since not every city a
    # future onboarding adds is necessarily Brazilian.
    ibge_municipality_code: str | None = None
    uf: str | None = None


class DataManifestEntry(BaseModel):
    id: str
    name: str
    description: str
    roadmap_ref: str
    agency: str
    license: str
    visibility: Visibility
    status: ManifestStatus
    sha256: str | None = None
    notes: str | None = None


class DataManifest(BaseModel):
    sources: list[DataManifestEntry] = Field(default_factory=list)


def load_city_config(path: str | Path) -> CityConfig:
    with open(path, encoding="utf-8") as f:
        return CityConfig.model_validate(yaml.safe_load(f))


def load_data_manifest(path: str | Path) -> DataManifest:
    with open(path, encoding="utf-8") as f:
        return DataManifest.model_validate(yaml.safe_load(f))
