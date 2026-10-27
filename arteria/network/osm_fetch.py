"""OSM source download and candidate-corridor extraction (roadmap P2.1,
remote task R4, desk task L8).

Both external calls this module makes — fetching the regional PBF and
running `osmium extract` — sit behind injectable callables, per ADR 0009:
this remote session has no network access and no `osmium` binary, so every
test here uses a fake `download`/`run`. `download_source_pbf` does ship a
real default (`_urlretrieve`, stdlib `urllib.request`) that is usable at the
desk; `extract_osm` has no real default for `run` because `osmium` isn't a
Python API — the desk run passes nothing and gets `subprocess.run`.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel

from arteria.data_safety import sha256_of
from arteria.network.snapshot import (
    SNAPSHOT_FILENAME,
    ExtractSnapshot,
    OsmSnapshot,
    SourceSnapshot,
    fingerprint,
    load_snapshot,
    pbf_data_timestamp,
    save_snapshot,
    verify_extract,
    verify_source,
)


class OsmFetchError(RuntimeError):
    pass


class OsmExtractError(RuntimeError):
    pass


def _urlretrieve(url: str, dest: Path) -> None:
    """Real default for `download_source_pbf`'s `download` parameter. Not
    exercised remotely (ADR 0009: no network access) — tests always inject
    a fake `download` instead.
    """
    import urllib.request

    urllib.request.urlretrieve(url, dest)  # noqa: S310 - desk-only, real fetch


def download_source_pbf(
    url: str,
    dest: Path,
    *,
    download: Callable[[str, Path], None] = _urlretrieve,
) -> Path:
    """Download the regional OSM extract at `url` to `dest`, creating
    `dest`'s parent directory if needed. `download` is injected so this is
    testable without a real network call (ADR 0009); the real desk run can
    omit it and get `_urlretrieve`.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    download(url, dest)
    return dest


def default_geofabrik_url(region: str = "south-america/brazil") -> str:
    """The Geofabrik regional-extract URL used when the caller doesn't pass
    `--source-url`.

    São José dos Campos (SJC), the first pilot city, is in São Paulo state,
    which Geofabrik's "south-america/brazil" sub-region page files under the
    "sudeste" (southeast Brazil) extract alongside Rio de Janeiro, Minas
    Gerais, and Espírito Santo. This is a reasonable default, not a fixed
    fact about every future city `arteria` supports — override `region` (or
    pass a full `--source-url`) for a city outside southeast Brazil.
    """
    return f"https://download.geofabrik.de/{region}/sudeste-latest.osm.pbf"


ALL_CANDIDATES_ID = "all"


def _envelope_of(features: list[dict], source: Path) -> dict:
    """One rectangular polygon enclosing every candidate polygon (ADR 0016:
    the unified city network is clipped to this envelope, so the gaps between
    corridors are included and the corridors stay connected through them).
    """

    def points(geometry: dict):
        if geometry.get("type") == "Polygon":
            polygons = [geometry["coordinates"]]
        else:  # MultiPolygon
            polygons = geometry["coordinates"]
        for polygon in polygons:
            yield from polygon[0]

    coords = [pt for f in features for pt in points(f.get("geometry", {}))]
    if not coords:
        raise OsmFetchError(f"no candidate polygons in {source}")
    xs = [pt[0] for pt in coords]
    ys = [pt[1] for pt in coords]
    west, south, east, north = min(xs), min(ys), max(xs), max(ys)
    ring = [[west, south], [east, south], [east, north], [west, north], [west, south]]
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"id": ALL_CANDIDATES_ID},
                "geometry": {"type": "Polygon", "coordinates": [ring]},
            }
        ],
    }


def extract_candidate_polygon(study_areas_geojson_path: Path, candidate_id: str) -> dict:
    """Read the `study-areas.geojson` FeatureCollection written by
    `arteria studyarea build` (see `arteria.network.study_area.build_study_areas`)
    and return a single-feature FeatureCollection for the feature whose
    `properties.id` matches `candidate_id` (case-insensitive). The special id
    `all` returns the bounding rectangle of every candidate polygon.

    Raises `OsmFetchError`, listing the available candidate ids, if no
    feature matches.
    """
    data = json.loads(Path(study_areas_geojson_path).read_text(encoding="utf-8"))
    features = data.get("features", [])

    if candidate_id.lower() == ALL_CANDIDATES_ID:
        return _envelope_of(features, study_areas_geojson_path)

    for feature in features:
        feature_id = feature.get("properties", {}).get("id", "")
        if feature_id.lower() == candidate_id.lower():
            return {"type": "FeatureCollection", "features": [feature]}

    available = sorted(feature.get("properties", {}).get("id", "") for feature in features)
    available_str = ", ".join(repr(a) for a in available) if available else "(none)"
    raise OsmFetchError(
        f"no candidate with id {candidate_id!r} in {study_areas_geojson_path}; "
        f"available candidate ids: {available_str}"
    )


