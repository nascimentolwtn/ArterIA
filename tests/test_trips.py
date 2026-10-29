"""Tests for `arteria.demand.trips` (roadmap P3.3).

Unit tests inject a fake `run` (ADR 0009: no real SUMO binaries needed
remotely). The real-binary round-trip tests are skipped where
`od2trips`/`duarouter`/`routeSampler.py` aren't available, same pattern as
`tests/test_network_patches.py`'s `test_patch_is_applied_by_real_netconvert`.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from arteria.demand.trips import (
    TripGenerationError,
    run_duarouter,
    run_od2trips,
    run_route_sampler,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _fake_run(output_flag: str, content: str):
    commands: list[list[str]] = []

    def fake(cmd, **kwargs):
        commands.append(cmd)
        Path(cmd[cmd.index(output_flag) + 1]).write_text(content)
        return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")

    return commands, fake


def _failing_run(cmd, **kwargs):
    return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="boom")


# -- od2trips -----------------------------------------------------------


def test_run_od2trips_raises_for_missing_taz_file(tmp_path: Path):
    od = tmp_path / "toy.od"
    od.write_text("$O;D2\n")
    with pytest.raises(FileNotFoundError, match="TAZ file"):
        run_od2trips(
            taz_file=tmp_path / "missing.taz.xml",
            od_matrix_files=[od],
            output_path=tmp_path / "out.trips.xml",
        )


def test_run_od2trips_raises_for_missing_od_matrix_files(tmp_path: Path):
    taz = tmp_path / "toy.taz.xml"
    taz.write_text("<tazs/>")
    with pytest.raises(FileNotFoundError, match="OD matrix"):
        run_od2trips(
            taz_file=taz,
            od_matrix_files=[tmp_path / "missing.od"],
            output_path=tmp_path / "out.trips.xml",
        )


def test_run_od2trips_command_shape_and_output(tmp_path: Path):
    taz = tmp_path / "toy.taz.xml"
    taz.write_text("<tazs/>")
    od = tmp_path / "toy.od"
    od.write_text("$O;D2\n")
    out = tmp_path / "out.trips.xml"
    commands, fake = _fake_run("--output-file", "<routes/>")

    result = run_od2trips(
        taz_file=taz,
        od_matrix_files=[od],
        output_path=out,
        extra_options=["--seed", "1"],
        run=fake,
    )

    assert result.output_path == str(out)
    assert out.read_text() == "<routes/>"
    [cmd] = commands
    assert cmd[0] == "od2trips"
    assert cmd[cmd.index("--taz-files") + 1] == str(taz)
    assert cmd[cmd.index("--od-matrix-files") + 1] == str(od)
    assert cmd[-2:] == ["--seed", "1"]


def test_run_od2trips_raises_on_nonzero_returncode(tmp_path: Path):
    taz = tmp_path / "toy.taz.xml"
    taz.write_text("<tazs/>")
    od = tmp_path / "toy.od"
    od.write_text("$O;D2\n")
    with pytest.raises(TripGenerationError, match="boom"):
        run_od2trips(
            taz_file=taz,
            od_matrix_files=[od],
            output_path=tmp_path / "out.trips.xml",
            run=_failing_run,
        )


# -- duarouter ------------------------------------------------------------


def test_run_duarouter_raises_for_missing_net_file(tmp_path: Path):
    trips = tmp_path / "toy.trips.xml"
    trips.write_text("<routes/>")
    with pytest.raises(FileNotFoundError, match="Net file"):
        run_duarouter(
            net_file=tmp_path / "missing.net.xml",
            trips_files=[trips],
            output_path=tmp_path / "out.rou.xml",
        )


def test_run_duarouter_command_shape_includes_additional_files(tmp_path: Path):
    net = tmp_path / "toy.net.xml"
    net.write_text("<net/>")
    trips = tmp_path / "toy.trips.xml"
    trips.write_text("<routes/>")
    taz = tmp_path / "toy.taz.xml"
    taz.write_text("<tazs/>")
    out = tmp_path / "out.rou.xml"
    commands, fake = _fake_run("--output-file", "<routes/>")

    result = run_duarouter(
        net_file=net,
        trips_files=[trips],
        output_path=out,
        additional_files=[taz],
        run=fake,
    )

    assert result.output_path == str(out)
    [cmd] = commands
    assert cmd[0] == "duarouter"
    assert cmd[cmd.index("--net-file") + 1] == str(net)
    assert cmd[cmd.index("--route-files") + 1] == str(trips)
    assert cmd[cmd.index("--additional-files") + 1] == str(taz)


def test_run_duarouter_raises_on_nonzero_returncode(tmp_path: Path):
    net = tmp_path / "toy.net.xml"
    net.write_text("<net/>")
    trips = tmp_path / "toy.trips.xml"
    trips.write_text("<routes/>")
    with pytest.raises(TripGenerationError, match="boom"):
        run_duarouter(
            net_file=net,
            trips_files=[trips],
            output_path=tmp_path / "out.rou.xml",
            run=_failing_run,
        )


# -- routeSampler ---------------------------------------------------------


def test_run_route_sampler_raises_when_sumo_home_unset(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("SUMO_HOME", raising=False)
    routes = tmp_path / "toy.rou.xml"
    routes.write_text("<routes/>")
    edgedata = tmp_path / "edgedata.xml"
    edgedata.write_text("<data/>")
    with pytest.raises(FileNotFoundError, match="SUMO_HOME"):
        run_route_sampler(
            route_files=[routes],
            edgedata_files=[edgedata],
            output_path=tmp_path / "out.rou.xml",
            sumo_home=None,
        )


def test_run_route_sampler_raises_for_missing_script(tmp_path: Path):
    routes = tmp_path / "toy.rou.xml"
    routes.write_text("<routes/>")
    edgedata = tmp_path / "edgedata.xml"
    edgedata.write_text("<data/>")
    with pytest.raises(FileNotFoundError, match="routeSampler.py"):
        run_route_sampler(
            route_files=[routes],
            edgedata_files=[edgedata],
            output_path=tmp_path / "out.rou.xml",
            sumo_home=str(tmp_path),
        )


def test_run_route_sampler_command_shape_and_turn_files(tmp_path: Path):
    sumo_home = tmp_path / "sumo"
    script = sumo_home / "tools" / "routeSampler.py"
    script.parent.mkdir(parents=True)
    script.write_text("# fake")

    routes = tmp_path / "toy.rou.xml"
    routes.write_text("<routes/>")
    edgedata = tmp_path / "edgedata.xml"
    edgedata.write_text("<data/>")
    turns = tmp_path / "turns.xml"
    turns.write_text("<data/>")
    out = tmp_path / "out.rou.xml"
    commands, fake = _fake_run("--output-file", "<routes/>")

    result = run_route_sampler(
        route_files=[routes],
        edgedata_files=[edgedata],
        output_path=out,
        turn_files=[turns],
        sumo_home=str(sumo_home),
        run=fake,
    )

    assert result.output_path == str(out)
    [cmd] = commands
    assert cmd[0] == sys.executable
    assert str(script) in cmd
    assert cmd[cmd.index("--route-files") + 1] == str(routes)
    assert cmd[cmd.index("--edgedata-files") + 1] == str(edgedata)
    assert cmd[cmd.index("--turn-files") + 1] == str(turns)


def test_run_route_sampler_raises_on_nonzero_returncode(tmp_path: Path):
    sumo_home = tmp_path / "sumo"
    script = sumo_home / "tools" / "routeSampler.py"
    script.parent.mkdir(parents=True)
    script.write_text("# fake")
    routes = tmp_path / "toy.rou.xml"
    routes.write_text("<routes/>")
    edgedata = tmp_path / "edgedata.xml"
    edgedata.write_text("<data/>")

    with pytest.raises(TripGenerationError, match="boom"):
        run_route_sampler(
            route_files=[routes],
            edgedata_files=[edgedata],
            output_path=tmp_path / "out.rou.xml",
            sumo_home=str(sumo_home),
            run=_failing_run,
        )


# -- real-binary round trip (desk-only) ----------------------------------

_SUMO_HOME = os.environ.get("SUMO_HOME")
_HAS_SUMO_TOOLS = (
    shutil.which("netconvert") is not None
    and shutil.which("od2trips") is not None
    and shutil.which("duarouter") is not None
    and _SUMO_HOME is not None
    and (Path(_SUMO_HOME) / "tools" / "routeSampler.py").exists()
)


@pytest.mark.skipif(not _HAS_SUMO_TOOLS, reason="needs real SUMO binaries and SUMO_HOME/tools")
def test_real_round_trip_od_to_sampled_routes(tmp_path: Path):
    smoke = FIXTURES / "smoke"
    net = tmp_path / "toy.net.xml"
    subprocess.run(
        [
            "netconvert",
            "--node-files",
            str(smoke / "toy.nod.xml"),
            "--edge-files",
            str(smoke / "toy.edg.xml"),
            "--output-file",
            str(net),
        ],
        check=True,
        capture_output=True,
    )

    taz = tmp_path / "toy.taz.xml"
    taz.write_text('<tazs><taz id="A" edges="ab"/><taz id="B" edges="bc"/></tazs>')
    od = tmp_path / "toy.od"
    od.write_text("$O;D2\n* From-Time  To-Time\n0.00 1.00\n* Factor\n1.00\nA     B     10.00\n")

    trips_path = tmp_path / "toy.trips.xml"
    trips_result = run_od2trips(taz_file=taz, od_matrix_files=[od], output_path=trips_path)
    assert Path(trips_result.output_path).exists()
    assert "<trip " in Path(trips_result.output_path).read_text()

    routes_path = tmp_path / "toy.rou.xml"
    routes_result = run_duarouter(net_file=net, trips_files=[trips_path], output_path=routes_path)
    routes_xml = Path(routes_result.output_path).read_text()
    assert "<vehicle " in routes_xml
    assert 'edges="ab bc"' in routes_xml

    edgedata = tmp_path / "edgedata.xml"
    edgedata.write_text(
        '<data><interval id="i1" begin="0" end="3600">'
        '<edge id="ab" entered="10"/><edge id="bc" entered="8"/>'
        "</interval></data>"
    )
    sampled_path = tmp_path / "sampled.rou.xml"
    sampled_result = run_route_sampler(
        route_files=[routes_path], edgedata_files=[edgedata], output_path=sampled_path
    )
    sampled_xml = Path(sampled_result.output_path).read_text()
    assert "<vehicle " in sampled_xml
    assert 'edges="ab bc"' in sampled_xml
