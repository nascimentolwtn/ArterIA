"""C:S 1 heightmap fetch (roadmap L21, ADR 0011): since terrain.party is
reported down/unreliable (see ADR 0011's 2026-11-03 revision) and this
session cannot drive a browser-based tool (Heightmapper) or spoof a browser
identity to probe a bot-gated site, this builds the heightmap PNG directly
from a public, scripted-access-friendly elevation API (Open Topo Data,
`api.opentopodata.org`, SRTM GL1 ~30 m dataset) instead.

The one real network seam (ADR 0009 style) is `query_fn`: a callable from a
batch of (lat, lon) pairs to a list of elevations, in the same order. The
real default (`_query_opentopodata`) batches at <=100 points/request (the
service's documented limit) and sleeps between requests to stay polite;
tests inject a fake `query_fn` instead.

Cities: Skylines' heightmap convention (per the game's own Map Editor import
docs; not independently re-verified by this session): a 1081x1081 16-bit
greyscale PNG, pixel value 0-65535 linearly mapped to 0-1024 m. Elevation
below 0 m is clamped to 0; this is an approximation to sanity-check in-game
with the terrain tools, not a survey-grade import.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from collections.abc import Callable, Sequence
from pathlib import Path

import numpy as np
from PIL import Image

OPENTOPODATA_URL = "https://api.opentopodata.org/v1/srtm30m"
OPENTOPODATA_BATCH_LIMIT = 100
OPENTOPODATA_MIN_INTERVAL_S = 1.1  # polite throttle; the service's own limit is undocumented here
CS1_HEIGHTMAP_PX = 1081  # C:S 1 Map Editor's expected heightmap resolution
CS1_MAX_HEIGHT_M = 1024.0  # C:S 1's full 16-bit heightmap range

QueryFn = Callable[[Sequence[tuple[float, float]]], list[float]]


class HeightmapError(RuntimeError):
    pass


def _query_opentopodata(points: Sequence[tuple[float, float]], *, user_agent: str) -> list[float]:
    """The one real network call: POSTs <=100 (lat, lon) points per request
    to the public Open Topo Data API and returns their elevations in order.

    Splits `points` into batches of `OPENTOPODATA_BATCH_LIMIT`, sleeping
    `OPENTOPODATA_MIN_INTERVAL_S` between requests. Raises `HeightmapError`
    on an API-reported failure or a null elevation (outside dataset coverage).
    """
    elevations: list[float] = []
    for start in range(0, len(points), OPENTOPODATA_BATCH_LIMIT):
        batch = points[start : start + OPENTOPODATA_BATCH_LIMIT]
        locations = "|".join(f"{lat:.6f},{lon:.6f}" for lat, lon in batch)
        url = f"{OPENTOPODATA_URL}?{urllib.parse.urlencode({'locations': locations})}"
        request = urllib.request.Request(url, headers={"User-Agent": user_agent})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:  # noqa: S310
                payload = json.loads(response.read().decode("utf-8"))
        except OSError as exc:
            raise HeightmapError(f"Open Topo Data request failed: {exc}") from exc

        if payload.get("status") != "OK":
            raise HeightmapError(f"Open Topo Data error: {payload.get('error', payload)}")

        for result in payload["results"]:
            elevation = result.get("elevation")
            if elevation is None:
                raise HeightmapError(
                    f"no SRTM coverage at {result['location']} (outside dataset extent)"
                )
            elevations.append(float(elevation))

        if start + OPENTOPODATA_BATCH_LIMIT < len(points):
            time.sleep(OPENTOPODATA_MIN_INTERVAL_S)

    return elevations


def fetch_elevation_grid(
    *,
    west: float,
    south: float,
    east: float,
    north: float,
    grid_size: int,
    query_fn: QueryFn,
) -> np.ndarray:
    """A `grid_size` x `grid_size` elevation array (metres), row 0 = north
    edge, column 0 = west edge — the same orientation as an image, so no
    flip is needed before converting to one. `query_fn` is called once with
    every point flattened row-major (north-to-south, west-to-east).
    """
    lats = np.linspace(north, south, grid_size)
    lons = np.linspace(west, east, grid_size)
    points = [(float(lat), float(lon)) for lat in lats for lon in lons]
    elevations = query_fn(points)
    if len(elevations) != len(points):
        raise HeightmapError(
            f"query_fn returned {len(elevations)} elevations for {len(points)} points"
        )
    return np.array(elevations, dtype=np.float64).reshape(grid_size, grid_size)


def heightmap_image_from_grid(
    grid: np.ndarray,
    *,
    size_px: int = CS1_HEIGHTMAP_PX,
    max_height_m: float = CS1_MAX_HEIGHT_M,
    rotate_180: bool = True,
) -> Image.Image:
    """Upsamples `grid` (bicubic) to `size_px` x `size_px` and scales it to
    a 16-bit greyscale image (0 m -> 0, `max_height_m` -> 65535, clamped).

    `rotate_180` pre-applies the fix the Map Editor otherwise needs by hand
    (it defaults to sun-north-at-noon, per ADR 0011) so the exported file
    can be dropped straight into the game without an extra manual step.
    """
    clamped = np.clip(grid, 0.0, max_height_m)
    scaled = (clamped / max_height_m * 65535.0).round().astype(np.uint16)
    low_res = Image.fromarray(scaled)  # uint16 2D array -> mode "I;16" automatically
    image = low_res.resize((size_px, size_px), resample=Image.Resampling.BICUBIC)
    if rotate_180:
        image = image.transpose(Image.Transpose.ROTATE_180)
    return image


def write_heightmap(image: Image.Image, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return path


def build_heightmap(
    *,
    west: float,
    south: float,
    east: float,
    north: float,
    user_agent: str,
    grid_size: int = 60,
    size_px: int = CS1_HEIGHTMAP_PX,
    query_fn: QueryFn | None = None,
) -> Image.Image:
    """Fetches a `grid_size` x `grid_size` elevation grid over the bbox and
    returns the finished C:S 1 heightmap image (see `heightmap_image_from_grid`).

    `query_fn` defaults to the real Open Topo Data call; pass a fake for tests.
    """
    real_query_fn = query_fn or (lambda points: _query_opentopodata(points, user_agent=user_agent))
    grid = fetch_elevation_grid(
        west=west, south=south, east=east, north=north, grid_size=grid_size, query_fn=real_query_fn
    )
    return heightmap_image_from_grid(grid, size_px=size_px)
