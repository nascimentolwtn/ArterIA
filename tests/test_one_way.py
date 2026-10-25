from pathlib import Path

import pytest

from arteria.interventions.one_way import EdgeNotFoundError, convert_to_one_way

FIXTURE = Path(__file__).parent / "fixtures" / "toy-one-way-net.net.xml"


def _toy_net() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def test_removing_a_two_way_edge_with_a_bypass_orphans_nothing() -> None:
    result = convert_to_one_way(_toy_net(), edge_id="-A")

    assert '<edge id="-A"' not in result.net_xml
    assert result.orphaned_junctions == []


def test_removing_a_two_way_edge_drops_its_connections() -> None:
    result = convert_to_one_way(_toy_net(), edge_id="-A")

    assert 'from="C" to="-A"' not in result.net_xml
    assert 'from="-A" to="-C"' not in result.net_xml
    # connections untouched by this removal survive
    assert 'from="A" to="B"' in result.net_xml


def test_removing_the_only_edge_to_a_dead_end_orphans_that_junction() -> None:
    result = convert_to_one_way(_toy_net(), edge_id="D")

    assert result.orphaned_junctions == ["j3"]


def test_missing_edge_raises() -> None:
    with pytest.raises(EdgeNotFoundError):
        convert_to_one_way(_toy_net(), edge_id="nonexistent")


def test_does_not_mutate_the_input() -> None:
    original = _toy_net()

    convert_to_one_way(original, edge_id="-A")

    assert original == _toy_net()
