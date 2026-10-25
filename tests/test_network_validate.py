from pathlib import Path

from arteria.network.validate import validate_network

FIXTURES = Path(__file__).parent / "fixtures"


def test_valid_toy_network_has_no_findings():
    report = validate_network(FIXTURES / "toy-net-valid.net.xml")
    assert report.findings == []
    assert not report.has_blocking_issues


def test_broken_toy_network_flags_dead_end():
    report = validate_network(FIXTURES / "toy-net-broken.net.xml")
    dead_ends = [f for f in report.findings if f.check == "dead_end"]
    assert len(dead_ends) == 1
    assert "j3" in dead_ends[0].message
    assert dead_ends[0].severity == "warning"


def test_broken_toy_network_flags_unreachable_junction():
    report = validate_network(FIXTURES / "toy-net-broken.net.xml")
    unreachable = [f for f in report.findings if f.check == "connectivity"]
    assert len(unreachable) == 1
    assert "j4" in unreachable[0].message
    assert unreachable[0].severity == "error"


def test_broken_toy_network_flags_unknown_connection_edge():
    report = validate_network(FIXTURES / "toy-net-broken.net.xml")
    unknown_edge = [
        f
        for f in report.findings
        if f.check == "connection_consistency" and "e99" in f.message
    ]
    assert len(unknown_edge) == 1
    assert unknown_edge[0].severity == "error"


def test_broken_toy_network_flags_out_of_range_lane():
    report = validate_network(FIXTURES / "toy-net-broken.net.xml")
    out_of_range = [
        f
        for f in report.findings
        if f.check == "connection_consistency" and "toLane" in f.message
    ]
    assert len(out_of_range) == 1
    assert "e3" in out_of_range[0].message


def test_broken_toy_network_flags_missing_speed():
    report = validate_network(FIXTURES / "toy-net-broken.net.xml")
    missing_speed = [f for f in report.findings if f.check == "speed_limit"]
    assert len(missing_speed) == 1
    assert "e3_0" in missing_speed[0].message


def test_broken_toy_network_flags_missing_oneway():
    report = validate_network(FIXTURES / "toy-net-broken.net.xml")
    missing_oneway = [f for f in report.findings if f.check == "oneway_status"]
    assert len(missing_oneway) == 1
    assert missing_oneway[0].severity == "warning"
    assert "e1" in missing_oneway[0].message


def test_broken_toy_network_flags_missing_traffic_light_logic():
    report = validate_network(FIXTURES / "toy-net-broken.net.xml")
    missing_tl = [f for f in report.findings if f.check == "traffic_light_logic"]
    assert len(missing_tl) == 1
    assert "j2" in missing_tl[0].message


def test_broken_toy_network_has_blocking_issues():
    report = validate_network(FIXTURES / "toy-net-broken.net.xml")
    assert report.has_blocking_issues
    assert len(report.by_severity("error")) >= 1
    assert len(report.by_severity("warning")) >= 1
