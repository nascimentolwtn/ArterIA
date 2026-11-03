"""Cities: Skylines map-prep note (roadmap L21, ADR 0011): the one piece of
the C:S hobby track that is actually scriptable without the game itself.

C:S 1's importable terrain tile tops out at about 18 km square (a terrain.party
tile is "roughly 1:1 scale with the game" at that size, per the research this
was written from); the whole SJC net is about 38 x 28 km (`origBoundary` in
`cities/sjc/network/sjc.net.xml`), so only one corridor-sized crop fits per
map, not the whole city. This module computes that crop's centre and bbox
from `cities/<city>/corridors/corridors.geojson` and writes a note with the
coordinates to paste into terrain.party (heightmap) and Cimtographer/the OSM
Import mod (roads) — everything past that is a manual GUI procedure, see
`docs/local/cities-skylines.md`.

No network/file access beyond the one `corridors.geojson` read: this module
has no ADR-0009 seam to begin with.
"""

from __future__ import annotations

import math
from pathlib import Path

from pydantic import BaseModel

CS1_MAX_TILE_KM = 18.0  # commonly-cited C:S 1 terrain-tile size at ~1:1 scale
_KM_PER_DEG_LAT = 110.574
_KM_PER_DEG_LON_AT_EQUATOR = 111.320


class PrepareMapError(RuntimeError):
    pass


class MapPrepResult(BaseModel):
    city: str
    corridor_id: str  # the requested id, or "all" for the whole net
    center_lon: float
    center_lat: float
    size_km: float
    west: float
    south: float
    east: float
    north: float
    warning: str | None = None


def _feature_points(features: list[dict]) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for feature in features:
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates") or []
        if geometry.get("type") == "LineString":
            points.extend((lon, lat) for lon, lat in coords)
    return points


def compute_map_prep(
    corridors_geojson: dict,
    *,
    city: str,
    corridor_id: str = "all",
    size_km: float = CS1_MAX_TILE_KM,
) -> MapPrepResult:
    """Pick a `size_km` square centred on `corridor_id`'s centroid (or, for
    `corridor_id="all"`, the whole collection's), from the corridor
    LineStrings in `corridors_geojson` (`cities/<city>/corridors/corridors.geojson`,
    WGS84 lon/lat already).

    Raises `PrepareMapError` if `corridor_id` matches no feature's
    `properties.corridor` (case-insensitive). Sets `warning` on the result,
    rather than raising, when `size_km` exceeds `CS1_MAX_TILE_KM` or when the
    square doesn't fully cover the selected corridor's own bounding box —
    both are real constraints the caller should see, not failures, since a
    deliberately cropped or oversized tile can still be a valid choice.
    """
    features = corridors_geojson.get("features", [])
    if corridor_id.lower() != "all":
        features = [
            f
            for f in features
            if str(f.get("properties", {}).get("corridor", "")).lower() == corridor_id.lower()
        ]
        if not features:
            all_features = corridors_geojson.get("features", [])
            available = sorted(
                {str(f.get("properties", {}).get("corridor", "")) for f in all_features}
            )
            raise PrepareMapError(
                f"no corridor {corridor_id!r} in corridors.geojson; available: "
                f"{', '.join(available) or '(none)'}"
            )

    points = _feature_points(features)
    if not points:
        raise PrepareMapError(f"no LineString geometry found for corridor {corridor_id!r}")

    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    west, east = min(lons), max(lons)
    south, north = min(lats), max(lats)
    center_lon = (west + east) / 2
    center_lat = (south + north) / 2

    lat_half_deg = (size_km / 2) / _KM_PER_DEG_LAT
    lon_half_deg = (size_km / 2) / (_KM_PER_DEG_LON_AT_EQUATOR * math.cos(math.radians(center_lat)))
    tile_west = center_lon - lon_half_deg
    tile_east = center_lon + lon_half_deg
    tile_south = center_lat - lat_half_deg
    tile_north = center_lat + lat_half_deg

    warnings: list[str] = []
    if size_km > CS1_MAX_TILE_KM:
        warnings.append(
            f"{size_km:g} km exceeds C:S 1's ~{CS1_MAX_TILE_KM:g} km terrain tile; "
            "the imported map will be cropped or distorted by the game/importer, not by this tool."
        )
    if west < tile_west or east > tile_east or south < tile_south or north > tile_north:
        warnings.append(
            f"corridor {corridor_id!r}'s own bounding box does not fully fit in a "
            f"{size_km:g} km tile centred on its centroid; increase --size-km or accept the crop."
        )

    return MapPrepResult(
        city=city,
        corridor_id=corridor_id,
        center_lon=round(center_lon, 6),
        center_lat=round(center_lat, 6),
        size_km=size_km,
        west=round(tile_west, 6),
        south=round(tile_south, 6),
        east=round(tile_east, 6),
        north=round(tile_north, 6),
        warning="; ".join(warnings) or None,
    )


def render_map_prep_note(result: MapPrepResult) -> str:
    """Markdown note with the coordinates for the manual steps in
    `docs/local/cities-skylines.md` (roadmap L21/L22)."""
    overpass_bbox = f"{result.south},{result.west},{result.north},{result.east}"
    lines = [
        f"# C:S 1 map prep — {result.city} / {result.corridor_id}",
        "",
        "Illustrative hobby track (ADR 0011, ADR 0015) — not SUMO evidence.",
        "",
        f"- Center (lon, lat): `{result.center_lon}, {result.center_lat}`",
        f"- Tile size: {result.size_km:g} km square",
        f"- Bbox (WGS84, west/south/east/north): "
        f"`{result.west}, {result.south}, {result.east}, {result.north}`",
        f"- Overpass/Cimtographer bbox paste (south,west,north,east): `{overpass_bbox}`",
    ]
    if result.warning:
        lines += ["", f"**Warning:** {result.warning}"]
    lines += [
        "",
        "## Manual next steps",
        "",
        "See `docs/local/cities-skylines.md` for the full procedure "
        "(terrain.party heightmap import, Cimtographer road import, "
        "Overlay satellite reference, TM:PE/Move It package edits, "
        "'illustrative, uncalibrated' labelling on every screenshot/video).",
        "",
    ]
    return "\n".join(lines)


def write_map_prep(result: MapPrepResult, cs_root: Path) -> Path:
    """Writes the note to `cs_root/<city>/<corridor_id>/map-prep.md`.

    `cs_root` is the `ARTERIA_DATA` layout's `cs/` root (roadmap `docs/roadmap.md`
    local directory layout), not necessarily inside this repo.
    """
    out_dir = cs_root / result.city / result.corridor_id.lower()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "map-prep.md"
    out_path.write_text(render_map_prep_note(result), encoding="utf-8")
    return out_path
