from pathlib import Path

import pytest

from arteria.interventions.catalog import InterventionCatalog, load_catalog

FIXTURES = Path(__file__).parent / "fixtures"


def test_toy_catalog_loads_and_round_trips_fields() -> None:
    catalog = load_catalog(FIXTURES / "toy-catalog.yaml")
    assert len(catalog.entries) == 3

    by_id = {entry.id for entry in catalog.entries}
    assert by_id == {
        "busline-x-bus-lane",
        "busline-x-one-way",
        "junction-y-turn-restriction",
    }

    types = {entry.type for entry in catalog.entries}
    assert types == {"bus_lane", "one_way_conversion", "turn_restriction"}

    bus_lane = next(e for e in catalog.entries if e.id == "busline-x-bus-lane")
    assert bus_lane.target_edges == ["edgeA", "edgeB"]
    assert bus_lane.parameters == {"lane_index": 1, "allow": ["bus"]}
    assert bus_lane.cost_estimate_brl == 120000.0
    assert bus_lane.complexity == "medium"
    assert bus_lane.mutual_exclusions == ["busline-x-one-way"]
    assert bus_lane.expected_beneficiaries == ["bus riders", "transit agency"]

    turn_restriction = next(e for e in catalog.entries if e.id == "junction-y-turn-restriction")
    assert turn_restriction.target_junctions == ["junctionY"]
    assert turn_restriction.mutual_exclusions == []
    assert turn_restriction.equity_notes is None


def test_mutual_exclusion_referencing_unknown_id_raises() -> None:
    with pytest.raises(ValueError, match="unknown id"):
        InterventionCatalog.model_validate(
            {
                "entries": [
                    {
                        "id": "a",
                        "type": "turn_restriction",
                        "description": "desc",
                        "complexity": "low",
                        "mutual_exclusions": ["does-not-exist"],
                    }
                ]
            }
        )


def test_mutual_exclusion_self_reference_raises() -> None:
    with pytest.raises(ValueError, match="lists itself"):
        InterventionCatalog.model_validate(
            {
                "entries": [
                    {
                        "id": "a",
                        "type": "turn_restriction",
                        "description": "desc",
                        "complexity": "low",
                        "mutual_exclusions": ["a"],
                    }
                ]
            }
        )


def test_minimal_single_entry_catalog_loads() -> None:
    catalog = InterventionCatalog.model_validate(
        {
            "entries": [
                {
                    "id": "only-entry",
                    "type": "pedestrian_street",
                    "description": "Convert one block to a pedestrian-only street.",
                    "complexity": "high",
                }
            ]
        }
    )
    assert len(catalog.entries) == 1
    entry = catalog.entries[0]
    assert entry.id == "only-entry"
    assert entry.mutual_exclusions == []
    assert entry.target_edges == []
    assert entry.cost_estimate_brl is None
