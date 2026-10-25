from pathlib import Path

import pytest

from arteria.interventions.turn_restriction import (
    ConnectionNotFoundError,
    remove_connection,
)

FIXTURE = Path(__file__).parent / "fixtures" / "toy-net.net.xml"


def _toy_net() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def test_remove_connection_drops_it_from_the_output() -> None:
    result = remove_connection(_toy_net(), from_edge="N", to_edge="M")

    assert 'from="N" to="M"' not in result.net_xml
    # the bypass connections are untouched
    assert 'from="N" to="S"' in result.net_xml
    assert 'from="S" to="M"' in result.net_xml


def test_does_not_mutate_the_input() -> None:
    original = _toy_net()

    remove_connection(original, from_edge="N", to_edge="M")

    assert 'from="N" to="M"' in original


def test_still_connected_when_a_bypass_remains() -> None:
    result = remove_connection(_toy_net(), from_edge="N", to_edge="M")

    assert result.still_connected is True


def test_not_connected_when_no_alternate_route_exists() -> None:
    result = remove_connection(_toy_net(), from_edge="P", to_edge="Q")

    assert result.still_connected is False


def test_missing_connection_raises() -> None:
    with pytest.raises(ConnectionNotFoundError):
        remove_connection(_toy_net(), from_edge="M", to_edge="N")


def test_lane_specific_removal_matches_only_the_given_lanes() -> None:
    result = remove_connection(
        _toy_net(), from_edge="N", to_edge="M", from_lane="0", to_lane="0"
    )

    assert 'from="N" to="M"' not in result.net_xml


def test_lane_specific_removal_raises_when_lanes_do_not_match() -> None:
    with pytest.raises(ConnectionNotFoundError):
        remove_connection(
            _toy_net(), from_edge="N", to_edge="M", from_lane="1", to_lane="0"
        )
