"""Network diff between two builds (roadmap P2.7).

Compares two SUMO `.net.xml` files by id and reports edges, lanes and
junctions added, removed or changed (length, lane count, speed, allowed
vehicle classes, junction type/position). Internal (`:`) edges and lanes are
ignored; they follow from the junctions. JSON for tools, markdown for people.
"""

from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from pydantic import BaseModel, Field

EDGE_ATTRS = ("from", "to", "type", "priority")
LANE_ATTRS = ("speed", "length", "allow", "disallow")
JUNCTION_ATTRS = ("type", "x", "y")
_ROUND = {"speed": 2, "length": 2, "x": 2, "y": 2}


class Change(BaseModel):
    id: str
    attribute: str
    old: str | None
    new: str | None


class KindDiff(BaseModel):
    added: list[str] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)
    changed: list[Change] = Field(default_factory=list)


class NetworkDiff(BaseModel):
    old: str
    new: str
    edges: KindDiff
    lanes: KindDiff
    junctions: KindDiff

    @property
    def identical(self) -> bool:
        return not any(
            (k.added or k.removed or k.changed) for k in (self.edges, self.lanes, self.junctions)
        )


def _norm(attr: str, value: str | None) -> str | None:
    if value is None:
        return None
    if attr in _ROUND:
        try:
            return f"{float(value):.{_ROUND[attr]}f}"
        except ValueError:
            return value
    if attr in ("allow", "disallow"):
        return " ".join(sorted(value.split()))
    return value


def _load(path: Path) -> tuple[dict, dict, dict]:
    """(edges, lanes, junctions): id -> normalised attribute dict."""
    edges: dict[str, dict] = {}
    lanes: dict[str, dict] = {}
    junctions: dict[str, dict] = {}
    edge_lanes: dict[str, int] = {}
    current: str | None = None
    for _, el in ET.iterparse(path, events=("end",)):
        if el.tag == "lane":
            lane_id = el.get("id", "")
            if not lane_id.startswith(":"):
                lanes[lane_id] = {a: _norm(a, el.get(a)) for a in LANE_ATTRS}
                current = lane_id.rsplit("_", 1)[0]
                edge_lanes[current] = edge_lanes.get(current, 0) + 1
        elif el.tag == "edge":
            edge_id = el.get("id", "")
            if not edge_id.startswith(":") and el.get("function") != "internal":
                edges[edge_id] = {a: _norm(a, el.get(a)) for a in EDGE_ATTRS}
                edges[edge_id]["numLanes"] = str(edge_lanes.get(edge_id, 0))
            el.clear()
        elif el.tag == "junction":
            junction_id = el.get("id", "")
            if not junction_id.startswith(":"):
                junctions[junction_id] = {a: _norm(a, el.get(a)) for a in JUNCTION_ATTRS}
            el.clear()
    return edges, lanes, junctions


def _diff_kind(old: dict, new: dict) -> KindDiff:
    diff = KindDiff(added=sorted(new.keys() - old.keys()), removed=sorted(old.keys() - new.keys()))
    for key in sorted(old.keys() & new.keys()):
        for attr in old[key].keys() | new[key].keys():
            if old[key].get(attr) != new[key].get(attr):
                diff.changed.append(
                    Change(id=key, attribute=attr, old=old[key].get(attr), new=new[key].get(attr))
                )
    return diff


def diff_networks(old_path: Path, new_path: Path) -> NetworkDiff:
    old_edges, old_lanes, old_junctions = _load(old_path)
    new_edges, new_lanes, new_junctions = _load(new_path)
    return NetworkDiff(
        old=str(old_path),
        new=str(new_path),
        edges=_diff_kind(old_edges, new_edges),
        lanes=_diff_kind(old_lanes, new_lanes),
        junctions=_diff_kind(old_junctions, new_junctions),
    )


def render_markdown(diff: NetworkDiff, *, limit: int = 25) -> str:
    lines = [
        "# Network diff",
        "",
        f"- old: `{diff.old}`",
        f"- new: `{diff.new}`",
        "",
        "| kind | added | removed | changed |",
        "|------|-------|---------|---------|",
    ]
    kinds = (("edges", diff.edges), ("lanes", diff.lanes), ("junctions", diff.junctions))
    for name, k in kinds:
        lines.append(f"| {name} | {len(k.added)} | {len(k.removed)} | {len(k.changed)} |")
    for name, k in kinds:
        for label, items in (("added", k.added), ("removed", k.removed)):
            if items:
                shown = ", ".join(f"`{i}`" for i in items[:limit])
                more = f" (+{len(items) - limit} more)" if len(items) > limit else ""
                lines += ["", f"## {name} {label}", "", shown + more]
        if k.changed:
            lines += ["", f"## {name} changed", ""]
            lines += [f"- `{c.id}` {c.attribute}: {c.old} -> {c.new}" for c in k.changed[:limit]]
            if len(k.changed) > limit:
                lines.append(f"- (+{len(k.changed) - limit} more)")
    if diff.identical:
        lines += ["", "The networks are identical."]
    return "\n".join(lines) + "\n"


_HEADER_COMMENT = re.compile(rb"^\s*<\?xml[^>]*\?>\s*<!--.*?-->", re.DOTALL)


def net_content_sha256(path: Path) -> str:
    """sha256 of a `.net.xml` without netconvert's leading `<!-- generated on
    <timestamp> ... -->` comment (it embeds the build time and output path, so
    the raw file hash changes on every build even when the network is the same)."""
    data = path.read_bytes()
    return hashlib.sha256(_HEADER_COMMENT.sub(b"", data, count=1)).hexdigest()
