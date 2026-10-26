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
        f for f in report.findings if f.check == "connection_consistency" and "e99" in f.message
    ]
    assert len(unknown_edge) == 1
    assert unknown_edge[0].severity == "error"


def test_broken_toy_network_flags_out_of_range_lane():
    report = validate_network(FIXTURES / "toy-net-broken.net.xml")
    out_of_range = [
        f for f in report.findings if f.check == "connection_consistency" and "toLane" in f.message
    ]
    assert len(out_of_range) == 1
    assert "e3" in out_of_range[0].message


def test_broken_toy_network_flags_missing_speed():
    report = validate_network(FIXTURES / "toy-net-broken.net.xml")
    missing_speed = [f for f in report.findings if f.check == "speed_limit"]
    assert len(missing_speed) == 1
    assert "e3_0" in missing_speed[0].message


def test_no_oneway_attribute_findings_and_pair_stats():
    report = validate_network(FIXTURES / "toy-net-broken.net.xml")
    assert not [f for f in report.findings if f.check == "oneway_status"]
    # e1 j1->j2, e2 j2->j3, e3 j1->j3: no opposite partners.
    assert report.stats["one_way_edges"] == 3
    assert report.stats["two_way_edges"] == 0


def test_opposite_edge_pairs_count_as_two_way(tmp_path):
    net = tmp_path / "n.net.xml"
    net.write_text(
        '<net><junction id="a"/><junction id="b"/>'
        '<edge id="ab" from="a" to="b"><lane id="ab_0" index="0" speed="10"/></edge>'
        '<edge id="ba" from="b" to="a"><lane id="ba_0" index="0" speed="10"/></edge>'
        "</net>"
    )
    report = validate_network(net)
    assert report.stats["two_way_edges"] == 2
    assert report.stats["one_way_edges"] == 0
    assert report.findings == []


def test_internal_edges_are_skipped(tmp_path):
    net = tmp_path / "n.net.xml"
    net.write_text(
        '<net><junction id="a"/><junction id="b"/>'
        '<edge id="ab" from="a" to="b"><lane id="ab_0" index="0" speed="10"/></edge>'
        '<edge id="ba" from="b" to="a"><lane id="ba_0" index="0" speed="10"/></edge>'
        '<edge id=":a_0" function="internal"><lane id=":a_0_0" index="0"/></edge>'
        "</net>"
    )
    report = validate_network(net)
    assert report.findings == []
    assert report.stats["edges"] == 2


def test_scc_reports_main_component_and_orphans(tmp_path):
    net = tmp_path / "n.net.xml"
    lane = '<lane id="x_0" index="0" speed="10"/>'
    edges = [
        ("ab", "a", "b"),
        ("ba", "b", "a"),
        ("bc", "b", "c"),
        ("ca", "c", "a"),
        ("de", "d", "e"),
        ("ed", "e", "d"),
        ("ad", "a", "d"),
    ]
    body = "".join(f'<edge id="{i}" from="{f}" to="{t}">{lane}</edge>' for i, f, t in edges)
    junctions = "".join(f'<junction id="{j}"/>' for j in "abcde")
    net.write_text(f"<net>{junctions}{body}</net>")
    report = validate_network(net)
    scc = [f for f in report.findings if f.check == "scc"]
    assert len(scc) == 1
    assert "3 of 5" in scc[0].message
    assert report.stats["main_component_junctions"] == 3
    assert report.stats["orphan_junctions"] == 2


def test_real_slice_has_no_blocking_issues():
    report = validate_network(FIXTURES / "real-slice-sjc-b.net.xml")
    assert not report.has_blocking_issues
    assert not [f for f in report.findings if f.check == "oneway_status"]
    # Internal edges are present in the file but not counted.
    assert report.stats["edges"] == 50
    assert report.stats["junctions"] == 24


def test_real_slice_scc_summary_and_clip_boundary_split():
    report = validate_network(FIXTURES / "real-slice-sjc-b.net.xml")
    scc = [f for f in report.findings if f.check == "scc"]
    assert len(scc) == 1
    assert report.stats["main_component_junctions"] == 12
    assert report.stats["orphan_junctions"] == 12
    boundary = [f for f in report.findings if f.check == "clip_boundary_dead_end"]
    assert len(boundary) == report.stats["clip_boundary_dead_ends"] == 4
    assert all(f.severity == "info" for f in boundary)
    assert not [f for f in report.findings if f.check == "dead_end"]


def test_real_slice_unsignalised_traffic_light_clusters_are_warnings():
    report = validate_network(FIXTURES / "real-slice-sjc-b.net.xml")
    tl = [f for f in report.findings if f.check == "traffic_light_logic"]
    assert len(tl) == 2
    assert all(f.severity == "warning" for f in tl)
    assert all("unsignalised" in f.message for f in tl)


def test_traffic_light_with_bound_connections_but_no_logic_is_error(tmp_path):
    net = tmp_path / "n.net.xml"
    net.write_text(
        '<net><junction id="a" type="traffic_light"/><junction id="b"/>'
        '<edge id="ab" from="a" to="b"><lane id="ab_0" index="0" speed="10"/></edge>'
        '<edge id="ba" from="b" to="a"><lane id="ba_0" index="0" speed="10"/></edge>'
        '<connection from="ba" to="ab" fromLane="0" toLane="0" tl="a" linkIndex="0"/>'
        "</net>"
    )
    report = validate_network(net)
    tl = [f for f in report.findings if f.check == "traffic_light_logic"]
    assert [f.severity for f in tl] == ["error"]


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
