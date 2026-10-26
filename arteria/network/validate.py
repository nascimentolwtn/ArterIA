"""Network validation checks (roadmap P2.5/P2.7): connectivity (strongly
connected components), dead ends (traps vs. clip-boundary), lane counts,
connection consistency, speed limits and traffic-light presence, run against a
SUMO `.net.xml`-shaped document. Internal (`:`-prefixed / `function=internal`)
edges are skipped. One-way status is reported as a statistic (opposite-edge
pairs), since real `.net.xml` carries no `oneway` attribute.

Remote sessions never build a real network (ADR 0009: no `sumo`/`netconvert`
binary, no `sumolib`), so this parses the plain-XML net format directly with
the stdlib. It is exercised against hand-written toy fixtures and a small slice
of the real candidate-B network. This module is what `arteria network validate`
and the P2.7 diff/report wrap.
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

Severity = Literal["error", "warning", "info"]

# A dead end within this many metres of the convex hull of all junctions is
# attributed to the study-area clip rather than to the street network itself.
CLIP_BOUNDARY_MARGIN_M = 50.0


class Finding(BaseModel):
    severity: Severity
    check: str
    message: str


class ValidationReport(BaseModel):
    findings: list[Finding] = []
    # Counts worth printing next to the findings (edges, one-way/two-way split,
    # strongly-connected-component sizes, ...).
    stats: dict[str, int | float] = {}

    @property
    def has_blocking_issues(self) -> bool:
        return any(f.severity == "error" for f in self.findings)

    def by_severity(self, severity: Severity) -> list[Finding]:
        return [f for f in self.findings if f.severity == severity]


def _is_internal(edge: ET.Element) -> bool:
    return edge.get("id", "").startswith(":") or edge.get("function") in {
        "internal",
        "crossing",
        "walkingarea",
    }


def _convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[tuple[float, float]] = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: list[tuple[float, float]] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _dist_to_hull(p: tuple[float, float], hull: list[tuple[float, float]]) -> float:
    if len(hull) < 3:
        return float("inf")
    best = float("inf")
    for i, a in enumerate(hull):
        b = hull[(i + 1) % len(hull)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        denom = dx * dx + dy * dy
        t = 0.0
        if denom:
            t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / denom))
        best = min(best, math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy))
    return best


def _strongly_connected_components(graph: dict[str, set[str]]) -> list[list[str]]:
    """Iterative Tarjan; `graph` maps node -> successors (all nodes are keys)."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    components: list[list[str]] = []
    counter = 0
    for start in sorted(graph):
        if start in index:
            continue
        index[start] = low[start] = counter
        counter += 1
        stack.append(start)
        on_stack.add(start)
        work = [(start, iter(sorted(graph[start])))]
        while work:
            node, it = work[-1]
            advanced = False
            for succ in it:
                if succ not in index:
                    index[succ] = low[succ] = counter
                    counter += 1
                    stack.append(succ)
                    on_stack.add(succ)
                    work.append((succ, iter(sorted(graph[succ]))))
                    advanced = True
                    break
                if succ in on_stack:
                    low[node] = min(low[node], index[succ])
            if advanced:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index[node]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)
                    if w == node:
                        break
                components.append(comp)
    return components


