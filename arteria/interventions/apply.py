"""Catalog-entry dispatcher: apply one `CatalogEntry` to a network (roadmap P5.2/P5.3).

`arteria/interventions/catalog.py` describes *what* a candidate intervention
is; `one_way.py`, `turn_restriction.py`, `lane_restriction.py` and
`signal_retiming.py` each know *how* to make one specific kind of network
edit. Nothing yet turned a `CatalogEntry` into a call to the right one of
those — this module is that missing link: `apply_intervention()` reads
`entry.type` and pulls the edge/junction ids and transform parameters it
needs out of `entry.target_edges`/`entry.target_junctions`/
`entry.parameters`, exactly as a real catalog entry (see
`tests/fixtures/toy-catalog.yaml`) carries them.

Two catalog types have no transform yet (`reversible_lane`,
`transit_signal_priority`): each needs a network edit beyond plain-XML
attribute/element removal (time-dependent lane permissions, or detector/
TraCI wiring), so `apply_intervention()` raises
`UnsupportedInterventionTypeError` for them rather than guessing.

Every successful transform also runs P5.4's `validity.py` checks
(`check_validity()`) against the edited network and attaches the result
as `ApplyResult.validity`. A broken result (a disconnected junction, a
named route no longer continuous) is *annotated, not rejected*:
`apply_intervention()` never raises for it, because deciding whether a
given break is acceptable is a planner/optimizer judgment call (e.g. P7
may want to explore a package that cuts through traffic at the cost of
one minor street's connectivity), not something this dispatcher should
veto on its own. `emergency_routes`/`transit_routes`/`pedestrian_routes`
name which routes to check; this module has no per-city default for them
(there is no hardcoded SJC route list) -- a caller that cares about named
routes passes them in, typically read from a `cities/<city>/` config.
With no routes given, `validity` still reports whole-network
connectivity (`check_validity()`'s one check that never needs named
routes).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from arteria.interventions.catalog import CatalogEntry, InterventionType
from arteria.interventions.lane_restriction import restrict_lane
from arteria.interventions.new_connector import add_connector
from arteria.interventions.one_way import convert_to_one_way
from arteria.interventions.signal_retiming import retime_signal
from arteria.interventions.turn_restriction import remove_connection
from arteria.interventions.validity import ValidityReport, check_validity

_LANE_RESTRICTION_TYPES: frozenset[InterventionType] = frozenset(
    {"bus_lane", "protected_bike_corridor", "pedestrian_street", "lane_reallocation"}
)

_DEFAULT_ALLOW: dict[str, list[str]] = {
    "bus_lane": ["bus"],
    "protected_bike_corridor": ["bicycle"],
    "pedestrian_street": ["pedestrian"],
}

_UNSUPPORTED_TYPES: frozenset[InterventionType] = frozenset(
    {"reversible_lane", "transit_signal_priority"}
)


class UnsupportedInterventionTypeError(NotImplementedError):
    """Raised for a catalog entry type with no transform implemented yet."""


@dataclass(frozen=True)
class OneWayApplyResult:
    """Outcome of applying a `one_way_conversion` catalog entry."""

    net_xml: str
    orphaned_junctions: list[str]
    validity: ValidityReport


@dataclass(frozen=True)
class TurnRestrictionApplyResult:
    """Outcome of applying a `turn_restriction` catalog entry."""

    net_xml: str
    still_connected: bool
    validity: ValidityReport


@dataclass(frozen=True)
class LaneRestrictionApplyResult:
    """Outcome of applying a lane-`allow`-based catalog entry (one of `_LANE_RESTRICTION_TYPES`)."""

    net_xml: str
    restricted_edges: list[str]
    previous_allow: dict[str, str | None]
    previous_disallow: dict[str, str | None]
    validity: ValidityReport


@dataclass(frozen=True)
class SignalRetimingApplyResult:
    """Outcome of applying a `signal_retiming` catalog entry."""

    net_xml: str
    previous_durations: list[float]
    previous_cycle_length_s: float
    new_cycle_length_s: float
    validity: ValidityReport


@dataclass(frozen=True)
class NewConnectorApplyResult:
    """Outcome of applying a `new_connector` catalog entry."""

    net_xml: str
    connectable_from: list[str]
    connectable_to: list[str]
    newly_reachable_junctions: list[str]
    validity: ValidityReport


ApplyResult = (
    OneWayApplyResult
    | TurnRestrictionApplyResult
    | LaneRestrictionApplyResult
    | SignalRetimingApplyResult
    | NewConnectorApplyResult
)


def apply_intervention(
    net_xml: str,
    entry: CatalogEntry,
    *,
    emergency_routes: dict[str, Sequence[str]] | None = None,
    transit_routes: dict[str, Sequence[str]] | None = None,
    pedestrian_routes: dict[str, Sequence[str]] | None = None,
) -> ApplyResult:
    """Apply `entry`'s transform to `net_xml`, dispatching on `entry.type`.

    `net_xml` is not mutated. Raises `ValueError` if `entry` is missing a
    `target_edges`/`target_junctions`/`parameters` value its type needs, and
    `UnsupportedInterventionTypeError` for a type with no transform yet.

    `emergency_routes`/`transit_routes`/`pedestrian_routes` are forwarded to
    `validity.check_validity()` against the transformed network and attached
    as the result's `validity` field; see the module docstring for why a
    broken result is annotated rather than rejected.
    """

    def _validity(transformed_net_xml: str) -> ValidityReport:
        return check_validity(
            transformed_net_xml,
            emergency_routes=emergency_routes,
            transit_routes=transit_routes,
            pedestrian_routes=pedestrian_routes,
        )

    if entry.type == "one_way_conversion":
        edge_id = _require_single_edge(entry)
        one_way_result = convert_to_one_way(net_xml, edge_id=edge_id)
        return OneWayApplyResult(
            net_xml=one_way_result.net_xml,
            orphaned_junctions=one_way_result.orphaned_junctions,
            validity=_validity(one_way_result.net_xml),
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
            net_xml=turn_result.net_xml,
            still_connected=turn_result.still_connected,
            validity=_validity(turn_result.net_xml),
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
            validity=_validity(current),
        )

    if entry.type == "signal_retiming":
        tls_id = _require_single_junction(entry)
        phase_durations = entry.parameters.get("phase_durations")
        if not phase_durations:
            raise ValueError(
                f"entry {entry.id!r}: signal_retiming needs parameters.phase_durations"
            )
        signal_result = retime_signal(
            net_xml, tls_id=tls_id, phase_durations=[float(d) for d in phase_durations]
        )
        return SignalRetimingApplyResult(
            net_xml=signal_result.net_xml,
            previous_durations=signal_result.previous_durations,
            previous_cycle_length_s=signal_result.previous_cycle_length_s,
            new_cycle_length_s=signal_result.new_cycle_length_s,
            validity=_validity(signal_result.net_xml),
        )

    if entry.type == "new_connector":
        from_junction, to_junction = _require_two_junctions(entry)
        edge_id = entry.parameters.get("edge_id")
        if not edge_id:
            raise ValueError(f"entry {entry.id!r}: new_connector needs parameters.edge_id")
        length_m = entry.parameters.get("length_m")
        connector_result = add_connector(
            net_xml,
            edge_id=str(edge_id),
            from_junction=from_junction,
            to_junction=to_junction,
            num_lanes=int(entry.parameters.get("num_lanes", 1)),
            speed_m_s=float(entry.parameters.get("speed_m_s", 13.89)),
            length_m=None if length_m is None else float(length_m),
        )
        return NewConnectorApplyResult(
            net_xml=connector_result.net_xml,
            connectable_from=connector_result.connectable_from,
            connectable_to=connector_result.connectable_to,
            newly_reachable_junctions=connector_result.newly_reachable_junctions,
            validity=_validity(connector_result.net_xml),
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


def _require_single_junction(entry: CatalogEntry) -> str:
    if len(entry.target_junctions) != 1:
        raise ValueError(
            f"entry {entry.id!r}: {entry.type!r} needs exactly one target_junctions entry, "
            f"got {len(entry.target_junctions)}"
        )
    return entry.target_junctions[0]


def _require_two_junctions(entry: CatalogEntry) -> tuple[str, str]:
    if len(entry.target_junctions) != 2:
        raise ValueError(
            f"entry {entry.id!r}: {entry.type!r} needs exactly two target_junctions entries "
            f"(from, to), got {len(entry.target_junctions)}"
        )
    return entry.target_junctions[0], entry.target_junctions[1]


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
