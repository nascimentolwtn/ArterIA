# ruff: noqa: E501
"""Draw candidate corridors C, D, A (and a derived B centreline plus the A-B link)
on the unified SJC network as ordered edge sequences (ADR 0016).

Run from the repo root with SUMO's python tools importable (the project venv):
    python cities/sjc/corridors/build_corridors.py

Method: each corridor is a list of "legs"; a leg is a list of (lon, lat) waypoints,
a set of preferred street names, and a routing mode. Waypoints snap to the nearest
passenger-usable edge (preferring named streets); consecutive waypoints are joined by
a least-cost path over the real directed network (cost = length, x PENALTY for
edges not on a preferred street), so one-way streets and missing connections are
honoured. Each leg is routed in both directions; a direction with no route is
reported, not faked.
Inputs : cities/sjc/network/sjc.net.xml, cities/sjc/study-areas.geojson
Outputs: cities/sjc/corridors/{corridors.geojson,sjc-corridors.kml,summary.json}
"""

from __future__ import annotations

import heapq
import json
from pathlib import Path

import sumolib

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PENALTY = 8.0

A_NAMES = {
    "Avenida Florestan Fernandes",
    "Avenida Senador Teotônio Vilela",
    "Rua Senador Teotônio Vilela",
    "Avenida Sen Teotonio Vilela",
}
D_NAMES = {
    "Avenida Doutor Eduardo Cury",
    "Avenida Jorge Zarur",
    "Avenida Doutor Jorge Zarur",
    "Avenida São João",
    "Avenida Cassiano Ricardo",
    "Arco da Inovação",
    "Avenida Major Miguel Naked",
    "Ponte Pastor Paulo Leivas Macalão",
}
B_NAMES = {"Avenida Andrômeda"}
C_EXT_NAMES = {
    "Avenida Barão do Rio Branco",
    "Rua Madre Paula de São José",
    "Rua José Francisco Alves",
}
PERSEU = {"Avenida Perseu"}
CASSIOPEIA = {"Avenida Cassiopéia"}

# id -> (label, [leg dicts])  ; points are (lon, lat)
LEGS = {
    "A": (
        "Anel Viario: Av. Florestan Fernandes -> Av. Senador Teotonio Vilela",
        [dict(name="anel-viario", names=A_NAMES, pts=[(-45.9012, -23.2196), (-45.8762, -23.1772)])],
    ),
    "D": (
        "Jardim Colinas roundabout / Arco da Inovacao (Ponte Estaiada) and its avenues",
        [
            dict(
                name="cury-arco-zarur",
                names=D_NAMES,
                pts=[(-45.9115, -23.2000), (-45.9060, -23.2050), (-45.9005, -23.2105)],
            ),
            dict(
                name="sao-joao-cassiano",
                names=D_NAMES,
                pts=[(-45.9060, -23.2050), (-45.9135, -23.2255)],
            ),
        ],
    ),
    "C": (
        "Centro / Sao Dimas / Vila Adyana one-way maze (street-level spine)",
        [
            dict(
                name="sao-dimas-adyana-centro",
                names=set(),
                pts=[(-45.8895, -23.2000), (-45.8919, -23.1964), (-45.8872, -23.1852)],
            ),
            # extension, owner feedback 2026-10-27: Parque Vicentina Aranha, Av. Rio Branco,
            # R. Madre Paula de Sao Jose, R. Jose Francisco Alves (one-way loop structure)
            dict(
                name="vicentina-rio-branco-loop",
                names=C_EXT_NAMES,
                pts=[
                    (-45.8953, -23.1983),
                    (-45.9017, -23.1950),
                    (-45.9030, -23.2018),
                    (-45.9005, -23.2030),
                    (-45.9025, -23.2059),
                ],
            ),
        ],
    ),
    "B": (
        "Av. Andromeda spine, and the actual route from it to DCTA (derived, see README)",
        [
            dict(name="andromeda", names=B_NAMES, pts=[(-45.8867, -23.2280), (-45.8895, -23.2178)]),
            dict(
                name="andromeda-to-dcta",
                names=set(),
                pts=[(-45.8895, -23.2178), (-45.8824, -23.2057)],
            ),
            # extension, owner feedback 2026-10-27: loop/one-way structure continues south
            # through Jd. Satelite (Av. Perseu, Av. Cassiopeia)
            dict(
                name="satelite-perseu",
                names=PERSEU,
                pts=[(-45.8909, -23.2345), (-45.8893, -23.2225)],
            ),
            dict(
                name="satelite-cassiopeia",
                names=CASSIOPEIA,
                pts=[(-45.8802, -23.2296), (-45.8904, -23.2290)],
            ),
        ],
    ),
}


