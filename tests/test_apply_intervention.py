from pathlib import Path

import pytest

from arteria.interventions.apply import (
    LaneRestrictionApplyResult,
    OneWayApplyResult,
    TurnRestrictionApplyResult,
    UnsupportedInterventionTypeError,
    apply_intervention,
)
from arteria.interventions.catalog import CatalogEntry, load_catalog

FIXTURES = Path(__file__).parent / "fixtures"
NET_FIXTURE = FIXTURES / "toy-net-apply-intervention.net.xml"
CATALOG_FIXTURE = FIXTURES / "toy-catalog.yaml"


def _toy_net() -> str:
    return NET_FIXTURE.read_text(encoding="utf-8")


def _catalog_entry(entry_id: str) -> CatalogEntry:
    catalog = load_catalog(CATALOG_FIXTURE)
    return next(e for e in catalog.entries if e.id == entry_id)


def test_one_way_conversion_entry_dispatches_to_convert_to_one_way() -> None:
    entry = _catalog_entry("busline-x-one-way")

    result = apply_intervention(_toy_net(), entry)

    assert isinstance(result, OneWayApplyResult)
    assert '<edge id="edgeA"' not in result.net_xml
    assert result.orphaned_junctions == []


def test_turn_restriction_entry_dispatches_to_remove_connection() -> None:
    entry = _catalog_entry("junction-y-turn-restriction")

    result = apply_intervention(_toy_net(), entry)

    assert isinstance(result, TurnRestrictionApplyResult)
    assert 'from="edgeC" to="edgeD"' not in result.net_xml
    assert result.still_connected is False


def test_bus_lane_entry_restricts_every_target_edge() -> None:
    entry = _catalog_entry("busline-x-bus-lane")

    result = apply_intervention(_toy_net(), entry)

    assert isinstance(result, LaneRestrictionApplyResult)
    assert result.restricted_edges == ["edgeA", "edgeB"]
    assert result.previous_allow == {"edgeA": None, "edgeB": None}
    assert result.previous_disallow == {"edgeA": None, "edgeB": None}
    for line in result.net_xml.splitlines():
        if 'id="edgeA_1"' in line or 'id="edgeB_1"' in line:
            assert 'allow="bus"' in line
        if 'id="edgeA_0"' in line or 'id="edgeB_0"' in line:
            assert "allow" not in line


def test_does_not_mutate_the_input() -> None:
    original = _toy_net()

    apply_intervention(original, _catalog_entry("busline-x-bus-lane"))

    assert original == _toy_net()


@pytest.mark.parametrize(
    "unsupported_type",
    ["reversible_lane", "new_connector", "signal_retiming", "transit_signal_priority"],
)
def test_unsupported_type_raises(unsupported_type: str) -> None:
    entry = CatalogEntry.model_validate(
        {
            "id": "not-yet-implemented",
            "type": unsupported_type,
            "description": "desc",
            "complexity": "low",
        }
    )

    with pytest.raises(UnsupportedInterventionTypeError):
        apply_intervention(_toy_net(), entry)


def test_one_way_conversion_requires_exactly_one_target_edge() -> None:
    entry = CatalogEntry.model_validate(
        {
            "id": "bad-one-way",
            "type": "one_way_conversion",
            "description": "desc",
            "complexity": "low",
            "target_edges": ["edgeA", "edgeB"],
        }
    )

    with pytest.raises(ValueError, match="exactly one"):
        apply_intervention(_toy_net(), entry)


def test_turn_restriction_requires_from_and_to_edge_parameters() -> None:
    entry = CatalogEntry.model_validate(
        {
            "id": "bad-turn-restriction",
            "type": "turn_restriction",
            "description": "desc",
            "complexity": "low",
        }
    )

    with pytest.raises(ValueError, match="from_edge"):
        apply_intervention(_toy_net(), entry)


def test_lane_restriction_requires_lane_index_parameter() -> None:
    entry = CatalogEntry.model_validate(
        {
            "id": "bad-bus-lane",
            "type": "bus_lane",
            "description": "desc",
            "complexity": "low",
            "target_edges": ["edgeA"],
        }
    )

    with pytest.raises(ValueError, match="lane_index"):
        apply_intervention(_toy_net(), entry)


def test_lane_reallocation_requires_explicit_allow_parameter() -> None:
    entry = CatalogEntry.model_validate(
        {
            "id": "bad-lane-reallocation",
            "type": "lane_reallocation",
            "description": "desc",
            "complexity": "low",
            "target_edges": ["edgeA"],
            "parameters": {"lane_index": 1},
        }
    )

    with pytest.raises(ValueError, match="allow"):
        apply_intervention(_toy_net(), entry)
