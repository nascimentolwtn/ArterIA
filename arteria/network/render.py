"""Map renders of the built net and the study areas (roadmap P2.7).

Draws edges by SUMO priority with the enabled study-area outlines: one overview
of the area envelope and one zoom per area. Output is not committed. Needs the
`geo` extra plus sumolib and matplotlib.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

NET_OFFSET = (384192.69, 7414390.50)  # net (x, y) + offset = EPSG:31983; see crosscheck.py
OVERVIEW_MARGIN_M = 1000.0  # around the envelope of the study areas
AREA_MARGIN_M = 150.0  # around each area's bounding box
# (predicate on edge priority, colour, line width, legend label)
_CLASSES = [
    (lambda p: p >= 9, "#b2182b", 2.2, "priority >= 9"),
    (lambda p: 7 <= p < 9, "#ef8a62", 1.5, "7-8"),
    (lambda p: 5 <= p < 7, "#4d4d4d", 0.9, "5-6"),
    (lambda p: p < 5, "#999999", 0.4, "< 5"),
]
_README = """ArterIA SJC map renders (P2.7). Generated from cities/sjc/network/sjc.net.xml; not committed.
Edges coloured/weighted by SUMO edge priority; blue outlines = the four enabled study areas (a-d).
overview.png - zoomed to the envelope of the four study areas plus a 1000 m margin (the full net, convBoundary (0,0)-(37926,27652) m, is much larger and was dominated by one long motorway edge), net coordinates.
area-a.png   - Anel Viario and its access roads.
area-b.png   - Av. Andromeda <-> DCTA / Jardim Satelite.
area-c.png   - Centro / Sao Dimas / Vila Adyana one-way maze.
area-d.png   - Jardim Colinas roundabout / Ponte Estaiada.
Each area render is the polygon bounding box plus 150 m.
"""  # noqa: E501


def render_maps(
    city_dir: Path,
    out_dir: Path,
    city: str,
    log: Callable[[str], None] = lambda _msg: None,
) -> list[Path]:
    """Write overview.png, area-<id>.png and README.txt to `out_dir`."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import sumolib
    from matplotlib.collections import LineCollection
    from pyproj import Transformer
    from shapely.affinity import translate
    from shapely.geometry import shape
    from shapely.ops import transform

    net_path = city_dir / "network" / f"{city}.net.xml"
    areas_path = city_dir / "study-areas.geojson"
    for path in (net_path, areas_path):
        if not path.exists():
            raise FileNotFoundError(path)

    dx, dy = NET_OFFSET
    to_utm = Transformer.from_crs(4326, 31983, always_xy=True).transform
    features = json.loads(areas_path.read_text(encoding="utf-8"))["features"]
    # study polygons moved into net coordinates
    areas = [
        (
            f["properties"]["id"],
            f["properties"]["name"],
            translate(transform(to_utm, shape(f["geometry"])), -dx, -dy),
        )
        for f in features
        if f["properties"].get("enabled")
    ]
    net = sumolib.net.readNet(str(net_path), withInternal=False)
    segs = [
        (e.getPriority(), e.getShape()) for e in net.getEdges() if e.getFunction() != "internal"
    ]

    def draw(ax, xl=None, yl=None) -> None:
        for in_class, colour, width, label in _CLASSES:
            lines = [shp for p, shp in segs if in_class(p)]
            if xl:
                lines = [
                    ln
                    for ln in lines
                    if any(xl[0] <= a <= xl[1] and yl[0] <= b <= yl[1] for a, b in ln)
                ]
            ax.add_collection(LineCollection(lines, colors=colour, linewidths=width, label=label))
        for area_id, _name, geom in areas:
            ax.plot(*geom.exterior.xy, color="#1f78b4", lw=1.8)
            c = geom.representative_point()
            ax.annotate(area_id.upper(), (c.x, c.y), color="#1f78b4", weight="bold", fontsize=12)
        ax.set_aspect("equal")
        ax.set_xlabel("net x (m)")
        ax.set_ylabel("net y (m)")

    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    fig, ax = plt.subplots(figsize=(12, 8.8))
    draw(ax)
    bounds = [g.bounds for _, _, g in areas]
    m = OVERVIEW_MARGIN_M
    ax.set_xlim(min(b[0] for b in bounds) - m, max(b[2] for b in bounds) + m)
    ax.set_ylim(min(b[1] for b in bounds) - m, max(b[3] for b in bounds) + m)
    ax.legend(loc="lower right", title="edge priority", fontsize=8)
    ax.set_title("SJC network, study-area envelope (edges by priority; blue = study areas)")
    written.append(out_dir / "overview.png")
    fig.savefig(written[-1], dpi=150, bbox_inches="tight")
    plt.close(fig)

    for area_id, name, geom in areas:
        x0, y0, x1, y1 = geom.bounds
        m = AREA_MARGIN_M
        xl, yl = (x0 - m, x1 + m), (y0 - m, y1 + m)
        fig, ax = plt.subplots(figsize=(10, 10 * (yl[1] - yl[0]) / (xl[1] - xl[0])))
        draw(ax, xl, yl)
        ax.set_xlim(*xl)
        ax.set_ylim(*yl)
        ax.legend(loc="best", title="edge priority", fontsize=8)
        ax.set_title(f"Area {area_id.upper()}: {name}")
        written.append(out_dir / f"area-{area_id}.png")
        fig.savefig(written[-1], dpi=150, bbox_inches="tight")
        plt.close(fig)

    readme = out_dir / "README.txt"
    readme.write_text(_README, encoding="utf-8")
    written.append(readme)
    for path in written:
        log(f"Wrote {path}")
    return written