def snap(net, lon, lat, names, k=4):
    """Up to k nearest passenger edges, preferred-name edges first (strict when any
    preferred edge lies within 800 m)."""
    x, y = net.convertLonLat2XY(lon, lat)
    for radius in (120, 300, 800):
        pref, other = [], []
        for e, d in net.getNeighboringEdges(x, y, radius):
            if e.getFunction() or not e.allows("passenger"):
                continue
            (pref if (not names or e.getName() in names) else other).append((d, e))
        pool = pref or other
        if pool and (pref or radius == 800):
            return [e for _, e in sorted(pool, key=lambda t: t[0])[:k]]
    raise RuntimeError(f"no edge near {lon},{lat}")


def route(net, src, dst, names, penalty=PENALTY):
    def cost(e):
        if not names or e.getName() in names:
            return e.getLength()
        # unnamed pieces are usually ramps/connectors of the named street
        return e.getLength() * (1.5 if not e.getName() else penalty)

    dist = {src: cost(src)}
    prev = {}
    pq = [(dist[src], 0, src.getID(), src)]
    n = 0
    while pq:
        d, _, _, e = heapq.heappop(pq)
        if e is dst:
            break
        if d > dist.get(e, 1e18):
            continue
        for nxt in e.getOutgoing():
            if nxt.getFunction() or not nxt.allows("passenger"):
                continue
            nd = d + cost(nxt)
            if nd < dist.get(nxt, 1e18):
                dist[nxt] = nd
                prev[nxt] = e
                n += 1
                heapq.heappush(pq, (nd, n, nxt.getID(), nxt))
    if dst not in dist:
        return None
    path = [dst]
    while path[-1] is not src:
        path.append(prev[path[-1]])
    return path[::-1]


def route_pts(net, pts, names):
    cands = [snap(net, lon, lat, names) for lon, lat in pts]
    full, starts = [], cands[0]
    for nxt in cands[1:]:
        best = None
        for a in starts:
            for b in nxt:
                p = route(net, a, b, names)
                if p is not None:
                    c = sum(e.getLength() for e in p)
                    if best is None or c < best[0]:
                        best = (c, p)
        if best is None:
            return None, cands
        full += best[1] if not full else best[1][1:]
        starts = [best[1][-1]]
    return full, cands


def lonlat_line(net, edges):
    pts = []
    for e in edges:
        for p in e.getShape():
            ll = net.convertXY2LonLat(*p)
            if not pts or pts[-1] != ll:
                pts.append(ll)
    return [[round(a, 6), round(b, 6)] for a, b in pts]


def describe(net, edges):
    names, last = [], None
    for e in edges:
        n = e.getName() or "(unnamed)"
        if n != last:
            names.append(n)
            last = n
    return dict(
        edges=[e.getID() for e in edges],
        length_m=round(sum(e.getLength() for e in edges)),
        streets=names,
        oneway_note=None,
    )


