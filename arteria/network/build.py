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

from arteria.network.patches import patch_options
from arteria.network.validate import validate_network


class NetconvertError(RuntimeError):
    pass


# netconvert 1.28.0 double-escapes a handful of XML special characters that
# were present literally in an OSM tag value: it first replaces the literal
# character with its named entity (e.g. "'" -> "&apos;"), then its own XML
# writer escapes the "&" in that entity again when serialising the attribute,
# so the net.xml ends up with "&amp;apos;" where the OSM source had a plain
# apostrophe. Reproduced with a two-way fixture against the real binary:
# literal ' & " < > in an OSM `name` tag all come out the same way. The right
# fix lives upstream in netconvert; until a fixed release is in use, undo the
# extra escaping here so `name`/`origId` attributes hold the correct text.
_DOUBLE_ESCAPED_ENTITIES = {
    "&amp;apos;": "'",  # apostrophe needs no escaping inside a double-quoted attribute
    "&amp;quot;": "&quot;",
    "&amp;lt;": "&lt;",
    "&amp;gt;": "&gt;",
    "&amp;amp;": "&amp;",
}


def fix_double_escaped_names(path: Path) -> int:
    """Undo netconvert's double-escaping (see `_DOUBLE_ESCAPED_ENTITIES`) in
    a written `.net.xml`. Returns the number of characters fixed (0 if none
    were found, which is the common case).
    """
    text = path.read_text(encoding="utf-8")
    fixed = text
    count = 0
    for broken, correct in _DOUBLE_ESCAPED_ENTITIES.items():
        n = fixed.count(broken)
        if n:
            count += n
            fixed = fixed.replace(broken, correct)
    if count:
        path.write_text(fixed, encoding="utf-8")
    return count


class NetworkBuildResult(BaseModel):
    net_xml_path: str
    log: str
    validation_errors: int
    validation_warnings: int
    patch_files: list[str] = []


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
    patch_files: Sequence[Path] = (),
    run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> NetworkBuildResult:
    """Run `netconvert` against `osm_pbf_path` (PBF is first converted to OSM XML
    with `osmium cat`; `.osm.xml` input is passed through), writing `output_path`, then
    validate the result with `validate_network`. `run` is injected (ADR
    0009: no `netconvert` binary here); tests use a fake that writes a toy
    `.net.xml` to `output_path`, since the real binary's job can't be
    mocked away and still exercise the validation step below.

    `extra_options` is appended last, after `default_netconvert_options()`
    and any `--type-files`, so a caller can override or add flags.

    `patch_files` (roadmap P2.3, `arteria.network.patches`) are plain-XML
    corrections applied in a second `netconvert` pass over the first pass's
    output (`<stem>.base.net.xml`), because SUMO only patches an existing
    `.net.xml`, not an OSM import. No patches means no second pass.
    """
    if not osm_pbf_path.exists():
        raise FileNotFoundError(f"OSM PBF not found: {osm_pbf_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # netconvert reads OSM XML only (first real run: "invalid multi-byte
    # sequence" on a .pbf), so convert PBF input with `osmium cat` first.
    osm_input = osm_pbf_path
    if osm_pbf_path.suffix == ".pbf":
        osm_input = osm_pbf_path.with_suffix("").with_suffix(".osm.xml")
        convert = run(
            ["osmium", "cat", str(osm_pbf_path), "-o", str(osm_input), "--overwrite"],
            capture_output=True,
            text=True,
        )
        if convert.returncode != 0:
            raise NetconvertError(
                f"osmium cat failed (exit {convert.returncode}): {convert.stderr}"
            )

    base_path = output_path.with_name(output_path.name.removesuffix(".net.xml") + ".base.net.xml")
    cmd = [
        "netconvert",
        "--osm-files",
        str(osm_input),
        "--output-file",
        str(base_path if patch_files else output_path),
        *default_netconvert_options(),
    ]
    if type_files:
        cmd += ["--type-files", ",".join(str(p) for p in type_files)]
    cmd += list(extra_options)

    result = run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise NetconvertError(f"netconvert failed (exit {result.returncode}): {result.stderr}")
    log = result.stdout + result.stderr

    if patch_files:
        patch_cmd = [
            "netconvert",
            "--sumo-net-file",
            str(base_path),
            "--output-file",
            str(output_path),
            *patch_options(patch_files),
        ]
        patched = run(patch_cmd, capture_output=True, text=True)
        if patched.returncode != 0:
            raise NetconvertError(
                f"netconvert patch pass failed (exit {patched.returncode}): {patched.stderr}"
            )
        log += patched.stdout + patched.stderr

    fixed_chars = fix_double_escaped_names(output_path)
    if fixed_chars:
        log += (
            f"\n[arteria] fixed {fixed_chars} double-escaped character(s) in names "
            "(netconvert bug, see build.py)\n"
        )

    report = validate_network(output_path)
    return NetworkBuildResult(
        net_xml_path=str(output_path),
        log=log,
        validation_errors=len(report.by_severity("error")),
        validation_warnings=len(report.by_severity("warning")),
        patch_files=[str(p) for p in patch_files],
    )
