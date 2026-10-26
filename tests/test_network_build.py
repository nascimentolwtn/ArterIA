import subprocess
from pathlib import Path

import pytest

from arteria.network.build import (
    NetconvertError,
    build_network,
    default_netconvert_options,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_default_netconvert_options_are_all_dashed_flags():
    options = default_netconvert_options()
    assert options
    assert all(isinstance(opt, str) and opt.startswith("--") for opt in options)


def test_build_network_raises_file_not_found_for_missing_pbf(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        build_network(
            osm_pbf_path=tmp_path / "missing.osm.pbf",
            output_path=tmp_path / "out.net.xml",
            run=lambda cmd, **kwargs: subprocess.CompletedProcess(cmd, 0),
        )


def _fake_run_writing(fixture_name: str):
    fixture_text = (FIXTURES / fixture_name).read_text(encoding="utf-8")

    def fake_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
        if cmd[0] == "osmium":
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
        output_path = Path(cmd[cmd.index("--output-file") + 1])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(fixture_text, encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, stdout="netconvert stdout\n", stderr="")

    return fake_run


def test_build_network_success_with_clean_toy_network_has_no_findings(tmp_path: Path):
    osm_pbf_path = tmp_path / "source.osm.pbf"
    osm_pbf_path.write_bytes(b"fake-osm-bytes")
    output_path = tmp_path / "out" / "city.net.xml"

    result = build_network(
        osm_pbf_path=osm_pbf_path,
        output_path=output_path,
        run=_fake_run_writing("toy-net-valid.net.xml"),
    )

    assert result.net_xml_path == str(output_path)
    assert result.validation_errors == 0
    assert result.validation_warnings == 0
    assert "netconvert stdout" in result.log


def test_build_network_success_with_broken_toy_network_reports_findings(tmp_path: Path):
    osm_pbf_path = tmp_path / "source.osm.pbf"
    osm_pbf_path.write_bytes(b"fake-osm-bytes")
    output_path = tmp_path / "out" / "city.net.xml"

    result = build_network(
        osm_pbf_path=osm_pbf_path,
        output_path=output_path,
        run=_fake_run_writing("toy-net-broken.net.xml"),
    )

    assert result.validation_errors == 5
    assert result.validation_warnings == 2


def test_build_network_command_shape_includes_type_files_and_extra_options(tmp_path: Path):
    osm_pbf_path = tmp_path / "source.osm.pbf"
    osm_pbf_path.write_bytes(b"fake-osm-bytes")
    output_path = tmp_path / "out" / "city.net.xml"
    type_file = tmp_path / "typemap.xml"

    captured_cmd = {}

    def fake_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
        if cmd[0] == "osmium":
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
        captured_cmd["cmd"] = cmd
        captured_cmd["kwargs"] = kwargs
        out = Path(cmd[cmd.index("--output-file") + 1])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text((FIXTURES / "toy-net-valid.net.xml").read_text(encoding="utf-8"))
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    build_network(
        osm_pbf_path=osm_pbf_path,
        output_path=output_path,
        type_files=[type_file],
        extra_options=["--extra-flag", "value"],
        run=fake_run,
    )

    cmd = captured_cmd["cmd"]
    assert cmd[0] == "netconvert"
    assert "--osm-files" in cmd
    assert cmd[cmd.index("--osm-files") + 1] == str(tmp_path / "source.osm.xml")
    assert "--output-file" in cmd
    assert cmd[cmd.index("--output-file") + 1] == str(output_path)
    assert "--type-files" in cmd
    assert cmd[cmd.index("--type-files") + 1] == str(type_file)
    # extra_options appended last
    assert cmd[-2:] == ["--extra-flag", "value"]
    assert captured_cmd["kwargs"] == {"capture_output": True, "text": True}


def test_build_network_raises_netconvert_error_with_stderr_on_nonzero_returncode(tmp_path: Path):
    osm_pbf_path = tmp_path / "source.osm.pbf"
    osm_pbf_path.write_bytes(b"fake-osm-bytes")

    def failing_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="netconvert: bad option")

    with pytest.raises(NetconvertError) as excinfo:
        build_network(
            osm_pbf_path=osm_pbf_path,
            output_path=tmp_path / "out.net.xml",
            run=failing_run,
        )

    assert "netconvert: bad option" in str(excinfo.value)


def test_build_network_converts_pbf_to_osm_xml_with_osmium_before_netconvert(tmp_path: Path):
    osm_pbf_path = tmp_path / "source.osm.pbf"
    osm_pbf_path.write_bytes(b"fake-osm-bytes")
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
        calls.append(cmd)
        if cmd[0] == "netconvert":
            out = Path(cmd[cmd.index("--output-file") + 1])
            out.write_text((FIXTURES / "toy-net-valid.net.xml").read_text(encoding="utf-8"))
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    build_network(
        osm_pbf_path=osm_pbf_path, output_path=tmp_path / "out" / "c.net.xml", run=fake_run
    )

    assert [c[0] for c in calls] == ["osmium", "netconvert"]
    assert calls[0][:3] == ["osmium", "cat", str(osm_pbf_path)]