class OsmExtractResult(BaseModel):
    output_path: str
    sha256: str


def extract_osm(
    *,
    pbf_path: Path,
    polygon_geojson: dict,
    output_path: Path,
    run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> OsmExtractResult:
    """Clip `pbf_path` to `polygon_geojson` with `osmium extract`, writing
    `output_path`. `run` is injected (ADR 0009: no `osmium` binary here);
    tests use a fake that writes bytes to `output_path` itself, since the
    real binary's job (producing that file) can't be mocked away and still
    exercise the sha256 step below.
    """
    if not pbf_path.exists():
        raise FileNotFoundError(f"OSM source PBF not found: {pbf_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".geojson", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(polygon_geojson, tmp)
        tmp_polygon_path = Path(tmp.name)

    try:
        cmd = [
            "osmium",
            "extract",
            "--polygon",
            str(tmp_polygon_path),
            str(pbf_path),
            "--output",
            str(output_path),
            "--overwrite",
        ]
        result = run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise OsmExtractError(
                f"osmium extract failed (exit {result.returncode}): {result.stderr}"
            )
        return OsmExtractResult(output_path=str(output_path), sha256=sha256_of(output_path))
    finally:
        tmp_polygon_path.unlink(missing_ok=True)


def fetch_candidate(
    *,
    city: str,
    city_dir: Path,
    candidate: str,
    pbf_path: Path | None = None,
    source_url: str | None = None,
    update_snapshot: bool = False,
    run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    download: Callable[[str, Path], None] = _urlretrieve,
    log: Callable[[str], None] = lambda message: None,
) -> OsmExtractResult:
    """Get (or reuse) the regional PBF, check it against the pinned snapshot
    `cities/<city>/network/osm-snapshot.yaml`, clip it to `candidate`, and check
    the clip too (roadmap P2.1).

    With a snapshot present, a source or extract whose sha256 differs raises
    `SnapshotMismatchError` and nothing is overwritten. `update_snapshot=True`
    skips the checks and re-pins the snapshot to what was just produced; with
    no snapshot yet, one is created.
    """
    raw_dir = city_dir / "network" / "raw"
    snapshot_path = city_dir / "network" / SNAPSHOT_FILENAME
    snapshot = load_snapshot(snapshot_path)
    checking = snapshot is not None and not update_snapshot

    url = source_url or (snapshot.source.url if snapshot else default_geofabrik_url())
    if pbf_path is not None:
        source_pbf = pbf_path
    else:
        source_pbf = raw_dir / url.rsplit("/", 1)[-1]
        if source_pbf.exists():
            log(f"Reusing cached {source_pbf}")
        else:
            download_source_pbf(url, source_pbf, download=download)
            log(f"Downloaded {url} -> {source_pbf}")
    if checking:
        assert snapshot is not None
        verify_source(snapshot, source_pbf)
        log("Source PBF matches the pinned snapshot.")

    polygon = extract_candidate_polygon(city_dir / "study-areas.geojson", candidate)
    output_path = raw_dir / f"{city}-{candidate}.osm.pbf"
    result = extract_osm(
        pbf_path=source_pbf, polygon_geojson=polygon, output_path=output_path, run=run
    )

    if checking:
        assert snapshot is not None
        verify_extract(snapshot, candidate, output_path)
        log(f"Extract {candidate!r} matches the pinned snapshot.")
    else:
        source = SourceSnapshot(
            file=source_pbf.name,
            url=url,
            data_timestamp=pbf_data_timestamp(source_pbf, run=run),
            **fingerprint(source_pbf).model_dump(),
        )
        pinned = snapshot or OsmSnapshot(city=city, source=source)
        pinned.source = source
        pinned.extracts[candidate] = ExtractSnapshot(
            file=output_path.name, candidate=candidate, **fingerprint(output_path).model_dump()
        )
        save_snapshot(pinned, snapshot_path)
        log(f"Pinned snapshot written to {snapshot_path}")
    return result
