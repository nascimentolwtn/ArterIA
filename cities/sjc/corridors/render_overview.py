# ruff: noqa: E402
"""PNG overview of the corridors over the unified network (needs matplotlib and
sumolib; matplotlib is not a project dependency). Usage:
    python render_overview.py [out.png]
Reads cities/sjc/network/sjc.net.xml, corridors.geojson and study-areas.geojson."""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

here = Path(__file__).resolve().parent
import sumolib

net = sumolib.net.readNet(str(here.parent / "network/sjc.net.xml"))
edges = [
    dict(type=e.getType(), sh=[net.convertXY2LonLat(*p) for p in e.getShape()])
    for e in net.getEdges()
    if not e.getFunction()
]
out = sys.argv[1] if len(sys.argv) > 1 else str(here / "corridors-overview.png")
corr = json.load(open(here / "corridors.geojson"))["features"]
areas = json.load(open(here.parent / "study-areas.geojson"))["features"]
COL = {"A": "#d62728", "B": "#1f77b4", "C": "#ff8c00", "D": "#2ca02c", "LINK": "#c000c0"}
fig, ax = plt.subplots(figsize=(13, 15))
for e in edges:
    t = e["type"]
    major = any(k in t for k in ("motorway", "trunk", "primary", "secondary"))
    ax.plot(*zip(*e["sh"]), color="#999" if major else "#ddd", lw=0.9 if major else 0.4, zorder=1)
for f in areas:
    k = f["properties"]["id"].upper()
    xs, ys = zip(*f["geometry"]["coordinates"][0])
    ax.plot(xs, ys, color=COL[k], lw=1, ls="--", zorder=2)
    ax.text(max(xs), max(ys), "area " + k, color=COL[k], fontsize=9, ha="right")
seen = set()
for f in corr:
    k = f["properties"]["corridor"]
    xs, ys = zip(*f["geometry"]["coordinates"])
    lab = None if k in seen else {"LINK": "A-B link"}.get(k, "corridor " + k)
    seen.add(k)
    ax.plot(
        xs,
        ys,
        color=COL[k],
        lw=3.2 if f["properties"]["direction"] in ("fwd", "A_to_B") else 1.8,
        alpha=0.85,
        zorder=3,
        label=lab,
    )
ax.legend(loc="upper left")
ax.set_xlim(-45.918, -45.862)
ax.set_ylim(-23.242, -23.172)
ax.set_aspect(1.087)
ax.set_title("ArterIA SJC corridors on the unified network (draft; thick = fwd, thin = reverse)")
plt.tight_layout()
plt.savefig(out, dpi=110)
