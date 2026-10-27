"""Run provenance manifests (roadmap P0.7).

Every simulation/optimization run (headless `sumo`, calibration, optimizer
batch — L15-L18) writes one `manifest.json` recording what produced its
outputs: git commit, SUMO version, random seed, a hash of the config used,
and checksums of its input files. Manifests let a later run (or another
person) tell whether re-running the same inputs should reproduce the same
outputs, without re-reading every file by hand.

This module only builds and writes the manifest; the run commands that
call it (`arteria sim run`, `arteria calibrate ...`, `arteria optimize
run`) land with their own roadmap phases (P3.6/P4/P7) and live outside
`ARTERIA_DATA`, so they are desk-only.
"""

from __future__ import annotations

import json
import subprocess
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from arteria.data_safety import sha256_of

RunKind = Literal["simulation", "calibration", "optimization", "network_build"]


class InputChecksum(BaseModel):
    path: str
    sha256: str


class RunManifest(BaseModel):
    run_id: str
    city: str
    kind: RunKind
    created_at: datetime
    git_sha: str | None
    sumo_version: str
    config_hash: str
    seed: int | None = None
    inputs: list[InputChecksum] = Field(default_factory=list)
    extra: dict[str, str] = Field(default_factory=dict)


def git_sha(repo_root: Path) -> str | None:
    """The current commit hash at `repo_root`, or `None` outside a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def new_run_id() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{uuid.uuid4().hex[:8]}"


def build_run_manifest(
    *,
    repo_root: Path,
    city: str,
    kind: RunKind,
    sumo_version: str,
    config_path: Path,
    input_paths: list[Path] | None = None,
    seed: int | None = None,
    run_id: str | None = None,
    extra: dict[str, str] | None = None,
) -> RunManifest:
    """Assemble a `RunManifest` from a config file and a run's input files.

    `config_path` and every path in `input_paths` must exist; their bytes
    are hashed with `sha256_of`, the same checksum the data-safety hook
    (ADR 0004) uses, so a manifest's hashes are directly comparable to a
    data-manifest entry's.
    """
    inputs = [InputChecksum(path=str(path), sha256=sha256_of(path)) for path in (input_paths or [])]
    return RunManifest(
        run_id=run_id or new_run_id(),
        city=city,
        kind=kind,
        created_at=datetime.now(UTC),
        git_sha=git_sha(repo_root),
        sumo_version=sumo_version,
        config_hash=sha256_of(config_path),
        seed=seed,
        inputs=inputs,
        extra=extra or {},
    )


def write_run_manifest(manifest: RunManifest, runs_root: Path) -> Path:
    """Write `manifest.json` to `runs_root/<city>/<run_id>/manifest.json`.

    Matches the local `ARTERIA_DATA` layout's `runs/<city>/<run-id>/`
    directory from `docs/roadmap.md`; `runs_root` is that layout's `runs/`
    root, not necessarily inside this repo.
    """
    run_dir = runs_root / manifest.city / manifest.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def load_run_manifest(path: Path) -> RunManifest:
    with open(path, encoding="utf-8") as f:
        return RunManifest.model_validate(json.load(f))
