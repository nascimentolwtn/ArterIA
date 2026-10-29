"""Route/trip generation (roadmap P3.3): wraps `od2trips` (OD matrix ->
trips), `duarouter` (trips -> routes) and `routeSampler.py` (routes +
measured counts -> a counts-matched route selection) — the three SUMO
tools ADR 0013's pipeline needs between a gravity-model OD matrix and a
counts-calibrated baseline.

Real use against SJC needs two inputs this project does not have yet: a
real OD matrix (P3.2's gravity model is still blocked on the Geosanja
attraction-side proxy, ADR 0017) and real traffic counts
(`traffic-counts` in `cities/sjc/data-manifest.yaml` is still `deferred`).
This module only builds and tests the *mechanics* against toy/synthetic
fixtures; wiring it to real SJC data waits on both of those (see
`.claude/napkin.md`).

`od2trips` and `duarouter` are real SUMO binaries, called through an
injected `run` callable (ADR 0009 seam, same pattern as
`network/build.py`). `routeSampler.py` ships as a Python *tool* under
`$SUMO_HOME/tools`, not a package or a binary, so it is invoked the same
way as a subprocess (`<python> <script> ...`) through that same `run`
seam, rather than imported (importing it would add `$SUMO_HOME/tools` to
`sys.path` process-wide for an unrelated reason).
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from pydantic import BaseModel


class TripGenerationError(RuntimeError):
    pass


class TripGenerationResult(BaseModel):
    output_path: str
    log: str


def _require_files(paths: Sequence[Path], what: str) -> None:
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError(f"{what} not found: {', '.join(missing)}")


def run_od2trips(
    *,
    taz_file: Path,
    od_matrix_files: Sequence[Path],
    output_path: Path,
    extra_options: Sequence[str] = (),
    run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> TripGenerationResult:
    """Turn an O/D matrix (SUMO's `$O;D2` text format) plus a `.taz.xml`
    zone file (e.g. `arteria.demand.zoning.build_taz_file`'s output) into a
    `.trips.xml`, via the real `od2trips` binary.
    """
    _require_files([taz_file], "TAZ file")
    _require_files(od_matrix_files, "OD matrix file(s)")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "od2trips",
        "--taz-files",
        str(taz_file),
        "--od-matrix-files",
        ",".join(str(p) for p in od_matrix_files),
        "--output-file",
        str(output_path),
        *extra_options,
    ]
    result = run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise TripGenerationError(f"od2trips failed (exit {result.returncode}): {result.stderr}")
    return TripGenerationResult(output_path=str(output_path), log=result.stdout + result.stderr)


def run_duarouter(
    *,
    net_file: Path,
    trips_files: Sequence[Path],
    output_path: Path,
    additional_files: Sequence[Path] = (),
    extra_options: Sequence[str] = (),
    run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> TripGenerationResult:
    """Route trips over `net_file` with the real `duarouter` binary, writing
    a `.rou.xml`. `-r/--route-files` reads trips, flows, routes and route
    alternatives alike, so `trips_files` is whatever `run_od2trips` (or a
    hand-written/externally supplied file) produced.
    """
    _require_files([net_file], "Net file")
    _require_files(trips_files, "Trips/route file(s)")
    _require_files(additional_files, "Additional file(s)")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "duarouter",
        "--net-file",
        str(net_file),
        "--route-files",
        ",".join(str(p) for p in trips_files),
        "--output-file",
        str(output_path),
    ]
    if additional_files:
        cmd += ["--additional-files", ",".join(str(p) for p in additional_files)]
    cmd += list(extra_options)

    result = run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise TripGenerationError(f"duarouter failed (exit {result.returncode}): {result.stderr}")
    return TripGenerationResult(output_path=str(output_path), log=result.stdout + result.stderr)


def _route_sampler_script(sumo_home: str | None) -> Path:
    if not sumo_home:
        raise FileNotFoundError(
            "SUMO_HOME is not set; routeSampler.py lives under $SUMO_HOME/tools"
        )
    script = Path(sumo_home) / "tools" / "routeSampler.py"
    if not script.exists():
        raise FileNotFoundError(f"routeSampler.py not found at {script}")
    return script


def run_route_sampler(
    *,
    route_files: Sequence[Path],
    edgedata_files: Sequence[Path],
    output_path: Path,
    turn_files: Sequence[Path] = (),
    extra_options: Sequence[str] = (),
    sumo_home: str | None = None,
    run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> TripGenerationResult:
    """Resample `route_files` (e.g. `run_duarouter`'s output) so the result
    matches measured counts in `edgedata_files` (roadmap P3.3's
    counts-driven half, ADR 0013). `sumo_home` defaults to the `SUMO_HOME`
    environment variable; the script is run as `<python> <script> ...`
    rather than imported (see module docstring).
    """
    script = _route_sampler_script(
        sumo_home if sumo_home is not None else os.environ.get("SUMO_HOME")
    )
    _require_files(route_files, "Route file(s)")
    _require_files(edgedata_files, "EdgeData file(s)")
    _require_files(turn_files, "Turn file(s)")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(script),
        "--route-files",
        ",".join(str(p) for p in route_files),
        "--edgedata-files",
        ",".join(str(p) for p in edgedata_files),
        "--output-file",
        str(output_path),
    ]
    if turn_files:
        cmd += ["--turn-files", ",".join(str(p) for p in turn_files)]
    cmd += list(extra_options)

    result = run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise TripGenerationError(
            f"routeSampler.py failed (exit {result.returncode}): {result.stderr}"
        )
    return TripGenerationResult(output_path=str(output_path), log=result.stdout + result.stderr)
