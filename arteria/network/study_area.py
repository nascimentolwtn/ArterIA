"""Study-area polygon drafting (roadmap P1.4): geocode a candidate's
landmark queries and build a buffered convex-hull polygon around them.

Geocoding needs real network access to Nominatim, which this remote
session's network policy blocks (see `cities/sjc/data-manifest.yaml`'s
`osm-network-extract` notes, and ADR 0009's remote/desktop boundary) — this
module was written and tested here, but its one real `geocode_nominatim`
run happens at the desk. The seam is deliberate: `geocode_nominatim` is the
only function that touches the network; `hull_buffer_polygon` and
`build_study_areas` are pure and exercised below against fixture points.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import numpy as np
import shapely
import yaml
from pydantic import BaseModel, Field
from pyproj import Transformer
from shapely.geometry import MultiPoint, mapping


def _apply_xy(transform_func, coords: np.ndarray) -> np.ndarray:
    """Adapts a pyproj Transformer.transform call to shapely.transform's
    per-geometry (N, 2) coordinate-array interface."""
    xs, ys = transform_func(coords[:, 0], coords[:, 1])
    return np.column_stack([xs, ys])


class CandidateQuery(BaseModel):
    id: str
    name: str
    queries: list[str]
    buffer_m: float
    priority: int | None = None
    enabled: bool = True
    note: str | None = None


class StudyAreaConfig(BaseModel):
    candidates: list[CandidateQuery] = Field(default_factory=list)


def load_study_area_config(path: str | Path) -> StudyAreaConfig:
    with open(path, encoding="utf-8") as f:
        return StudyAreaConfig.model_validate(yaml.safe_load(f))


GeocodeFn = Callable[[str], tuple[float, float]]  # query -> (lon, lat), WGS84


def geocode_nominatim(query: str, user_agent: str) -> tuple[float, float]:
    """The one network seam in this module (ADR 0009). Not unit-tested
    remotely: it needs a live request to nominatim.openstreetmap.org,
    which this session's network policy blocks. `user_agent` must
    identify the tool and a way to reach its operator, per Nominatim's
    usage policy — pass a real one at the desk, don't reuse a placeholder.
    """
    from geopy.geocoders import Nominatim  # lazy: only needed for the real run

    geolocator = Nominatim(user_agent=user_agent)
    location = geolocator.geocode(query, country_codes="br", timeout=10)
    if location is None:
        raise ValueError(f"Nominatim found nothing for {query!r}")
    return (location.longitude, location.latitude)


def hull_buffer_polygon(
    points_lonlat: list[tuple[float, float]],
    buffer_m: float,
    projected_crs: str,
) -> dict:
    """Convex hull of `points_lonlat`, buffered by `buffer_m` metres in
    `projected_crs` (so the buffer is a real distance, not degrees), and
    returned as a GeoJSON Polygon geometry back in WGS84 (lon, lat).
    Degenerates gracefully for 1-2 points: the buffer still produces a
    polygon around the point or line.
    """
    if not points_lonlat:
        raise ValueError("need at least one point to build a study-area polygon")

    to_projected = Transformer.from_crs("EPSG:4326", projected_crs, always_xy=True).transform
    to_wgs84 = Transformer.from_crs(projected_crs, "EPSG:4326", always_xy=True).transform

    hull = MultiPoint(points_lonlat).convex_hull
    hull_projected = shapely.transform(hull, lambda coords: _apply_xy(to_projected, coords))
    buffered_projected = hull_projected.buffer(buffer_m)
    buffered_wgs84 = shapely.transform(
        buffered_projected, lambda coords: _apply_xy(to_wgs84, coords)
    )

    return mapping(buffered_wgs84)


def build_study_areas(
    config: StudyAreaConfig,
    geocode: GeocodeFn,
    projected_crs: str,
    include_disabled: bool = False,
) -> dict:
    """Geocode every candidate's queries and build its polygon. Returns a
    GeoJSON FeatureCollection. `geocode` is injected so this orchestration
    is testable with a fixture geocoder and no network call.
    """
    features = []
    for candidate in config.candidates:
        if not candidate.enabled and not include_disabled:
            continue
        points = [geocode(q) for q in candidate.queries]
        geometry = hull_buffer_polygon(points, candidate.buffer_m, projected_crs)
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": candidate.id,
                    "name": candidate.name,
                    "priority": candidate.priority,
                    "enabled": candidate.enabled,
                    "note": candidate.note,
                },
                "geometry": geometry,
            }
        )
    return {"type": "FeatureCollection", "features": features}
