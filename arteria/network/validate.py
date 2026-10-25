"""Network validation checks (roadmap P2.5/P2.7): connectivity, dead ends,
lane counts, one-way status, connection consistency, speed limits and
traffic-light presence, run against a SUMO `.net.xml`-shaped document.

Remote sessions never build a real network (ADR 0009: no `sumo`/`netconvert`
binary, no `sumolib`), so this parses the plain-XML net format directly with
the stdlib and is exercised only against hand-written toy fixtures. The real
build and visual check stay at the desk (L9-L11); this module is what a
future `arteria network validate` command and the P2.7 diff/report wrap.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

Severity = Literal["error", "warning"]


class Finding(BaseModel):
    severity: Severity
    check: str
    message: str


class ValidationReport(BaseModel):
    findings: list[Finding] = []

    @property
    def has_blocking_issues(self) -> bool:
        return any(f.severity == "error" for f in self.findings)

    def by_severity(self, severity: Severity) -> list[Finding]:
        return [f for f in self.findings if f.severity == severity]


def validate_network(path: str | Path) -> ValidationReport:
    tree = ET.parse(path)
    root = tree.getroot()

    findings: list[Finding] = []

    edges = root.findall("edge")
    junctions = root.findall("junction")
    connections = root.findall("connection")

    edge_ids = {e.get("id", "") for e in edges}
    junction_ids = {j.get("id", "") for j in junctions}

    # Lane counts and speed limits per edge.
    for edge in edges:
        edge_id = edge.get("id", "<unknown>")
        lanes = edge.findall("lane")
        if len(lanes) < 1:
            findings.append(
                Finding(
                    severity="error",
                    check="lane_count",
                    message=f"edge {edge_id!r} has no lanes",
                )
            )
        for lane in lanes:
            speed = lane.get("speed")
            if speed is None:
                findings.append(
                    Finding(
                        severity="error",
                        check="speed_limit",
                        message=f"lane {lane.get('id', '<unknown>')!r} on edge "
                        f"{edge_id!r} has no speed attribute",
                    )
                )
            elif float(speed) <= 0:
                findings.append(
                    Finding(
                        severity="error",
                        check="speed_limit",
                        message=f"lane {lane.get('id', '<unknown>')!r} on edge "
                        f"{edge_id!r} has non-positive speed {speed!r}",
                    )
                )

        # One-way status must be explicit: an edge should either carry its own
        # paired/opposite edge (`id` ending `-id`/reversed `from`/`to`) or an
        # explicit marker; here we require the `oneway` attribute be present
        # so the build pipeline recorded a deliberate decision rather than
        # relying on netconvert's default guess.
        if edge.get("oneway") is None:
            findings.append(
                Finding(
                    severity="warning",
                    check="oneway_status",
                    message=f"edge {edge_id!r} has no explicit 'oneway' attribute",
                )
            )

    # Connections must reference edges/lanes that exist, and lane indices
    # must be in range for their edge.
    for conn in connections:
        from_edge = conn.get("from", "")
        to_edge = conn.get("to", "")
        from_lane_idx = conn.get("fromLane")
        to_lane_idx = conn.get("toLane")

        if from_edge not in edge_ids:
            findings.append(
                Finding(
                    severity="error",
                    check="connection_consistency",
                    message=f"connection references unknown from-edge {from_edge!r}",
                )
            )
        if to_edge not in edge_ids:
            findings.append(
                Finding(
                    severity="error",
                    check="connection_consistency",
                    message=f"connection references unknown to-edge {to_edge!r}",
                )
            )

        from_edge_el = next((e for e in edges if e.get("id") == from_edge), None)
        if from_edge_el is not None and from_lane_idx is not None:
            n_lanes = len(from_edge_el.findall("lane"))
            if int(from_lane_idx) >= n_lanes:
                findings.append(
                    Finding(
                        severity="error",
                        check="connection_consistency",
                        message=f"connection fromLane={from_lane_idx!r} is out of range "
                        f"for edge {from_edge!r} ({n_lanes} lane(s))",
                    )
                )

        to_edge_el = next((e for e in edges if e.get("id") == to_edge), None)
        if to_edge_el is not None and to_lane_idx is not None:
            n_lanes = len(to_edge_el.findall("lane"))
            if int(to_lane_idx) >= n_lanes:
                findings.append(
                    Finding(
                        severity="error",
                        check="connection_consistency",
                        message=f"connection toLane={to_lane_idx!r} is out of range "
                        f"for edge {to_edge!r} ({n_lanes} lane(s))",
                    )
                )

    # Traffic-light junctions should have a matching tlLogic program.
    tl_logic_ids = {tl.get("id", "") for tl in root.findall("tlLogic")}
    for junction in junctions:
        if junction.get("type") == "traffic_light":
            tl_id = junction.get("id", "")
            if tl_id not in tl_logic_ids:
                findings.append(
                    Finding(
                        severity="error",
                        check="traffic_light_logic",
                        message=f"junction {tl_id!r} is type='traffic_light' but has "
                        f"no matching <tlLogic id={tl_id!r}>",
                    )
                )

    # Connectivity and dead ends: build an undirected adjacency from edges'
    # from/to junctions, then flag unreachable junctions and edges whose
    # target junction has no outgoing edge (a dead end).
    outgoing_from: dict[str, list[str]] = {j: [] for j in junction_ids}
    incoming_to: dict[str, list[str]] = {j: [] for j in junction_ids}
    adjacency: dict[str, set[str]] = {j: set() for j in junction_ids}
    for edge in edges:
        from_j = edge.get("from", "")
        to_j = edge.get("to", "")
        if from_j in outgoing_from:
            outgoing_from[from_j].append(edge.get("id", ""))
        if to_j in incoming_to:
            incoming_to[to_j].append(edge.get("id", ""))
        if from_j in adjacency and to_j in adjacency:
            adjacency[from_j].add(to_j)
            adjacency[to_j].add(from_j)

    if junction_ids:
        start = next(iter(junction_ids))
        seen = {start}
        stack = [start]
        while stack:
            current = stack.pop()
            for neighbor in adjacency.get(current, ()):
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        unreachable = junction_ids - seen
        for j in sorted(unreachable):
            findings.append(
                Finding(
                    severity="error",
                    check="connectivity",
                    message=f"junction {j!r} is unreachable from junction {start!r}",
                )
            )

    for j in sorted(junction_ids):
        if incoming_to.get(j) and not outgoing_from.get(j):
            findings.append(
                Finding(
                    severity="warning",
                    check="dead_end",
                    message=f"junction {j!r} has incoming edge(s) but no outgoing edge "
                    f"(dead end)",
                )
            )

    return ValidationReport(findings=findings)
