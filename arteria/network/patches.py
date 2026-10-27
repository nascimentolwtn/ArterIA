"""Network correction patches (roadmap P2.3).

SUMO 1.28's `netconvert` has no `--patch-files` option, and plain-XML edge
files given together with `--osm-files` are treated as *new* edges (they fail
with "from-node is not given"). The documented way to change an existing
network is to load it with `--sumo-net-file` plus plain-XML files, where an
`<edge id=.../>` with the same id overrides attributes (speed, numLanes,
allow, ...), `<delete .../>` removes things, and so on. So a build with patches
is two passes: OSM -> `<city>.base.net.xml`, then base + patches -> `<city>.net.xml`
(see `arteria.network.build.build_network`). Without patches the second pass
is skipped, because even a pass-through re-run rewrites the net.

`cities/<city>/network/patches/manifest.yaml` lists the patch files in the order
they are given to `netconvert`:

    patches:
      - file: 001-slow-service-road.edg.xml
        reason: why the correction is needed
        evidence: aerial imagery / field note / OSM way id
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import yaml
from pydantic import BaseModel

MANIFEST_FILENAME = "manifest.yaml"

# Plain-XML suffix -> netconvert option that loads it.
PATCH_OPTIONS = {
    ".nod.xml": "--node-files",
    ".edg.xml": "--edge-files",
    ".con.xml": "--connection-files",
    ".tll.xml": "--tllogic-files",
}


class PatchError(ValueError):
    pass


class PatchEntry(BaseModel):
    file: str
    reason: str
    evidence: str | None = None


def load_patch_files(patches_dir: Path) -> list[Path]:
    """Patch files listed in `patches_dir/manifest.yaml`, in order. A missing
    manifest or an empty list means no patches. Raises `PatchError` for an
    unknown suffix or a listed file that does not exist."""
    manifest_path = patches_dir / MANIFEST_FILENAME
    if not manifest_path.exists():
        return []
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    entries = [PatchEntry.model_validate(item) for item in data.get("patches") or []]
    files = []
    for entry in entries:
        path = patches_dir / entry.file
        if not any(entry.file.endswith(suffix) for suffix in PATCH_OPTIONS):
            raise PatchError(
                f"patch {entry.file!r}: name must end with one of {', '.join(PATCH_OPTIONS)}"
            )
        if not path.exists():
            raise PatchError(f"patch {entry.file!r} listed in {manifest_path} does not exist")
        files.append(path)
    return files


def patch_options(patch_files: Sequence[Path]) -> list[str]:
    """`netconvert` options for `patch_files`: one option per kind, files
    comma-joined in the given order."""
    grouped: dict[str, list[str]] = {}
    for path in patch_files:
        for suffix, option in PATCH_OPTIONS.items():
            if path.name.endswith(suffix):
                grouped.setdefault(option, []).append(str(path))
                break
        else:
            raise PatchError(f"unsupported patch file name: {path.name}")
    options: list[str] = []
    for option, paths in grouped.items():
        options += [option, ",".join(paths)]
    return options
