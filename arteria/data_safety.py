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
    repo_root = Path(__file__).resolve().parent.parent
    violations = check_files([Path(p) for p in argv], repo_root)
    for v in violations:
        print(v, file=sys.stderr)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
