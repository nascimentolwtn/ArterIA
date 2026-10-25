"""SUMO induction-loop ("E1") detector mapping for calibration (roadmap P4.2).

Calibration compares modeled link volumes against observed counts, and SUMO
needs a `<detector>`/`<inductionLoop>` definition per count location to
produce those modeled volumes. This maps a list of count locations (edge +
position along it) onto a `.net.xml`-shaped network and emits the
`<additional>` XML SUMO expects, flagging anything that can't be mapped
cleanly (unknown edge, out-of-range position) rather than silently guessing.

Remote sessions never run a real network build or simulation (ADR 0009: no
`sumo`/`netconvert` binary, no `sumolib`), so this parses the plain-XML net
format directly with the stdlib, as `arteria.network.validate` does, and is
exercised only against hand-written toy fixtures.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Sequence

from pydantic import BaseModel

DETECTOR_FREQ_S = "3600"
DETECTOR_OUTPUT_FILE = "detectors.out.xml"
_LANE_POS_MARGIN_M = 0.1


class CountLocation(BaseModel):
    count_id: str
    edge_id: str
    position_m: float


class DetectorBuildResult(BaseModel):
    additional_xml: str
    unmatched: list[str] = []
    clamped: list[str] = []


def build_induction_loops(
    net_xml: str, locations: Sequence[CountLocation]
) -> DetectorBuildResult:
    """Place one `<inductionLoop>` per lane of each matched location's edge.

    A location whose `edge_id` isn't in the network is skipped (no detector
    emitted) and its `count_id` is added to `unmatched`. A location whose
    `position_m` doesn't fit a lane's length (negative, or `>=` the lane's
    length) has its `pos` clamped into `[0.0, lane_length - 0.1]` — SUMO
    requires `pos` strictly less than the lane's length — and its `count_id`
    is added to `clamped` once, even if several lanes needed clamping.
    """
    root = ET.fromstring(net_xml)
    edges_by_id = {e.get("id", ""): e for e in root.findall("edge")}

    unmatched: list[str] = []
    clamped: list[str] = []
    additional = ET.Element("additional")

    for location in locations:
        edge = edges_by_id.get(location.edge_id)
        if edge is None:
            unmatched.append(location.count_id)
            continue

        was_clamped = False
        for lane in edge.findall("lane"):
            lane_id = lane.get("id", "")
            lane_length = float(lane.get("length", "0"))

            if 0 <= location.position_m < lane_length:
                pos = location.position_m
            else:
                pos = max(0.0, min(location.position_m, lane_length - _LANE_POS_MARGIN_M))
                was_clamped = True

            ET.SubElement(
                additional,
                "inductionLoop",
                {
                    "id": f"{location.count_id}_{lane_id}",
                    "lane": lane_id,
                    "pos": str(pos),
                    "freq": DETECTOR_FREQ_S,
                    "file": DETECTOR_OUTPUT_FILE,
                },
            )

        if was_clamped:
            clamped.append(location.count_id)

    return DetectorBuildResult(
        additional_xml=ET.tostring(additional, encoding="unicode"),
        unmatched=unmatched,
        clamped=clamped,
    )
