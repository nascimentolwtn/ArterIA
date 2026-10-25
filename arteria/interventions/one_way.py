"""One-way conversion transform (roadmap P5.2, catalog entry "one_way_conversion").

SUMO represents a two-way street as two separate directional `<edge>`
elements between the same pair of junctions (e.g. `A` and `-A`), each with
its own lanes and `<connection>` elements. Converting a street to one-way
means removing one of those directional edges entirely, along with every
`<connection>` that references it (otherwise the connections dangle).

This module only edits the plain XML with the standard-library
`xml.etree.ElementTree` — no `sumolib` and no real `netconvert`/`sumo`
binary, per the remote-session boundary (ADR 0009). The real build and
visual check of a city's actual network stay at the desk (L9-L11); this
operates on hand-written toy fixtures (remote task R18).

After removing the edge, a minimal connectivity check reports which
junctions, if any, became unreachable from the rest of the network (for
example a dead-end side branch that was only reachable through the removed
edge), so a caller can tell a harmless conversion from one that strands
part of the network.
"""

from __future__ import annotations

from collections import deque
from copy import deepcopy
from dataclasses import dataclass
from xml.etree import ElementTree as ET


class EdgeNotFoundError(ValueError):
    """Raised when the requested edge does not exist in the network."""


@dataclass(frozen=True)
class OneWayResult:
    """Outcome of removing one directional edge from a network."""

    net_xml: str
    orphaned_junctions: list[str]


def convert_to_one_way(net_xml: str, *, edge_id: str) -> OneWayResult:
    """Remove the `<edge id=edge_id>` (and its connections) from `net_xml`.

    `net_xml` is not mutated: the result's `net_xml` is a new document.
    Every `<connection>` whose `from` or `to` equals `edge_id` is removed
    along with the edge, since it would otherwise reference a non-existent
    edge. `orphaned_junctions` lists (sorted) every junction that is no
    longer reachable from the rest of the network once the edge is gone,
    including a junction left with no touching edges at all.

    Raises `EdgeNotFoundError` if no edge with `edge_id` exists.
    """
    root = ET.fromstring(net_xml)
    if _find_edge(root, edge_id) is None:
        raise EdgeNotFoundError(f"no edge {edge_id!r} in network")

    new_root = deepcopy(root)
    removed = _find_edge(new_root, edge_id)
    assert removed is not None  # same lookup as above, just confirmed to exist
    new_root.remove(removed)

    for conn in new_root.findall("connection"):
        if conn.get("from") == edge_id or conn.get("to") == edge_id:
            new_root.remove(conn)

    return OneWayResult(
        net_xml=ET.tostring(new_root, encoding="unicode"),
        orphaned_junctions=_orphaned_junctions(new_root),
    )


def _find_edge(root: ET.Element, edge_id: str) -> ET.Element | None:
    for edge in root.findall("edge"):
        if edge.get("id") == edge_id:
            return edge
    return None


def _orphaned_junctions(root: ET.Element) -> list[str]:
    """Junctions in `root` not reachable from an arbitrary one via its edges."""
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

    start = next(iter(junction_ids))
    seen = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for neighbor in adjacency.get(current, ()):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)

    return sorted(junction_ids - seen)
