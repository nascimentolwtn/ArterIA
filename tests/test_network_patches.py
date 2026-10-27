import shutil
import subprocess
from pathlib import Path

import pytest

from arteria.network.build import build_network
from arteria.network.diff import diff_networks
from arteria.network.patches import PatchError, load_patch_files, patch_options

FIXTURES = Path(__file__).parent / "fixtures"


def _write_patches(tmp_path: Path, manifest: str, files: tuple[str, ...]) -> Path:
    patches = tmp_path / "patches"
    patches.mkdir()
    for name in files:
        (patches / name).write_text("<edges/>")
    (patches / "manifest.yaml").write_text(manifest)
    return patches


def test_no_manifest_or_empty_manifest_means_no_patches(tmp_path: Path):
    assert load_patch_files(tmp_path) == []
    (tmp_path / "manifest.yaml").write_text("patches: []\n")
    assert load_patch_files(tmp_path) == []


def test_manifest_order_is_kept_and_options_group_by_kind(tmp_path: Path):
    patches = _write_patches(
        tmp_path,
        "patches:\n"
        "  - {file: 001-a.edg.xml, reason: r}\n"
        "  - {file: 002-b.con.xml, reason: r}\n"
        "  - {file: 003-c.edg.xml, reason: r}\n",
        ("001-a.edg.xml", "002-b.con.xml", "003-c.edg.xml"),
    )
    files = load_patch_files(patches)

    assert [f.name for f in files] == ["001-a.edg.xml", "002-b.con.xml", "003-c.edg.xml"]
    assert patch_options(files) == [
        "--edge-files",
        f"{patches / '001-a.edg.xml'},{patches / '003-c.edg.xml'}",
        "--connection-files",
        str(patches / "002-b.con.xml"),
    ]


def test_missing_file_and_bad_suffix_are_errors(tmp_path: Path):
    patches = _write_patches(tmp_path, "patches:\n  - {file: gone.edg.xml, reason: r}\n", ())
    with pytest.raises(PatchError, match="does not exist"):
        load_patch_files(patches)
    (patches / "manifest.yaml").write_text("patches:\n  - {file: x.txt, reason: r}\n")
    with pytest.raises(PatchError, match="must end with"):
        load_patch_files(patches)


def test_build_network_runs_a_second_pass_only_when_patches_exist(tmp_path: Path):
    osm = tmp_path / "source.osm.xml"
    osm.write_text("<osm/>")
    patch = tmp_path / "001-a.edg.xml"
    patch.write_text("<edges/>")
    toy = (FIXTURES / "toy-net-valid.net.xml").read_text()
    commands: list[list[str]] = []

    def fake_run(cmd, **kwargs):
        commands.append(cmd)
        Path(cmd[cmd.index("--output-file") + 1]).write_text(toy)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    build_network(osm_pbf_path=osm, output_path=tmp_path / "c.net.xml", run=fake_run)
    assert len(commands) == 1

    commands.clear()
    result = build_network(
        osm_pbf_path=osm, output_path=tmp_path / "c.net.xml", patch_files=[patch], run=fake_run
    )
    assert len(commands) == 2
    assert commands[0][commands[0].index("--output-file") + 1].endswith("c.base.net.xml")
    assert "--osm-files" not in commands[1]
    assert commands[1][commands[1].index("--sumo-net-file") + 1].endswith("c.base.net.xml")
    assert commands[1][commands[1].index("--edge-files") + 1] == str(patch)
    assert result.patch_files == [str(patch)]


@pytest.mark.skipif(shutil.which("netconvert") is None, reason="needs the netconvert binary")
def test_patch_is_applied_by_real_netconvert(tmp_path: Path):
    smoke = FIXTURES / "smoke"
    base = tmp_path / "base.net.xml"
    patched = tmp_path / "patched.net.xml"
    subprocess.run(
        [
            "netconvert",
            "--node-files",
            str(smoke / "toy.nod.xml"),
            "--edge-files",
            str(smoke / "toy.edg.xml"),
            "--output-file",
            str(base),
        ],
        check=True,
        capture_output=True,
    )
    patch = tmp_path / "001-slow-ab.edg.xml"
    patch.write_text('<edges><edge id="ab" speed="5.00"/></edges>')
    subprocess.run(
        [
            "netconvert",
            "--sumo-net-file",
            str(base),
            "--output-file",
            str(patched),
            *patch_options([patch]),
        ],
        check=True,
        capture_output=True,
    )

    diff = diff_networks(base, patched)
    changed = {(c.id, c.attribute, c.new) for c in diff.lanes.changed}
    assert changed == {("ab_0", "speed", "5.00")}