def main():
    net = sumolib.net.readNet(str(ROOT / "cities/sjc/network/sjc.net.xml"))
    feats, summary = [], {}
    ends = {}
    for cid, (label, legs) in LEGS.items():
        for leg in legs:
            for tag, pts in (("fwd", leg["pts"]), ("rev", leg["pts"][::-1])):
                edges, snapped = route_pts(net, pts, leg["names"])
                key = f"{cid}/{leg['name']}/{tag}"
                if edges is None:
                    summary[key] = dict(error="no directed route between waypoints")
                    continue
                d = describe(net, edges)
                summary[key] = d
                ends[key] = edges
                feats.append(
                    dict(
                        type="Feature",
                        properties=dict(
                            corridor=cid,
                            leg=leg["name"],
                            direction=tag,
                            label=label,
                            length_m=d["length_m"],
                            n_edges=len(d["edges"]),
                            edges=d["edges"],
                        ),
                        geometry=dict(type="LineString", coordinates=lonlat_line(net, edges)),
                    )
                )
    # A-B link: from the Anel Viario's Dutra-interchange area to the Andromeda spine start.
    a_pt, b_pt = (-45.8950, -23.2125), (-45.8895, -23.2178)
    for tag, pts in (("A_to_B", [a_pt, b_pt]), ("B_to_A", [b_pt, a_pt])):
        edges, snapped = route_pts(net, pts, set())
        key = f"LINK/a-b/{tag}"
        if edges is None:
            summary[key] = dict(error="no directed route")
            continue
        d = describe(net, edges)
        summary[key] = d
        feats.append(
            dict(
                type="Feature",
                properties=dict(
                    corridor="LINK",
                    leg="a-b",
                    direction=tag,
                    label="A-B connecting route (least-cost real route)",
                    length_m=d["length_m"],
                    n_edges=len(d["edges"]),
                    edges=d["edges"],
                ),
                geometry=dict(type="LineString", coordinates=lonlat_line(net, edges)),
            )
        )
    (OUT / "corridors.geojson").write_text(
        json.dumps(dict(type="FeatureCollection", features=feats), ensure_ascii=False)
    )
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    write_kml(feats)
    for k, v in summary.items():
        print(k, v.get("length_m"), len(v.get("edges", [])), v.get("error", ""))


COL = {
    "A": "ff0000ff",
    "B": "ffff8000",
    "C": "ff00a5ff",
    "D": "ff00c000",
    "LINK": "ffff00ff",
}  # aabbggrr


def write_kml(feats):
    areas = json.loads((ROOT / "cities/sjc/study-areas.geojson").read_text())["features"]
    styles = "".join(
        f'<Style id="s{k}"><LineStyle><color>{c}</color><width>{5 if k != "LINK" else 6}</width></LineStyle></Style>'
        for k, c in COL.items()
    )
    styles += "".join(
        f'<Style id="p{k}"><LineStyle><color>{c}</color><width>2</width></LineStyle>'
        f"<PolyStyle><fill>0</fill></PolyStyle></Style>"
        for k, c in COL.items()
    )
    body = ["<Folder><name>Study-area polygons (draft; B and C extended 2026-10-27)</name>"]
    for f in areas:
        k = f["properties"]["id"].upper()
        ring = " ".join(f"{x},{y},0" for x, y in f["geometry"]["coordinates"][0])
        body.append(
            f"<Placemark><name>Area {k}</name><styleUrl>#p{k}</styleUrl><Polygon><outerBoundaryIs>"
            f"<LinearRing><coordinates>{ring}</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>"
        )
    body.append("</Folder><Folder><name>Corridor centrelines (network edges)</name>")
    for f in feats:
        p = f["properties"]
        k = p["corridor"]
        coords = " ".join(f"{x},{y},0" for x, y in f["geometry"]["coordinates"])
        body.append(
            f'<Placemark><name>{k} {p["leg"]} {p["direction"]} ({p["length_m"]} m)</name>'
            f'<description>{p["label"]}; {p["n_edges"]} edges</description><styleUrl>#s{k}</styleUrl>'
            f'<LineString><tessellate>1</tessellate><coordinates>{coords}</coordinates></LineString></Placemark>'
        )
    body.append("</Folder>")
    (OUT / "sjc-corridors.kml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
        f'<name>ArterIA SJC corridors (draft)</name>{styles}{"".join(body)}</Document></kml>'
    )


if __name__ == "__main__":
    main()
