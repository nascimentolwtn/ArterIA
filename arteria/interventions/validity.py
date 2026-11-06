"""General-purpose validity checks after a network transform (roadmap P5.4).

`one_way.py` and `turn_restriction.py` each carry a narrow, ad hoc slice of
this idea, scoped to their own transform: orphaned-junction connectivity
after an edge removal, and single-edge reachability after a connection
removal. This module is the general, standalone version: whole-network
connectivity, plus route continuity for named emergency/transit/pedestrian
routes, assembled into one `ValidityReport` a caller can run after any
transform.

Deliberately standalone: it does not import from `one_way.py`,
`turn_restriction.py`, or `lane_restriction.py`, and nothing wires it into
`apply.py` yet (separate work). Like those modules, it only reads the plain
XML with the standard-library `xml.etree.ElementTree` -- no `sumolib` and
no real `netconvert`/`sumo` binary, per the remote-session boundary
(ADR 0009). The real build and visual check of a city's actual network
stay at the desk (L9-L11); this operates on hand-written toy fixtures.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Sequence
from xml.etree import ElementTree as ET

from pydantic import BaseModel


def find_disconnected_junctions(net_xml: str) -> list[str]:
    """Junctions in `net_xml` not reachable from an arbitrary one via its edges.

    An empty list means the whole network is one connected component. This
    is the same BFS-over-an-undirected-junction-graph idea as
    `one_way.py`'s `_orphaned_junctions`, written fresh here so this module
    stays standalone.
    """
    root = ET.fromstring(net_xml)
    junction_ids = {j.get("id", "") for j in root.findall("junction")}

    adjacency: dict[str, set[str]] = {j: set() for j in junction_ids}
    for edge in root.findall("edge"):
        from_j = edge.get("from", "")
        to_j = edge.get("to", "")
        if from_j in adjacency and to_j in adjacency:
            adjacency[from_j].add(to_j)
            adjacency[to_j].add(from_j)

    if not junction_ids:
        return []

    start = min(junction_ids)
    seen = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for neighbor in adjacency.get(current, ()):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)

    return sorted(junction_ids - seen)


class RouteContinuityResult(BaseModel):
    broken_at: list[tuple[str, str]]

    @property
    def is_continuous(self) -> bool:
        return not self.broken_at


def route_is_continuous(net_xml: str, edge_ids: Sequence[str]) -> RouteContinuityResult:
    """Whether every consecutive pair of `edge_ids` has a direct `<connection>`.

    `broken_at` lists every consecutive `(edge_ids[i], edge_ids[i+1])` pair
    for which no `<connection from=edge_ids[i] to=edge_ids[i+1]>` exists
    anywhere in the network. This checks the given route's edges stay
    directly joined in order, not whether some other, longer path between
    them still exists.

    Raises `ValueError` if `edge_ids` has fewer than two edges.
    """
    if len(edge_ids) < 2:
        raise ValueError("edge_ids must have at least two edges")

    root = ET.fromstring(net_xml)
    direct_connections = {(c.get("from", ""), c.get("to", "")) for c in root.findall("connection")}

    broken_at = [
        (edge_ids[i], edge_ids[i + 1])
        for i in range(len(edge_ids) - 1)
        if (edge_ids[i], edge_ids[i + 1]) not in direct_connections
    ]
    return RouteContinuityResult(broken_at=broken_at)


def check_emergency_route_continuity(
    net_xml: str, edge_ids: Sequence[str]
) -> RouteContinuityResult:
    """Whether a named emergency route's edges stay directly connected in order.

    Mechanically identical to `route_is_continuous`; the separate name lets
    a caller/report say "an emergency route broke" rather than just "a
    route broke" (roadmap P5.4).
    """
    return route_is_continuous(net_xml, edge_ids)


def check_transit_route_continuity(net_xml: str, edge_ids: Sequence[str]) -> RouteContinuityResult:
    """Whether a named transit route's edges stay directly connected in order.

    Mechanically identical to `route_is_continuous`; the separate name lets
    a caller/report say "a transit route broke" rather than just "a route
    broke" (roadmap P5.4).
    """
    return route_is_continuous(net_xml, edge_ids)


class PedestrianContinuityResult(BaseModel):
    blocked_edges: list[str]

    @property
    def is_continuous(self) -> bool:
        return not self.blocked_edges


def check_pedestrian_continuity(
    net_xml: str, edge_ids: Sequence[str]
) -> PedestrianContinuityResult:
    """Which of `edge_ids` has every lane closed to pedestrians.

    An edge is "blocked" only if *every* one of its `<lane>` children
    excludes pedestrians (via `disallow` or a non-pedestrian `allow`
    list) -- one unrestricted or pedestrian-allowing lane is enough to
    keep the edge passable on foot.

    Raises `ValueError` if any `edge_id` is not present in the network.
    """
    root = ET.fromstring(net_xml)
    edges_by_id = {e.get("id"): e for e in root.findall("edge")}

    blocked_edges = []
    for edge_id in edge_ids:
        edge = edges_by_id.get(edge_id)
        if edge is None:
            raise ValueError(f"no edge {edge_id!r} in network")

        lanes = edge.findall("lane")
        if lanes and all(_lane_blocks_pedestrians(lane) for lane in lanes):
            blocked_edges.append(edge_id)

    return PedestrianContinuityResult(blocked_edges=blocked_edges)


def _lane_blocks_pedestrians(lane: ET.Element) -> bool:
    disallow = lane.get("disallow")
    if disallow is not None and "pedestrian" in disallow.split():
        return True

    allow = lane.get("allow")
    if allow is not None and "pedestrian" not in allow.split():
        return True

    return False


class ValidityReport(BaseModel):
    disconnected_junctions: list[str]
    emergency_route_breaks: dict[str, RouteContinuityResult]
    transit_route_breaks: dict[str, RouteContinuityResult]
    pedestrian_breaks: dict[str, PedestrianContinuityResult]

    @property
    def is_valid(self) -> bool:
        return (
            not self.disconnected_junctions
            and all(result.is_continuous for result in self.emergency_route_breaks.values())
            and all(result.is_continuous for result in self.transit_route_breaks.values())
            and all(result.is_continuous for result in self.pedestrian_breaks.values())
        )


def check_validity(
    net_xml: str,
    *,
    emergency_routes: dict[str, Sequence[str]] | None = None,
    transit_routes: dict[str, Sequence[str]] | None = None,
    pedestrian_routes: dict[str, Sequence[str]] | None = None,
) -> ValidityReport:
    """Run every P5.4 validity check on `net_xml` and assemble one report.

    Whole-network connectivity (`find_disconnected_junctions`) always runs.
    Each of `emergency_routes`/`transit_routes`/`pedestrian_routes` maps a
    caller-chosen label (e.g. "hospital-access") to a sequence of edge ids,
    run through the matching single-route check; the labels become the
    keys of the corresponding dict on the returned `ValidityReport`.
    """
    if emergency_routes is None:
        emergency_routes = {}
    if transit_routes is None:
        transit_routes = {}
    if pedestrian_routes is None:
        pedestrian_routes = {}

    return ValidityReport(
        disconnected_junctions=find_disconnected_junctions(net_xml),
        emergency_route_breaks={
            label: check_emergency_route_continuity(net_xml, edge_ids)
            for label, edge_ids in emergency_routes.items()
        },
        transit_route_breaks={
            label: check_transit_route_continuity(net_xml, edge_ids)
            for label, edge_ids in transit_routes.items()
        },
        pedestrian_breaks={
            label: check_pedestrian_continuity(net_xml, edge_ids)
            for label, edge_ids in pedestrian_routes.items()
        },
    )
