"""Pre-commit safety net (ADR 0004): refuse a commit that stages a file whose
bytes match a `visibility: restricted` entry's `sha256` in any
`cities/*/data-manifest.yaml`. A safety net, not the only control.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from arteria.config import load_data_manifest


def restricted_checksums(repo_root: Path) -> set[str]:
    checksums: set[str] = set()
    for manifest_path in repo_root.glob("cities/*/data-manifest.yaml"):
        manifest = load_data_manifest(manifest_path)
        for entry in manifest.sources:
            if entry.visibility == "restricted" and entry.sha256:
                checksums.add(entry.sha256.lower())
    return checksums


def find_repo_root(start: Path) -> Path:
    """Walk up from `start` looking for `.git`.

    Deliberately independent of `__file__`: if `arteria` is ever installed
    non-editably, `__file__` resolves into site-packages, nowhere near the
    checkout, and a root derived from it would silently find no manifests —
    the one safety net ADR 0004 relies on going quietly inert instead of
    failing loudly. `pre-commit` always runs hooks with cwd at the repo
    root, so `start` is normally `Path.cwd()`.
    """
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError(f"could not find repo root (no .git) above {start}")


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_files(paths: list[Path], repo_root: Path) -> list[str]:
    restricted = restricted_checksums(repo_root)
    if not restricted:
        return []
    violations = []
    for path in paths:
        if not path.is_file():
            continue
        if sha256_of(path) in restricted:
            violations.append(
                f"{path}: matches a restricted data-manifest checksum (ADR 0004) — do not commit it"
            )
    return violations


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    repo_root = find_repo_root(Path.cwd())
    violations = check_files([Path(p) for p in argv], repo_root)
    for v in violations:
        print(v, file=sys.stderr)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
