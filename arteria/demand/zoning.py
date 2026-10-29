"""Traffic analysis zones (roadmap P3.1): assign every network edge to one of
the four aerial-verified study-area polygons (`cities/sjc/study-areas.geojson`,
candidates a/b/c/d) or to a catch-all `external` zone, and write the result as
a SUMO `.taz.xml`. Per ADR 0017, the TAZ layer reuses this existing, already
-verified geometry rather than drawing a new zone layer.

Needs the `geo` extra (shapely, pyproj), same as `study_area.py` — this module
is pure geometry with no real-binary call, so it carries no ADR 0009 seam: it
is fully exercised here against toy fixtures, and the one real run (against
the real `sjc.net.xml`) is just this same code pointed at real files.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import shapely
from pydantic import BaseModel
from pyproj import Transformer
from shapely.affinity import translate
from shapely.geometry import Point, shape

EXTERNAL_ZONE_ID = "external"
# Net (x, y) + offset = EPSG:31983 (SIRGAS 2000 / UTM 23S); see crosscheck.py/render.py,
# which derived this from netconvert's <location netOffset>, negated, for SJC.
NET_OFFSET = (384192.69, 7414390.50)


class ZonePolygon(BaseModel):
    id: str
    name: str
    geometry: dict  # GeoJSON geometry, WGS84 (lon, lat)


class TazBuildResult(BaseModel):
    output_path: str
    zone_edge_counts: dict[str, int]
    total_edges: int
    empty_zones: list[str]


def load_zones_from_study_areas(path: str | Path) -> list[ZonePolygon]:
    """Reads `study-areas.geojson`, keeping only `enabled: true` features."""
    features = json.loads(Path(path).read_text(encoding="utf-8"))["features"]
    return [
        ZonePolygon(
            id=f["properties"]["id"],
            name=f["properties"]["name"],
            geometry=f["geometry"],
        )
        for f in features
        if f["properties"].get("enabled")
    ]


def _is_internal(edge: ET.Element) -> bool:
    return edge.get("id", "").startswith(":") or edge.get("function") in {
        "internal",
        "crossing",
        "walkingarea",
    }


def _edge_midpoints(net_path: str | Path) -> dict[str, tuple[float, float]]:
    """Net-local (x, y) midpoint of each non-internal edge, from the mean of
    its `from`/`to` junction coordinates (TAZ granularity doesn't need the
    full lane shape)."""
    root = ET.parse(net_path).getroot()
    junction_xy = {
        j.get("id", ""): (float(j.get("x", "0")), float(j.get("y", "0")))
        for j in root.findall("junction")
        if j.get("x") is not None and j.get("y") is not None
    }
    midpoints: dict[str, tuple[float, float]] = {}
    for edge in root.findall("edge"):
        if _is_internal(edge):
            continue
        edge_id = edge.get("id", "")
        from_xy = junction_xy.get(edge.get("from", ""))
        to_xy = junction_xy.get(edge.get("to", ""))
        if from_xy is None or to_xy is None:
            continue
        midpoints[edge_id] = ((from_xy[0] + to_xy[0]) / 2, (from_xy[1] + to_xy[1]) / 2)
    return midpoints


def _apply_xy(transform_func, coords: np.ndarray) -> np.ndarray:
    """Adapts a pyproj Transformer.transform call to shapely.transform's
    per-geometry (N, 2) coordinate-array interface (see study_area.py)."""
    xs, ys = transform_func(coords[:, 0], coords[:, 1])
    return np.column_stack([xs, ys])


def assign_edges_to_zones(net_path: str | Path, zones: list[ZonePolygon]) -> dict[str, str]:
    """Edge id -> zone id, by point-in-polygon test of each edge's midpoint
    (projected from net-local coordinates into the zones' WGS84 polygons).
    Falls back to `EXTERNAL_ZONE_ID` when no zone polygon contains it.
    """
    dx, dy = NET_OFFSET
    to_utm = Transformer.from_crs(4326, 31983, always_xy=True).transform
    zone_polygons = [
        (
            zone.id,
            translate(
                shapely.transform(shape(zone.geometry), lambda c: _apply_xy(to_utm, c)), -dx, -dy
            ),
        )
        for zone in zones
    ]

    assignment: dict[str, str] = {}
    for edge_id, (x, y) in _edge_midpoints(net_path).items():
        point = Point(x, y)
        zone_id = next((zid for zid, poly in zone_polygons if poly.contains(point)), None)
        assignment[edge_id] = zone_id if zone_id is not None else EXTERNAL_ZONE_ID
    return assignment


def build_taz_file(
    net_path: str | Path, study_areas_path: str | Path, output_path: str | Path
) -> TazBuildResult:
    """Writes the SUMO `.taz.xml` (one `<taz>` per enabled study area plus
    `external`) to `output_path`."""
    zones = load_zones_from_study_areas(study_areas_path)
    assignment = assign_edges_to_zones(net_path, zones)

    edges_by_zone: dict[str, list[str]] = {zone.id: [] for zone in zones}
    edges_by_zone[EXTERNAL_ZONE_ID] = []
    for edge_id, zone_id in assignment.items():
        edges_by_zone[zone_id].append(edge_id)

    root = ET.Element("tazs")
    for zone_id in [*[zone.id for zone in zones], EXTERNAL_ZONE_ID]:
        ET.SubElement(
            root, "taz", {"id": zone_id, "edges": " ".join(sorted(edges_by_zone[zone_id]))}
        )
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space="    ")
    ET.ElementTree(root).write(output_path, encoding="UTF-8", xml_declaration=True)

    zone_edge_counts = {zone_id: len(edges) for zone_id, edges in edges_by_zone.items()}
    return TazBuildResult(
        output_path=str(output_path),
        zone_edge_counts=zone_edge_counts,
        total_edges=len(assignment),
        empty_zones=[zone_id for zone_id, count in zone_edge_counts.items() if count == 0],
    )
