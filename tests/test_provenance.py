import json
import subprocess
from pathlib import Path

from arteria.provenance import (
    build_run_manifest,
    git_sha,
    load_run_manifest,
    write_run_manifest,
)


def _init_git_repo(repo_root: Path) -> str:
    subprocess.run(["git", "init", "-q"], cwd=repo_root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_root, check=True)
    (repo_root / "README.md").write_text("test repo")
    subprocess.run(["git", "add", "README.md"], cwd=repo_root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo_root, check=True)
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def test_git_sha_matches_head_of_a_real_repo(tmp_path: Path) -> None:
    expected = _init_git_repo(tmp_path)

    assert git_sha(tmp_path) == expected


def test_git_sha_is_none_outside_a_repo(tmp_path: Path) -> None:
    assert git_sha(tmp_path) is None


def test_build_run_manifest_hashes_config_and_inputs(tmp_path: Path) -> None:
    config = tmp_path / "city.yaml"
    config.write_text("name: testcity\n")
    counts = tmp_path / "counts.csv"
    counts.write_text("edge,count\nA,10\n")

    manifest = build_run_manifest(
        repo_root=tmp_path,
        city="testcity",
        kind="simulation",
        sumo_version="1.20.0",
        config_path=config,
        input_paths=[counts],
        seed=42,
    )

    assert manifest.city == "testcity"
    assert manifest.kind == "simulation"
    assert manifest.sumo_version == "1.20.0"
    assert manifest.seed == 42
    assert len(manifest.config_hash) == 64
    assert len(manifest.inputs) == 1
    assert manifest.inputs[0].path == str(counts)
    assert len(manifest.inputs[0].sha256) == 64
    assert manifest.git_sha is None  # tmp_path is not a git repo


def test_build_run_manifest_is_deterministic_for_unchanged_inputs(tmp_path: Path) -> None:
    config = tmp_path / "city.yaml"
    config.write_text("name: testcity\n")

    first = build_run_manifest(
        repo_root=tmp_path,
        city="testcity",
        kind="calibration",
        sumo_version="1.20.0",
        config_path=config,
    )
    second = build_run_manifest(
        repo_root=tmp_path,
        city="testcity",
        kind="calibration",
        sumo_version="1.20.0",
        config_path=config,
    )

    assert first.config_hash == second.config_hash
    assert first.run_id != second.run_id  # each run still gets its own id


def test_write_and_load_run_manifest_round_trips(tmp_path: Path) -> None:
    config = tmp_path / "city.yaml"
    config.write_text("name: testcity\n")
    manifest = build_run_manifest(
        repo_root=tmp_path,
        city="testcity",
        kind="optimization",
        sumo_version="1.20.0",
        config_path=config,
        run_id="fixed-run-id",
        extra={"algo": "nsga2"},
    )
    runs_root = tmp_path / "runs"

    manifest_path = write_run_manifest(manifest, runs_root)

    assert manifest_path == runs_root / "testcity" / "fixed-run-id" / "manifest.json"
    on_disk = json.loads(manifest_path.read_text())
    assert on_disk["extra"] == {"algo": "nsga2"}
    loaded = load_run_manifest(manifest_path)
    assert loaded == manifest
