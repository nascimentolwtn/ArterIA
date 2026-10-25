"""`netconvert` OSM-import pipeline (roadmap P2.2/P2.3/P2.5, remote task R4,
desk tasks L9/L11).

The real `netconvert` call sits behind an injected `run` callable (ADR
0009: no `netconvert` binary in this remote session). Validation reuses
`arteria.network.validate.validate_network` rather than reimplementing any
checks.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path

from pydantic import BaseModel

from arteria.network.validate import validate_network


class NetconvertError(RuntimeError):
    pass


class NetworkBuildResult(BaseModel):
    net_xml_path: str
    log: str
    validation_errors: int
    validation_warnings: int


def default_netconvert_options() -> list[str]:
    """The standard OSM-import flag set recommended by SUMO's own
    "Networks/Import/OpenStreetMap" documentation: remove interior
    geometry points, guess roundabouts/ramps, join nearby junctions, guess
    and clean up traffic-light groups, and keep the original OSM street
    names alongside SUMO's output names.

    Not run against a real `netconvert` binary in this remote session
    (ADR 0009) — confirm this list still matches `netconvert --help` at
    the desk before relying on it for the real SJC build.
    """
    return [
        "--geometry.remove",
        "--roundabouts.guess",
        "--ramps.guess",
        "--junctions.join",
        "--tls.guess-signals",
        "--tls.discard-simple",
        "--tls.join",
        "--output.street-names",
        "--output.original-names",
    ]


def build_network(
    *,
    osm_pbf_path: Path,
    output_path: Path,
    type_files: Sequence[Path] = (),
    extra_options: Sequence[str] = (),
    run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> NetworkBuildResult:
    """Run `netconvert` against `osm_pbf_path`, writing `output_path`, then
    validate the result with `validate_network`. `run` is injected (ADR
    0009: no `netconvert` binary here); tests use a fake that writes a toy
    `.net.xml` to `output_path`, since the real binary's job can't be
    mocked away and still exercise the validation step below.

    `extra_options` is appended last, after `default_netconvert_options()`
    and any `--type-files`, so a caller can override or add flags.
    """
    if not osm_pbf_path.exists():
        raise FileNotFoundError(f"OSM PBF not found: {osm_pbf_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "netconvert",
        "--osm-files",
        str(osm_pbf_path),
        "--output-file",
        str(output_path),
        *default_netconvert_options(),
    ]
    if type_files:
        cmd += ["--type-files", ",".join(str(p) for p in type_files)]
    cmd += list(extra_options)

    result = run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise NetconvertError(f"netconvert failed (exit {result.returncode}): {result.stderr}")

    report = validate_network(output_path)
    return NetworkBuildResult(
        net_xml_path=str(output_path),
        log=result.stdout + result.stderr,
        validation_errors=len(report.by_severity("error")),
        validation_warnings=len(report.by_severity("warning")),
    )
