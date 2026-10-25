"""Catalog-entry dispatcher: apply one `CatalogEntry` to a network (roadmap P5.2/P5.3).

`arteria/interventions/catalog.py` describes *what* a candidate intervention
is; `one_way.py`, `turn_restriction.py` and `lane_restriction.py` each know
*how* to make one specific kind of network edit. Nothing yet turned a
`CatalogEntry` into a call to the right one of those — this module is that
missing link: `apply_intervention()` reads `entry.type` and pulls the edge/
junction ids and transform parameters it needs out of `entry.target_edges`/
`entry.target_junctions`/`entry.parameters`, exactly as a real catalog entry
(see `tests/fixtures/toy-catalog.yaml`) carries them.

Four catalog types have no transform yet (`reversible_lane`, `new_connector`,
`signal_retiming`, `transit_signal_priority`): each needs a network edit
beyond plain-XML attribute/element removal (time-dependent lane permissions,
a brand-new edge, or a TLS program), so `apply_intervention()` raises
`UnsupportedInterventionTypeError` for them rather than guessing.
"""

from __future__ import annotations

from dataclasses import dataclass

from arteria.interventions.catalog import CatalogEntry, InterventionType
from arteria.interventions.lane_restriction import restrict_lane
from arteria.interventions.one_way import convert_to_one_way
from arteria.interventions.turn_restriction import remove_connection

_LANE_RESTRICTION_TYPES: frozenset[InterventionType] = frozenset(
    {"bus_lane", "protected_bike_corridor", "pedestrian_street", "lane_reallocation"}
)

_DEFAULT_ALLOW: dict[str, list[str]] = {
    "bus_lane": ["bus"],
    "protected_bike_corridor": ["bicycle"],
    "pedestrian_street": ["pedestrian"],
}

_UNSUPPORTED_TYPES: frozenset[InterventionType] = frozenset(
    {"reversible_lane", "new_connector", "signal_retiming", "transit_signal_priority"}
)


class UnsupportedInterventionTypeError(NotImplementedError):
    """Raised for a catalog entry type with no transform implemented yet."""


@dataclass(frozen=True)
class OneWayApplyResult:
    """Outcome of applying a `one_way_conversion` catalog entry."""

    net_xml: str
    orphaned_junctions: list[str]


@dataclass(frozen=True)
class TurnRestrictionApplyResult:
    """Outcome of applying a `turn_restriction` catalog entry."""

    net_xml: str
    still_connected: bool


@dataclass(frozen=True)
class LaneRestrictionApplyResult:
    """Outcome of applying a lane-`allow`-based catalog entry (one of `_LANE_RESTRICTION_TYPES`)."""

    net_xml: str
    restricted_edges: list[str]
    previous_allow: dict[str, str | None]
    previous_disallow: dict[str, str | None]


ApplyResult = OneWayApplyResult | TurnRestrictionApplyResult | LaneRestrictionApplyResult


def apply_intervention(net_xml: str, entry: CatalogEntry) -> ApplyResult:
    """Apply `entry`'s transform to `net_xml`, dispatching on `entry.type`.

    `net_xml` is not mutated. Raises `ValueError` if `entry` is missing a
    `target_edges`/`target_junctions`/`parameters` value its type needs, and
    `UnsupportedInterventionTypeError` for a type with no transform yet.
    """
    if entry.type == "one_way_conversion":
        edge_id = _require_single_edge(entry)
        one_way_result = convert_to_one_way(net_xml, edge_id=edge_id)
        return OneWayApplyResult(
            net_xml=one_way_result.net_xml,
            orphaned_junctions=one_way_result.orphaned_junctions,
        )

    if entry.type == "turn_restriction":
        from_edge, to_edge = _require_turn_edges(entry)
        turn_result = remove_connection(
            net_xml,
            from_edge=from_edge,
            to_edge=to_edge,
            from_lane=_optional_str(entry.parameters.get("from_lane")),
            to_lane=_optional_str(entry.parameters.get("to_lane")),
        )
        return TurnRestrictionApplyResult(
            net_xml=turn_result.net_xml, still_connected=turn_result.still_connected
        )

    if entry.type in _LANE_RESTRICTION_TYPES:
        edges = _require_edges(entry)
        allow = entry.parameters.get("allow") or _DEFAULT_ALLOW.get(entry.type)
        if not allow:
            raise ValueError(
                f"entry {entry.id!r}: {entry.type!r} needs parameters.allow "
                "(no default vClass list for this type)"
            )
        lane_index = entry.parameters.get("lane_index")
        if lane_index is None:
            raise ValueError(f"entry {entry.id!r}: {entry.type!r} needs parameters.lane_index")

        current = net_xml
        previous_allow: dict[str, str | None] = {}
        previous_disallow: dict[str, str | None] = {}
        for edge_id in edges:
            lane_result = restrict_lane(
                current, edge_id=edge_id, lane_index=int(lane_index), allow=allow
            )
            current = lane_result.net_xml
            previous_allow[edge_id] = lane_result.previous_allow
            previous_disallow[edge_id] = lane_result.previous_disallow

        return LaneRestrictionApplyResult(
            net_xml=current,
            restricted_edges=edges,
            previous_allow=previous_allow,
            previous_disallow=previous_disallow,
        )

    if entry.type in _UNSUPPORTED_TYPES:
        raise UnsupportedInterventionTypeError(
            f"entry {entry.id!r}: no transform implemented yet for type {entry.type!r} "
            "(needs a network edit beyond plain-XML attribute/element removal -- "
            "a new edge, time-dependent lane permissions, or a TLS program)"
        )

    raise AssertionError(f"unhandled intervention type {entry.type!r}")  # pragma: no cover


def _require_single_edge(entry: CatalogEntry) -> str:
    if len(entry.target_edges) != 1:
        raise ValueError(
            f"entry {entry.id!r}: {entry.type!r} needs exactly one target_edges entry, "
            f"got {len(entry.target_edges)}"
        )
    return entry.target_edges[0]


def _require_edges(entry: CatalogEntry) -> list[str]:
    if not entry.target_edges:
        raise ValueError(
            f"entry {entry.id!r}: {entry.type!r} needs at least one target_edges entry"
        )
    return entry.target_edges


def _require_turn_edges(entry: CatalogEntry) -> tuple[str, str]:
    try:
        from_edge = entry.parameters["from_edge"]
        to_edge = entry.parameters["to_edge"]
    except KeyError as exc:
        raise ValueError(
            f"entry {entry.id!r}: turn_restriction needs parameters.from_edge and "
            "parameters.to_edge"
        ) from exc
    return str(from_edge), str(to_edge)


def _optional_str(value: object) -> str | None:
    return None if value is None else str(value)
