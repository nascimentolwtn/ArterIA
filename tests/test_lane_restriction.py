from pathlib import Path

import pytest

from arteria.interventions.lane_restriction import (
    LaneNotFoundError,
    restrict_lane,
)

FIXTURE = Path(__file__).parent / "fixtures" / "toy-net-lane-restriction.net.xml"


def _toy_net() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def test_restrict_unrestricted_lane_to_bus() -> None:
    result = restrict_lane(_toy_net(), edge_id="W", lane_index=0, allow=["bus"])

    assert 'id="W_0"' in result.net_xml
    assert 'allow="bus"' in result.net_xml
    assert result.previous_allow is None
    assert result.previous_disallow is None

    # the lane that got the new `allow` must not also carry `disallow`.
    for line in result.net_xml.splitlines():
        if 'id="W_0"' in line:
            assert "disallow" not in line


def test_restrict_lane_that_had_disallow_replaces_it() -> None:
    result = restrict_lane(_toy_net(), edge_id="W", lane_index=1, allow=["bicycle"])

    assert result.previous_allow is None
    assert result.previous_disallow == "bicycle pedestrian"

    for line in result.net_xml.splitlines():
        if 'id="W_1"' in line:
            assert "disallow" not in line
            assert 'allow="bicycle"' in line


def test_shared_ped_bike_allow_list() -> None:
    result = restrict_lane(
        _toy_net(), edge_id="W", lane_index=1, allow=["bicycle", "pedestrian"]
    )

    assert 'allow="bicycle pedestrian"' in result.net_xml
    assert result.previous_disallow == "bicycle pedestrian"


def test_does_not_mutate_the_input() -> None:
    original = _toy_net()

    restrict_lane(original, edge_id="W", lane_index=0, allow=["bus"])

    # the input string object itself is untouched: still byte-identical
    # to a fresh read of the fixture, and still carries the original
    # (unrestricted) W_0 lane plus the untouched disallow on W_1.
    assert original == _toy_net()
    assert 'id="W_0" index="0" speed="13.89" length="100.00" shape="0,0 100,0"' in original
    assert 'disallow="bicycle pedestrian"' in original


def test_missing_edge_raises() -> None:
    with pytest.raises(LaneNotFoundError):
        restrict_lane(_toy_net(), edge_id="DOES_NOT_EXIST", lane_index=0, allow=["bus"])


def test_out_of_range_lane_index_raises() -> None:
    with pytest.raises(LaneNotFoundError):
        restrict_lane(_toy_net(), edge_id="W", lane_index=5, allow=["bus"])


def test_empty_allow_raises() -> None:
    with pytest.raises(ValueError):
        restrict_lane(_toy_net(), edge_id="W", lane_index=0, allow=[])
