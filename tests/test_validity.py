from pathlib import Path

import pytest

from arteria.interventions.validity import (
    PedestrianContinuityResult,
    RouteContinuityResult,
    check_emergency_route_continuity,
    check_pedestrian_continuity,
    check_transit_route_continuity,
    check_validity,
    find_disconnected_junctions,
    route_is_continuous,
)

RING_FIXTURE = Path(__file__).parent / "fixtures" / "toy-net-apply-intervention.net.xml"
VALIDITY_FIXTURE = Path(__file__).parent / "fixtures" / "toy-net-validity.net.xml"


def _ring_net() -> str:
    return RING_FIXTURE.read_text(encoding="utf-8")


def _validity_net() -> str:
    return VALIDITY_FIXTURE.read_text(encoding="utf-8")


def test_find_disconnected_junctions_empty_on_a_connected_ring() -> None:
    assert find_disconnected_junctions(_ring_net()) == []


def test_find_disconnected_junctions_reports_an_isolated_junction() -> None:
    assert find_disconnected_junctions(_validity_net()) == ["lonely"]


def test_route_is_continuous_on_consecutive_ring_edges() -> None:
    result = route_is_continuous(_ring_net(), ["edgeA", "edgeB", "edgeC"])

    assert result.is_continuous is True
    assert result.broken_at == []


def test_route_is_continuous_false_when_a_pair_has_no_direct_connection() -> None:
    result = route_is_continuous(_ring_net(), ["edgeA", "edgeC"])

    assert result.is_continuous is False
    assert result.broken_at == [("edgeA", "edgeC")]


def test_route_is_continuous_reports_only_the_broken_pair() -> None:
    result = route_is_continuous(_ring_net(), ["edgeA", "edgeB", "edgeD"])

    assert result.broken_at == [("edgeB", "edgeD")]


def test_route_is_continuous_raises_on_fewer_than_two_edges() -> None:
    with pytest.raises(ValueError):
        route_is_continuous(_ring_net(), ["edgeA"])


def test_check_emergency_route_continuity_delegates_to_route_is_continuous() -> None:
    result = check_emergency_route_continuity(_ring_net(), ["edgeA", "edgeB"])

    assert isinstance(result, RouteContinuityResult)
    assert result.is_continuous is True


def test_check_transit_route_continuity_delegates_to_route_is_continuous() -> None:
    result = check_transit_route_continuity(_ring_net(), ["edgeA", "edgeC"])

    assert isinstance(result, RouteContinuityResult)
    assert result.is_continuous is False


def test_check_pedestrian_continuity_finds_the_blocked_edge() -> None:
    result = check_pedestrian_continuity(_validity_net(), ["edgeX", "edgeP", "edgeQ"])

    assert isinstance(result, PedestrianContinuityResult)
    assert result.blocked_edges == ["edgeP"]
    assert result.is_continuous is False


def test_check_pedestrian_continuity_true_when_no_edge_is_fully_blocked() -> None:
    result = check_pedestrian_continuity(_validity_net(), ["edgeX", "edgeQ"])

    assert result.blocked_edges == []
    assert result.is_continuous is True


def test_check_pedestrian_continuity_raises_on_unknown_edge() -> None:
    with pytest.raises(ValueError):
        check_pedestrian_continuity(_validity_net(), ["does-not-exist"])


def test_check_validity_all_clean_on_a_connected_ring_with_no_routes() -> None:
    report = check_validity(_ring_net())

    assert report.disconnected_junctions == []
    assert report.emergency_route_breaks == {}
    assert report.transit_route_breaks == {}
    assert report.pedestrian_breaks == {}
    assert report.is_valid is True


def test_check_validity_aggregates_passing_and_failing_named_routes() -> None:
    report = check_validity(
        _ring_net(),
        emergency_routes={
            "hospital-access": ["edgeA", "edgeB"],
            "fire-station": ["edgeA", "edgeC"],
        },
        transit_routes={"bus-12": ["edgeB", "edgeC"]},
    )

    assert report.emergency_route_breaks["hospital-access"].is_continuous is True
    assert report.emergency_route_breaks["fire-station"].is_continuous is False
    assert report.transit_route_breaks["bus-12"].is_continuous is True
    assert report.is_valid is False


def test_check_validity_is_valid_false_when_a_pedestrian_route_is_blocked() -> None:
    report = check_validity(
        _validity_net(),
        pedestrian_routes={"school-walk": ["edgeX", "edgeP", "edgeQ"]},
    )

    assert report.disconnected_junctions == ["lonely"]
    assert report.pedestrian_breaks["school-walk"].is_continuous is False
    assert report.is_valid is False


def test_check_validity_is_valid_true_on_an_all_clean_network() -> None:
    report = check_validity(
        _ring_net(),
        emergency_routes={"hospital-access": ["edgeA", "edgeB", "edgeC"]},
        transit_routes={"bus-12": ["edgeC", "edgeD"]},
    )

    assert report.disconnected_junctions == []
    assert report.is_valid is True
