"""New-connector-edge transform (roadmap P5.2, catalog entry "new_connector").

A new connector is the one catalog type that *adds* network capacity
instead of reallocating or restricting what is already there: a brand-new
`<edge>` (with its own lanes) directly joining two existing junctions that
were not directly joined before. The catalog only offers this from a
pre-approved list of junction pairs, so this module takes the pair as
given and does not itself judge whether a connector belongs there.

This module only edits the plain XML with the standard-library
`xml.etree.ElementTree` -- no `sumolib` and no real `netconvert`/`sumo`
binary, per the remote-session boundary (ADR 0009). The real build and
visual check of a city's actual network stay at the desk (L9-L11); this
operates on hand-written toy fixtures.

Deliberately out of scope: wiring the new edge into traffic. Deciding
which existing edges should actually connect into or out of it is a
network-design judgment call for whoever applies a real catalog entry, not
something this transform should guess at by adding `<connection>`
elements of its own. Instead, it only *reports* the existing edges that
are geometrically plausible connections (those touching the same two
junctions), leaving the decision -- and the connection-building -- to the
caller.
"""

from __future__ import annotations

import math
from collections import deque
from copy import deepcopy
from dataclasses import dataclass
from xml.etree import ElementTree as ET


class JunctionNotFoundError(ValueError):
    """Raised when a referenced junction does not exist in the network."""


class DuplicateEdgeError(ValueError):
    """Raised when the requested edge id already exists in the network."""


@dataclass(frozen=True)
class NewConnectorResult:
    """Outcome of adding one new connector edge between two junctions."""

    net_xml: str
    connectable_from: list[str]
    connectable_to: list[str]
    newly_reachable_junctions: list[str]


def add_connector(
    net_xml: str,
    *,
    edge_id: str,
    from_junction: str,
    to_junction: str,
    num_lanes: int = 1,
    speed_m_s: float = 13.89,
    length_m: float | None = None,
) -> NewConnectorResult:
    """Add a new `<edge id=edge_id>` from `from_junction` to `to_junction`.

    `net_xml` is not mutated: the result's `net_xml` is a new document.
    The new edge carries `num_lanes` lanes at `speed_m_s`, each with
    `length_m` (the straight-line distance between the two junctions'
    `x`/`y` when not given) and a two-point `shape` spanning them. No
    `<connection>` is created for the new edge; `connectable_from` and
    `connectable_to` instead report the ids of existing edges that already
    touch `from_junction` (as a `to`) or `to_junction` (as a `from`), i.e.
    what the new edge could plausibly be wired to. `newly_reachable_junctions`
    lists (sorted) every junction that was unreachable from the rest of the
    network before the edge was added and is reachable after.

    Raises `JunctionNotFoundError` if either junction does not exist, and
    `DuplicateEdgeError` if `edge_id` already names an existing edge.
    """
    root = ET.fromstring(net_xml)

    from_j = _find_junction(root, from_junction)
    if from_j is None:
        raise JunctionNotFoundError(f"no junction {from_junction!r} in network")
    to_j = _find_junction(root, to_junction)
    if to_j is None:
        raise JunctionNotFoundError(f"no junction {to_junction!r} in network")
    if _find_edge(root, edge_id) is not None:
        raise DuplicateEdgeError(f"edge {edge_id!r} already exists in network")

    before_reachable = _reachable_junctions(root)

    if length_m is None:
        length_m = _distance(from_j, to_j)
    shape = f"{from_j.get('x')},{from_j.get('y')} {to_j.get('x')},{to_j.get('y')}"

    new_edge = ET.Element(
        "edge",
        {
            "id": edge_id,
            "from": from_junction,
            "to": to_junction,
            "priority": "1",
            "numLanes": str(num_lanes),
            "speed": str(speed_m_s),
        },
    )
    for i in range(num_lanes):
        ET.SubElement(
            new_edge,
            "lane",
            {
                "id": f"{edge_id}_{i}",
                "index": str(i),
                "speed": str(speed_m_s),
                "length": f"{length_m:.2f}",
                "shape": shape,
            },
        )

    connectable_from = sorted(
        e.get("id", "") for e in root.findall("edge") if e.get("to") == from_junction
    )
    connectable_to = sorted(
        e.get("id", "") for e in root.findall("edge") if e.get("from") == to_junction
    )

    new_root = deepcopy(root)
    existing_edges = new_root.findall("edge")
    children = list(new_root)
    insert_at = children.index(existing_edges[-1]) + 1 if existing_edges else len(children)
    new_root.insert(insert_at, new_edge)

    after_reachable = _reachable_junctions(new_root)

    return NewConnectorResult(
        net_xml=ET.tostring(new_root, encoding="unicode"),
        connectable_from=connectable_from,
        connectable_to=connectable_to,
        newly_reachable_junctions=sorted(after_reachable - before_reachable),
    )


def _find_junction(root: ET.Element, junction_id: str) -> ET.Element | None:
    for junction in root.findall("junction"):
        if junction.get("id") == junction_id:
            return junction
    return None


def _find_edge(root: ET.Element, edge_id: str) -> ET.Element | None:
    for edge in root.findall("edge"):
        if edge.get("id") == edge_id:
            return edge
    return None


def _distance(from_junction: ET.Element, to_junction: ET.Element) -> float:
    from_x, from_y = float(from_junction.get("x", "0")), float(from_junction.get("y", "0"))
    to_x, to_y = float(to_junction.get("x", "0")), float(to_junction.get("y", "0"))
    return math.hypot(to_x - from_x, to_y - from_y)


def _reachable_junctions(root: ET.Element) -> set[str]:
    """Junctions in `root` reachable from an arbitrary one via its edges."""
    junction_ids = {j.get("id", "") for j in root.findall("junction")}

    adjacency: dict[str, set[str]] = {j: set() for j in junction_ids}
    for edge in root.findall("edge"):
        from_j = edge.get("from", "")
        to_j = edge.get("to", "")
        if from_j in adjacency and to_j in adjacency:
            adjacency[from_j].add(to_j)
            adjacency[to_j].add(from_j)

    if not junction_ids:
        return set()

    start = min(junction_ids)
    seen = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for neighbor in adjacency.get(current, ()):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)

    return seen
