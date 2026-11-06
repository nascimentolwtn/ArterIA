from pathlib import Path

import pytest

from arteria.interventions.new_connector import (
    DuplicateEdgeError,
    JunctionNotFoundError,
    add_connector,
)

FIXTURES = Path(__file__).parent / "fixtures"
RING_FIXTURE = FIXTURES / "toy-net-apply-intervention.net.xml"
DISCONNECTED_FIXTURE = FIXTURES / "toy-net-disconnected-junction.net.xml"


def _ring_net() -> str:
    return RING_FIXTURE.read_text(encoding="utf-8")


def _disconnected_net() -> str:
    return DISCONNECTED_FIXTURE.read_text(encoding="utf-8")


def test_adding_a_chord_within_a_connected_ring_orphans_nothing_new() -> None:
    result = add_connector(_ring_net(), edge_id="edgeX", from_junction="j0", to_junction="j2")

    assert '<edge id="edgeX"' in result.net_xml
    assert result.connectable_from != []
    assert result.connectable_to != []
    assert result.newly_reachable_junctions == []


def test_connector_lanes_and_shape_use_junction_coordinates() -> None:
    result = add_connector(
        _ring_net(), edge_id="edgeX", from_junction="j0", to_junction="j2", num_lanes=2
    )

    assert 'id="edgeX_0"' in result.net_xml
    assert 'id="edgeX_1"' in result.net_xml
    assert 'shape="0,0 100,100"' in result.net_xml


def test_connectable_from_and_to_report_the_right_existing_edges() -> None:
    result = add_connector(_ring_net(), edge_id="edgeX", from_junction="j0", to_junction="j2")

    # edgeD feeds into j0 (the new edge's "from"); edgeC leaves j2 (the new edge's "to").
    assert result.connectable_from == ["edgeD"]
    assert result.connectable_to == ["edgeC"]


def test_connecting_a_disconnected_junction_makes_it_newly_reachable() -> None:
    result = add_connector(
        _disconnected_net(), edge_id="edgeE", from_junction="j2", to_junction="j4"
    )

    assert result.newly_reachable_junctions == ["j4"]


def test_missing_from_junction_raises() -> None:
    with pytest.raises(JunctionNotFoundError):
        add_connector(_ring_net(), edge_id="edgeX", from_junction="nonexistent", to_junction="j2")


def test_missing_to_junction_raises() -> None:
    with pytest.raises(JunctionNotFoundError):
        add_connector(_ring_net(), edge_id="edgeX", from_junction="j0", to_junction="nonexistent")


def test_duplicate_edge_id_raises() -> None:
    with pytest.raises(DuplicateEdgeError):
        add_connector(_ring_net(), edge_id="edgeA", from_junction="j0", to_junction="j2")


def test_does_not_mutate_the_input() -> None:
    original = _ring_net()

    add_connector(original, edge_id="edgeX", from_junction="j0", to_junction="j2")

    assert original == _ring_net()
