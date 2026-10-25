import shutil
from pathlib import Path

from typer.testing import CliRunner

from arteria.cli import app

runner = CliRunner()
REPO_ROOT = Path(__file__).parent.parent


def test_doctor_runs_and_reports_python_and_sumo() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Python:" in result.stdout
    assert "SUMO_HOME:" in result.stdout


def test_city_new_scaffolds_and_validates(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cities").mkdir()
    shutil.copytree(REPO_ROOT / "cities" / "_template", tmp_path / "cities" / "_template")

    result = runner.invoke(app, ["city", "new", "testcity"])

    assert result.exit_code == 0
    assert (tmp_path / "cities" / "testcity" / "city.yaml").exists()


def test_city_new_refuses_to_overwrite(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cities" / "existing").mkdir(parents=True)

    result = runner.invoke(app, ["city", "new", "existing"])

    assert result.exit_code == 1


def test_osm_fetch_wires_arguments_through_with_a_local_pbf_path(
    tmp_path: Path, monkeypatch
) -> None:
    import arteria.network.osm_fetch as osm_fetch_module

    monkeypatch.chdir(tmp_path)
    (tmp_path / "cities" / "sjc").mkdir(parents=True)

    calls: dict = {}

    def fake_extract_candidate_polygon(path: Path, candidate_id: str) -> dict:
        calls["polygon_args"] = (path, candidate_id)
        return {"type": "FeatureCollection", "features": []}

    def fake_extract_osm(*, pbf_path, polygon_geojson, output_path, run=None):
        calls["extract_osm_args"] = (pbf_path, polygon_geojson, output_path)
        return osm_fetch_module.OsmExtractResult(
            output_path=str(output_path), sha256="deadbeef"
        )

    monkeypatch.setattr(
        osm_fetch_module, "extract_candidate_polygon", fake_extract_candidate_polygon
    )
    monkeypatch.setattr(osm_fetch_module, "extract_osm", fake_extract_osm)

    local_pbf = tmp_path / "local.osm.pbf"
    local_pbf.write_bytes(b"x")

    result = runner.invoke(
        app,
        ["osm", "fetch", "--city", "sjc", "--candidate", "b", "--pbf-path", str(local_pbf)],
    )

    assert result.exit_code == 0, result.stdout
    assert "deadbeef" in result.stdout
    assert calls["polygon_args"][1] == "b"
    assert calls["extract_osm_args"][0] == local_pbf
    expected_output = tmp_path / "cities" / "sjc" / "network" / "raw" / "sjc-b.osm.pbf"
    assert calls["extract_osm_args"][2] == expected_output


def test_osm_fetch_exits_nonzero_and_prints_message_on_error(tmp_path: Path, monkeypatch) -> None:
    import arteria.network.osm_fetch as osm_fetch_module

    monkeypatch.chdir(tmp_path)
    (tmp_path / "cities" / "sjc").mkdir(parents=True)

    def raising_extract_candidate_polygon(path: Path, candidate_id: str) -> dict:
        raise osm_fetch_module.OsmFetchError(f"no candidate {candidate_id!r}")

    monkeypatch.setattr(
        osm_fetch_module, "extract_candidate_polygon", raising_extract_candidate_polygon
    )

    local_pbf = tmp_path / "local.osm.pbf"
    local_pbf.write_bytes(b"x")

    result = runner.invoke(
        app,
        ["osm", "fetch", "--city", "sjc", "--candidate", "zz", "--pbf-path", str(local_pbf)],
    )

    assert result.exit_code == 1
    assert "no candidate 'zz'" in result.stderr


def test_network_build_wires_arguments_through_and_reports_validation_counts(
    tmp_path: Path, monkeypatch
) -> None:
    import arteria.network.build as build_module

    monkeypatch.chdir(tmp_path)

    calls: dict = {}

    def fake_build_network(*, osm_pbf_path, output_path, type_files=(), extra_options=(), run=None):
        calls["args"] = (osm_pbf_path, output_path, tuple(type_files), tuple(extra_options))
        return build_module.NetworkBuildResult(
            net_xml_path=str(output_path), log="ok", validation_errors=1, validation_warnings=2
        )

    monkeypatch.setattr(build_module, "build_network", fake_build_network)

    osm_pbf = tmp_path / "source.osm.pbf"
    osm_pbf.write_bytes(b"x")

    result = runner.invoke(
        app, ["network", "build", "--city", "sjc", "--osm-pbf", str(osm_pbf)]
    )

    assert result.exit_code == 0, result.stdout
    assert "1 error(s)" in result.stdout
    assert "2 warning(s)" in result.stdout
    assert "network validate" in result.stdout
    osm_pbf_path, output_path, type_files, extra_options = calls["args"]
    assert osm_pbf_path == osm_pbf
    assert output_path == tmp_path / "cities" / "sjc" / "network" / "sjc.net.xml"
    assert type_files == ()
    assert extra_options == ()


def test_network_build_exits_nonzero_on_netconvert_error(tmp_path: Path, monkeypatch) -> None:
    import arteria.network.build as build_module

    monkeypatch.chdir(tmp_path)

    def raising_build_network(**kwargs):
        raise build_module.NetconvertError("netconvert: bad option")

    monkeypatch.setattr(build_module, "build_network", raising_build_network)

    osm_pbf = tmp_path / "source.osm.pbf"
    osm_pbf.write_bytes(b"x")

    result = runner.invoke(
        app, ["network", "build", "--city", "sjc", "--osm-pbf", str(osm_pbf)]
    )

    assert result.exit_code == 1
    assert "netconvert: bad option" in result.stderr


def test_network_validate_prints_findings_and_exits_nonzero_for_broken_network() -> None:
    broken = REPO_ROOT / "tests" / "fixtures" / "toy-net-broken.net.xml"

    result = runner.invoke(
        app, ["network", "validate", "--city", "sjc", "--net", str(broken)]
    )

    assert result.exit_code == 1
    assert "dead_end" in result.stdout
    assert "connectivity" in result.stdout


def test_network_validate_exits_zero_for_clean_network() -> None:
    valid = REPO_ROOT / "tests" / "fixtures" / "toy-net-valid.net.xml"

    result = runner.invoke(
        app, ["network", "validate", "--city", "sjc", "--net", str(valid)]
    )

    assert result.exit_code == 0
