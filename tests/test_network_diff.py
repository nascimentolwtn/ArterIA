import shutil
from pathlib import Path

from typer.testing import CliRunner

from arteria.cli import app
from arteria.network.diff import diff_networks, net_content_sha256, render_markdown

FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()


def _net(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(f'<?xml version="1.0"?>\n<net>\n{body}\n</net>\n')
    return path


def _edge(edge_id: str, *lanes: str, to: str = "b") -> str:
    return f'<edge id="{edge_id}" from="a" to="{to}" priority="1">{"".join(lanes)}</edge>'


def _lane(lane_id: str, speed: str, length: str, allow: str = "") -> str:
    allow_attr = f' allow="{allow}"' if allow else ""
    return f'<lane id="{lane_id}" speed="{speed}" length="{length}"{allow_attr}/>'


OLD = "\n".join(
    [
        _edge("e1", _lane("e1_0", "13.89", "100.00", "passenger bus")),
        _edge("e2", _lane("e2_0", "13.89", "50.00"), to="c"),
        '<edge id=":b_0" function="internal"><lane id=":b_0_0" speed="3" length="5"/></edge>',
        '<junction id="b" type="priority" x="1.0" y="2.0"/>',
        '<junction id="c" type="priority" x="9.0" y="2.0"/>',
    ]
)
NEW = "\n".join(
    [
        _edge(
            "e1",
            _lane("e1_0", "8.33", "100.001", "bus passenger"),
            _lane("e1_1", "8.33", "100.00"),
        ),
        _edge("e3", _lane("e3_0", "13.89", "70.00"), to="d"),
        '<junction id="b" type="traffic_light" x="1.0" y="2.0"/>',
        '<junction id="d" type="priority" x="9.0" y="2.0"/>',
    ]
)


def test_diff_reports_added_removed_and_changed(tmp_path: Path):
    diff = diff_networks(_net(tmp_path, "old.net.xml", OLD), _net(tmp_path, "new.net.xml", NEW))

    assert diff.edges.added == ["e3"]
    assert diff.edges.removed == ["e2"]
    assert [(c.id, c.attribute, c.old, c.new) for c in diff.edges.changed] == [
        ("e1", "numLanes", "1", "2")
    ]
    assert diff.lanes.added == ["e1_1", "e3_0"]
    assert diff.lanes.removed == ["e2_0"]
    # length 100.00 vs 100.001 rounds equal; allow is order-insensitive; speed changed
    assert [(c.id, c.attribute) for c in diff.lanes.changed] == [("e1_0", "speed")]
    assert diff.junctions.added == ["d"]
    assert diff.junctions.removed == ["c"]
    assert [(c.id, c.old, c.new) for c in diff.junctions.changed] == [
        ("b", "priority", "traffic_light")
    ]
    assert not diff.identical


def test_identical_networks_and_markdown(tmp_path: Path):
    net = _net(tmp_path, "n.net.xml", OLD)
    diff = diff_networks(net, net)
    assert diff.identical
    assert "identical" in render_markdown(diff)


def test_markdown_truncates_long_lists(tmp_path: Path):
    many = "\n".join(
        f'<edge id="x{i}" from="a" to="b"><lane id="x{i}_0"/></edge>' for i in range(30)
    )
    diff = diff_networks(_net(tmp_path, "o.net.xml", ""), _net(tmp_path, "n.net.xml", many))
    assert "(+5 more)" in render_markdown(diff, limit=25)


def test_content_hash_ignores_netconvert_header_comment(tmp_path: Path):
    body = '<net><edge id="e"/></net>\n'
    a = tmp_path / "a.net.xml"
    b = tmp_path / "b.net.xml"
    a.write_text('<?xml version="1.0" encoding="UTF-8"?>\n\n<!-- generated on T1 -->\n' + body)
    b.write_text('<?xml version="1.0" encoding="UTF-8"?>\n\n<!-- generated on T2 -->\n' + body)
    c = tmp_path / "c.net.xml"
    c.write_text('<?xml version="1.0" encoding="UTF-8"?>\n\n<!-- generated on T1 -->\n<net/>\n')

    assert net_content_sha256(a) == net_content_sha256(b)
    assert net_content_sha256(a) != net_content_sha256(c)


def test_cli_diff_writes_json_and_markdown(tmp_path: Path):
    old = tmp_path / "old.net.xml"
    shutil.copy(FIXTURES / "toy-net-valid.net.xml", old)
    new = _net(tmp_path, "new.net.xml", NEW)
    json_out = tmp_path / "d.json"
    md_out = tmp_path / "d.md"

    result = runner.invoke(
        app,
        ["network", "diff", "--old", str(old), "--new", str(new), "--json", str(json_out),
         "--markdown", str(md_out)],
    )  # fmt: skip

    assert result.exit_code == 0, result.stdout
    assert '"edges"' in json_out.read_text()
    assert "| edges |" in md_out.read_text()
