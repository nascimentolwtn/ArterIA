"""One-command network rebuild (roadmap P2 exit criterion).

verify pinned OSM snapshot -> clip the whole-city envelope -> `netconvert`
(+ patches) -> validate -> compare with the pinned reference net -> write a
provenance manifest. Every external call goes through the injected `run`
(ADR 0009).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel

from arteria.data_safety import sha256_of
from arteria.network.build import build_network
from arteria.network.diff import diff_networks, net_content_sha256, render_markdown
from arteria.network.osm_fetch import ALL_CANDIDATES_ID, fetch_candidate
from arteria.network.patches import load_patch_files
from arteria.network.snapshot import (
    SNAPSHOT_FILENAME,
    NetReference,
    load_snapshot,
    save_snapshot,
)
from arteria.provenance import build_run_manifest, write_run_manifest


class RebuildError(RuntimeError):
    pass


class RebuildResult(BaseModel):
    net_path: str
    net_sha256: str
    content_sha256: str
    netconvert_version: str
    patch_files: list[str]
    validation_errors: int
    validation_warnings: int
    validation_blocking: bool
    reference_pinned: bool  # a reference net was in the snapshot
    reproduced: bool | None  # content hash equals the reference (None: no reference)
    diff_counts: dict[str, dict[str, int]] | None = None
    manifest_path: str


def netconvert_version(run: Callable[..., subprocess.CompletedProcess] = subprocess.run) -> str:
    result = run(["netconvert", "--version"], capture_output=True, text=True)
    match = re.search(r"netconvert\s+(\d+(?:\.\d+)+)", result.stdout or "")
    return match.group(1) if match else "unknown"


def rebuild_network(
    *,
    city: str,
    city_dir: Path,
    repo_root: Path,
    update_snapshot: bool = False,
    diff_previous: bool = True,
    run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    log: Callable[[str], None] = lambda message: None,
) -> RebuildResult:
    network_dir = city_dir / "network"
    snapshot_path = network_dir / SNAPSHOT_FILENAME
    if load_snapshot(snapshot_path) is None and not update_snapshot:
        raise RebuildError(
            f"no pinned OSM snapshot at {snapshot_path}; pin one first with "
            f"`arteria osm fetch --city {city} --candidate all --update-snapshot`"
        )

    log("1/5 verify snapshot and clip")
    extract = fetch_candidate(
        city=city,
        city_dir=city_dir,
        candidate=ALL_CANDIDATES_ID,
        update_snapshot=update_snapshot,
        run=run,
        log=log,
    )

    patch_files = load_patch_files(network_dir / "patches")
    net_path = network_dir / f"{city}.net.xml"
    previous = net_path.with_name(f"{city}.prev.net.xml")
    had_previous = net_path.exists()
    if had_previous:
        shutil.copyfile(net_path, previous)

    log(f"2/5 netconvert ({len(patch_files)} patch file(s))")
    build = build_network(
        osm_pbf_path=Path(extract.output_path),
        output_path=net_path,
        patch_files=patch_files,
        run=run,
    )

    log("3/5 validated by the build; hash the net")
    content_sha = net_content_sha256(net_path)
    version = netconvert_version(run)

    snapshot = load_snapshot(snapshot_path)
    assert snapshot is not None
    reference = snapshot.network
    reproduced = None if reference is None else reference.content_sha256 == content_sha
    if update_snapshot or reference is None:
        snapshot.network = NetReference(
            content_sha256=content_sha,
            netconvert_version=version,
            patches=[p.name for p in patch_files],
        )
        save_snapshot(snapshot, snapshot_path)
        log(f"reference net pinned in {snapshot_path}")

    log("4/5 diff against previous net")
    diff_counts = None
    diff_markdown = None
    if diff_previous and had_previous:
        diff = diff_networks(previous, net_path)
        diff_counts = {
            kind: {
                "added": len(getattr(diff, kind).added),
                "removed": len(getattr(diff, kind).removed),
                "changed": len(getattr(diff, kind).changed),
            }
            for kind in ("edges", "lanes", "junctions")
        }
        diff_markdown = render_markdown(diff)

    log("5/5 provenance manifest")
    net_sha = sha256_of(net_path)
    manifest = build_run_manifest(
        repo_root=repo_root,
        city=city,
        kind="network_build",
        sumo_version=version,
        config_path=city_dir / "city.yaml",
        input_paths=[snapshot_path, Path(extract.output_path), *patch_files],
        extra={
            "net_path": str(net_path),
            "net_sha256": net_sha,
            "net_content_sha256": content_sha,
            "source_pbf_sha256": snapshot.source.sha256,
            "validation": (
                f"{build.validation_errors} error(s), {build.validation_warnings} warning(s)"
            ),
            "reproduced": str(reproduced),
        },
    )
    manifest_path = write_run_manifest(manifest, network_dir / "builds")
    if diff_markdown is not None:
        (manifest_path.parent / "diff.md").write_text(diff_markdown, encoding="utf-8")
        (manifest_path.parent / "diff-counts.json").write_text(
            json.dumps(diff_counts, indent=2) + "\n", encoding="utf-8"
        )

    return RebuildResult(
        net_path=str(net_path),
        net_sha256=net_sha,
        content_sha256=content_sha,
        netconvert_version=version,
        patch_files=[str(p) for p in patch_files],
        validation_errors=build.validation_errors,
        validation_warnings=build.validation_warnings,
        validation_blocking=build.validation_errors > 0,
        reference_pinned=reference is not None,
        reproduced=reproduced,
        diff_counts=diff_counts,
        manifest_path=str(manifest_path),
    )
