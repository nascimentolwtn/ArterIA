"""Lane vehicle-class restriction transform (roadmap P5.2, remote task R18).

Several catalog entry *types* all reduce, mechanically, to the same SUMO
network edit: set a lane's `allow` attribute to a vehicle-class allow-list
(and drop any `disallow` attribute, since a lane must not carry both).
This module implements that one generic transform; the catalog entry type
is just a choice of `allow` values, e.g.:

    allow=["bus"]                    -> bus lane
    allow=["bicycle"]                -> protected bike corridor
    allow=["pedestrian"]             -> pedestrian lane / street
    allow=["bicycle", "pedestrian"]  -> shared ped/bike lane (car->bike
                                         lane reallocation case)

Like `turn_restriction.py`, this module only edits the plain XML with the
standard-library `xml.etree.ElementTree` -- no `sumolib` and no real
`netconvert`/`sumo` binary, per the remote-session boundary (ADR 0009).
The real build and visual check of a city's actual network stay at the
desk (L9-L11); this operates on hand-written toy fixtures.
"""

from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass
from xml.etree import ElementTree as ET


class LaneNotFoundError(ValueError):
    """Raised when the requested edge or lane index does not exist in the network."""


@dataclass(frozen=True)
class LaneRestrictionResult:
    """Outcome of restricting one lane's allowed vehicle classes."""

    net_xml: str
    previous_allow: str | None
    previous_disallow: str | None


def restrict_lane(
    net_xml: str,
    *,
    edge_id: str,
    lane_index: int,
    allow: Sequence[str],
) -> LaneRestrictionResult:
    """Set the `allow` vClass list on one lane of `net_xml`.

    `net_xml` is not mutated: the result's `net_xml` is a new document.
    The lane is identified by its parent `<edge id=edge_id>` and its own
    `index` attribute equal to `str(lane_index)`. On success, the lane's
    `allow` attribute is set to the space-separated `allow` list and any
    existing `disallow` attribute is removed (a lane must not carry both).

    Raises `LaneNotFoundError` if the edge or that lane index does not
    exist, and `ValueError` if `allow` is empty.
    """
    if not allow:
        raise ValueError("allow must not be empty")

    root = ET.fromstring(net_xml)
    lane = _find_lane(root, edge_id, lane_index)
    if lane is None:
        raise LaneNotFoundError(f"no lane with index {lane_index} on edge {edge_id!r}")

    new_root = deepcopy(root)
    new_lane = _find_lane(new_root, edge_id, lane_index)
    assert new_lane is not None  # same lookup as above, just confirmed to exist

    previous_allow = new_lane.get("allow")
    previous_disallow = new_lane.get("disallow")

    new_lane.set("allow", " ".join(allow))
    if "disallow" in new_lane.attrib:
        del new_lane.attrib["disallow"]

    return LaneRestrictionResult(
        net_xml=ET.tostring(new_root, encoding="unicode"),
        previous_allow=previous_allow,
        previous_disallow=previous_disallow,
    )


def _find_lane(root: ET.Element, edge_id: str, lane_index: int) -> ET.Element | None:
    for edge in root.findall("edge"):
        if edge.get("id") != edge_id:
            continue
        for lane in edge.findall("lane"):
            if lane.get("index") == str(lane_index):
                return lane
        return None
    return None
