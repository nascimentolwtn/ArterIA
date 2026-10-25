"""Turn-restriction transform: connection removal (roadmap P5.2).

A turn restriction is applied as a deterministic network transform: remove
one `<connection>` element from a SUMO `.net.xml` document, identified by
its `from`/`to` edge ids (and optionally `fromLane`/`toLane`). This module
only edits the plain XML with the standard-library `xml.etree.ElementTree`
— no `sumolib` and no real `netconvert`/`sumo` binary, per the remote-
session boundary (ADR 0009). The real build and visual check of a city's
actual network stay at the desk (L9-L11); this operates on hand-written
toy fixtures.

After removing the connection, a minimal connectivity check (a scaled-down
version of the full validity checks in P5.4, which cover more than turn
restrictions) reports whether the target edge is still reachable from the
source edge through some other remaining connection, so a caller can tell
a harmless restriction from one that strands part of the network.
"""

from __future__ import annotations

from collections import deque
from copy import deepcopy
from dataclasses import dataclass
from xml.etree import ElementTree as ET


class ConnectionNotFoundError(ValueError):
    """Raised when the requested connection does not exist in the network."""


@dataclass(frozen=True)
class TurnRestrictionResult:
    """Outcome of removing one connection from a network."""

    net_xml: str
    still_connected: bool


def remove_connection(
    net_xml: str,
    *,
    from_edge: str,
    to_edge: str,
    from_lane: str | None = None,
    to_lane: str | None = None,
) -> TurnRestrictionResult:
    """Remove the `<connection>` from `from_edge` to `to_edge` from `net_xml`.

    `net_xml` is not mutated: the result's `net_xml` is a new document.
    When `from_lane`/`to_lane` are given, only a connection matching those
    lane indices too is removed; otherwise the first connection matching
    just the edge ids is removed.

    Raises `ConnectionNotFoundError` if no connection matches.
    """
    root = ET.fromstring(net_xml)
    if _find_connection(root, from_edge, to_edge, from_lane, to_lane) is None:
        lane_detail = (
            f" (fromLane={from_lane!r}, toLane={to_lane!r})" if from_lane or to_lane else ""
        )
        raise ConnectionNotFoundError(
            f"no connection from edge {from_edge!r} to edge {to_edge!r}{lane_detail}"
        )

    new_root = deepcopy(root)
    removed = _find_connection(new_root, from_edge, to_edge, from_lane, to_lane)
    assert removed is not None  # same lookup as above, just confirmed to exist
    new_root.remove(removed)

    return TurnRestrictionResult(
        net_xml=ET.tostring(new_root, encoding="unicode"),
        still_connected=_edge_reachable(new_root, from_edge, to_edge),
    )


def _find_connection(
    root: ET.Element,
    from_edge: str,
    to_edge: str,
    from_lane: str | None,
    to_lane: str | None,
) -> ET.Element | None:
    for conn in root.findall("connection"):
        if conn.get("from") != from_edge or conn.get("to") != to_edge:
            continue
        if from_lane is not None and conn.get("fromLane") != from_lane:
            continue
        if to_lane is not None and conn.get("toLane") != to_lane:
            continue
        return conn
    return None


def _edge_reachable(root: ET.Element, from_edge: str, to_edge: str) -> bool:
    """Whether `to_edge` is reachable from `from_edge` via the remaining connections."""
    graph: dict[str, list[str]] = {}
    for conn in root.findall("connection"):
        graph.setdefault(conn.get("from", ""), []).append(conn.get("to", ""))

    visited = {from_edge}
    queue = deque([from_edge])
    while queue:
        edge = queue.popleft()
        for neighbor in graph.get(edge, []):
            if neighbor == to_edge:
                return True
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return False