def validate_network(
    path: str | Path, clip_margin_m: float = CLIP_BOUNDARY_MARGIN_M
) -> ValidationReport:
    root = ET.parse(path).getroot()

    findings: list[Finding] = []
    stats: dict[str, int | float] = {}

    all_edges = root.findall("edge")
    edges = [e for e in all_edges if not _is_internal(e)]
    junctions = [j for j in root.findall("junction") if j.get("type") != "internal"]
    connections = root.findall("connection")

    edge_by_id = {e.get("id", ""): e for e in all_edges}
    junction_by_id = {j.get("id", ""): j for j in junctions}
    junction_ids = set(junction_by_id)
    stats["edges"] = len(edges)
    stats["junctions"] = len(junctions)

    # Lane counts and speed limits per (non-internal) edge.
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
            lane_id = lane.get("id", "<unknown>")
            if speed is None:
                findings.append(
                    Finding(
                        severity="error",
                        check="speed_limit",
                        message=f"lane {lane_id!r} on edge {edge_id!r} has no speed attribute",
                    )
                )
            elif float(speed) <= 0:
                findings.append(
                    Finding(
                        severity="error",
                        check="speed_limit",
                        message=f"lane {lane_id!r} on edge {edge_id!r} has non-positive "
                        f"speed {speed!r}",
                    )
                )

    # One-way status: real `.net.xml` has no `oneway` attribute, so classify
    # by opposite-edge pairs (an edge a->b with a b->a partner is two-way).
    directed = {(e.get("from", ""), e.get("to", "")) for e in edges}
    one_way = sum(1 for a, b in directed if (b, a) not in directed)
    stats["one_way_edges"] = one_way
    stats["two_way_edges"] = len(directed) - one_way

    # Connections must reference edges/lanes that exist, with lane indices in range.
    for conn in connections:
        for end, lane_key in (("from", "fromLane"), ("to", "toLane")):
            edge_id = conn.get(end, "")
            lane_idx = conn.get(lane_key)
            edge_el = edge_by_id.get(edge_id)
            if edge_el is None:
                findings.append(
                    Finding(
                        severity="error",
                        check="connection_consistency",
                        message=f"connection references unknown {end}-edge {edge_id!r}",
                    )
                )
            elif lane_idx is not None:
                n_lanes = len(edge_el.findall("lane"))
                if int(lane_idx) >= n_lanes:
                    findings.append(
                        Finding(
                            severity="error",
                            check="connection_consistency",
                            message=f"connection {lane_key}={lane_idx!r} is out of range "
                            f"for edge {edge_id!r} ({n_lanes} lane(s))",
                        )
                    )

    # Traffic-light junctions should have a tlLogic program. Without one, SUMO
    # only breaks if connections are bound to it via `tl=`; otherwise the
    # junction behaves as unsignalised, so downgrade to a warning.
    tl_logic_ids = {tl.get("id", "") for tl in root.findall("tlLogic")}
    tl_bound = {c.get("tl", "") for c in connections if c.get("tl")}
    for junction in junctions:
        if junction.get("type") != "traffic_light":
            continue
        tl_id = junction.get("id", "")
        if tl_id in tl_logic_ids:
            continue
        bound = tl_id in tl_bound
        findings.append(
            Finding(
                severity="error" if bound else "warning",
                check="traffic_light_logic",
                message=f"junction {tl_id!r} is type='traffic_light' but has "
                f"no matching <tlLogic id={tl_id!r}>"
                + (
                    " and connections reference it"
                    if bound
                    else " (no connection uses it; effectively unsignalised)"
                ),
            )
        )

    # Directed junction graph from the non-internal edges.
    graph: dict[str, set[str]] = {j: set() for j in junction_ids}
    outgoing: dict[str, int] = {j: 0 for j in junction_ids}
    incoming: dict[str, int] = {j: 0 for j in junction_ids}
    for edge in edges:
        from_j, to_j = edge.get("from", ""), edge.get("to", "")
        if from_j in graph:
            outgoing[from_j] += 1
        if to_j in graph:
            incoming[to_j] += 1
        if from_j in graph and to_j in graph and from_j != to_j:
            graph[from_j].add(to_j)

    # Connectivity: junctions touched by no edge are errors; otherwise report
    # the main strongly connected component and the orphans outside it.
    for j in sorted(junction_ids):
        if not outgoing[j] and not incoming[j]:
            findings.append(
                Finding(
                    severity="error",
                    check="connectivity",
                    message=f"junction {j!r} is not touched by any edge (isolated)",
                )
            )
    touched = {j for j in junction_ids if outgoing[j] or incoming[j]}
    if touched:
        sub = {j: {s for s in graph[j] if s in touched} for j in touched}
        comps = sorted(_strongly_connected_components(sub), key=lambda c: (-len(c), sorted(c)))
        main = comps[0]
        orphans = sum(len(c) for c in comps[1:])
        stats["main_component_junctions"] = len(main)
        stats["orphan_junctions"] = orphans
        stats["orphan_components"] = len(comps) - 1
        if orphans:
            sizes: dict[int, int] = {}
            for c in comps[1:]:
                sizes[len(c)] = sizes.get(len(c), 0) + 1
            hist = ", ".join(f"{n}x size {s}" for s, n in sorted(sizes.items(), reverse=True)[:5])
            examples = ", ".join(repr(x) for x in sorted(comps[1])[:3])
            findings.append(
                Finding(
                    severity="warning",
                    check="scc",
                    message=f"main strongly connected component has {len(main)} of "
                    f"{len(touched)} junctions ({100 * len(main) / len(touched):.1f}%); "
                    f"{orphans} junction(s) in {len(comps) - 1} other component(s) "
                    f"({hist}); e.g. {examples}",
                )
            )

    # Dead ends: a junction with incoming but no outgoing edge traps vehicles.
    # Those at the study-area clip boundary (near the convex hull of all
    # junctions) are expected and reported separately.
    def _xy(j: ET.Element) -> tuple[float, float] | None:
        if j.get("x") is None or j.get("y") is None:
            return None
        return float(j.get("x", "0")), float(j.get("y", "0"))

    hull = _convex_hull([xy for j in junctions if (xy := _xy(j)) is not None])
    boundary = 0
    for j in sorted(junction_ids):
        if not (incoming[j] and not outgoing[j]):
            continue
        xy = _xy(junction_by_id[j])
        if xy is not None and _dist_to_hull(xy, hull) <= clip_margin_m:
            boundary += 1
            findings.append(
                Finding(
                    severity="info",
                    check="clip_boundary_dead_end",
                    message=f"junction {j!r} has incoming edge(s) but no outgoing edge "
                    f"and lies at the study-area clip boundary",
                )
            )
        else:
            findings.append(
                Finding(
                    severity="warning",
                    check="dead_end",
                    message=f"junction {j!r} has incoming edge(s) but no outgoing edge "
                    f"(dead end)",
                )
            )
    stats["clip_boundary_dead_ends"] = boundary

    return ValidationReport(findings=findings, stats=stats)
