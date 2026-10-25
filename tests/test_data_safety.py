from pathlib import Path

import pytest

from arteria.data_safety import check_files, find_repo_root, sha256_of


def _write_manifest(repo_root: Path, sha256: str) -> None:
    city_dir = repo_root / "cities" / "testcity"
    city_dir.mkdir(parents=True)
    (city_dir / "data-manifest.yaml").write_text(
        f"""
sources:
  - id: restricted-fixture
    name: "Restricted fixture"
    description: "test"
    roadmap_ref: P0.6
    agency: test
    license: TBD
    visibility: restricted
    sha256: "{sha256}"
    status: deferred
    notes: null
"""
    )


def test_flags_a_file_matching_a_restricted_checksum(tmp_path: Path) -> None:
    secret = tmp_path / "secret.csv"
    secret.write_text("sensitive content")
    _write_manifest(tmp_path, sha256_of(secret))

    violations = check_files([secret], tmp_path)

    assert len(violations) == 1
    assert "secret.csv" in violations[0]


def test_does_not_flag_an_unrelated_file(tmp_path: Path) -> None:
    other = tmp_path / "readme.md"
    other.write_text("just docs")
    _write_manifest(tmp_path, "0" * 64)

    assert check_files([other], tmp_path) == []


def test_find_repo_root_locates_git_dir_regardless_of_cwd_depth(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)

    assert find_repo_root(nested) == tmp_path
    assert find_repo_root(tmp_path) == tmp_path


def test_find_repo_root_raises_when_no_git_dir_is_found(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        find_repo_root(tmp_path / "nowhere")
