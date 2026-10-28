"""Corridor cross-check of the built net against IBGE faces and GeoSanja (roadmap P2.7).

Compares the SUMO net inside the study-area corridors with two external
sources: IBGE street faces (by normalised street name, then by distance on the
matched names) and GeoSanja `arruamentos` (geometry only). A screening tool,
not a calibration: name matching is deliberately untuned. JSON for tools,
markdown for people. Needs the `geo` extra plus pyshp and sumolib.
"""

from __future__ import annotations

import collections
import json
import re
import statistics
import unicodedata
from collections.abc import Callable
from pathlib import Path

NET_CRS = "EPSG:31983"  # SIRGAS 2000 / UTM 23S, the net and GeoSanja CRS
IBGE_CRS = "EPSG:4674"  # SIRGAS 2000 geographic, the IBGE faces CRS
# Net (x, y) -> UTM: netconvert's <location netOffset>, negated. Hardcoded for SJC.
NET_OFFSET = (384192.69, 7414390.50)
MASK_BUFFER_M = 50.0  # corridor mask = union of enabled study polygons + this buffer
THRESHOLD_M = 15.0  # "close enough" distance between two centrelines
SAMPLE_STEP_M = 5.0  # spacing of the OSM samples measured against IBGE
MAX_LISTED = 150  # cap on the unmatched-name lists written to the JSON
# Street-type words dropped from the front of a name before comparing.
_STREET_TYPES = {
    "RUA", "AVENIDA", "AV", "ESTRADA", "EST", "PRACA", "PCA", "ALAMEDA", "AL", "RODOVIA",
    "ROD", "TRAVESSA", "TRAV", "TV", "VIA", "VIELA", "LARGO", "PARQUE", "PQ",
}  # fmt: skip


class CrosscheckError(Exception):
    pass


def normalise_name(name: str) -> str:
    """Upper-case, accent-free, leading street-type words and spaces removed."""
    decomposed = unicodedata.normalize("NFD", name)
    plain = "".join(c for c in decomposed if not unicodedata.combining(c)).upper()
    tokens = re.sub(r"[^A-Z0-9 ]", " ", plain).split()
    while tokens and tokens[0] in _STREET_TYPES:
        tokens = tokens[1:]
    return "".join(tokens)


def _samples(geom):
    parts = geom.geoms if hasattr(geom, "geoms") else [geom]
    out = []
    for part in parts:
        n = max(1, int(part.length // SAMPLE_STEP_M))
        out += [part.interpolate((i + 0.5) / n, normalized=True) for i in range(n)]
    return out


def run_crosscheck(
    city_dir: Path,
    repo_root: Path,
    city: str,
    log: Callable[[str], None] = lambda _msg: None,
) -> dict:
    """Run the cross-check and return the result dict (see `write_outputs`)."""
    import shapefile  # pyshp
    import shapely.prepared
    import sumolib
    from pyproj import Transformer
    from shapely.geometry import LineString, shape
    from shapely.ops import transform, unary_union

    net_path = city_dir / "network" / f"{city}.net.xml"
    areas_path = city_dir / "study-areas.geojson"
    ibge_path = repo_root / "data" / "ibge-faces" / "3549904_faces_de_logradouros_2022.shp"
    geosanja_path = repo_root / "data" / "geosanja" / "arruamentos.geojson"
    for path in (net_path, areas_path, ibge_path, geosanja_path):
        if not path.exists():
            raise FileNotFoundError(path)

    to_utm = Transformer.from_crs(4326, NET_CRS, always_xy=True).transform
    features = json.loads(areas_path.read_text(encoding="utf-8"))["features"]
    areas = [
        transform(to_utm, shape(f["geometry"])) for f in features if f["properties"].get("enabled")
    ]
    if not areas:
        raise CrosscheckError(f"No enabled study areas in {areas_path}")
    mask = unary_union(areas).buffer(MASK_BUFFER_M)
    log(f"mask bounds {mask.bounds}")

    # OSM: edge centrelines from the net, clipped to the mask
    dx, dy = NET_OFFSET
    net = sumolib.net.readNet(str(net_path), withInternal=False)
    osm: dict[str, list] = {}  # key -> [names, clipped geometries]
    clipped = []
    types: collections.Counter = collections.Counter()  # edge types intersecting the mask
    types_whole_net: collections.Counter = collections.Counter()  # edge types, whole net
    n_whole_net_edges = 0
    for edge in net.getEdges():
        if edge.getFunction() == "internal":
            continue
        n_whole_net_edges += 1
        types_whole_net[edge.getType()] += 1
        pts = [(x + dx, y + dy) for x, y in edge.getShape()]
        if len(pts) < 2:
            continue
        geom = LineString(pts)
        if not geom.intersects(mask):
            continue
        types[edge.getType()] += 1
        part = geom.intersection(mask)
        if part.is_empty or part.length == 0:
            continue
        clipped.append(part)
        name = edge.getName()
        key = normalise_name(name) if name else ""
        if key:
            entry = osm.setdefault(key, [set(), []])
            entry[0].add(name)
            entry[1].append(part)
    log(f"osm edges {len(clipped)}, named keys {len(osm)}")
    osm_union = unary_union(clipped)

    # IBGE faces: key = title + name (e.g. CORONEL + name), reprojected to UTM
    ibge_utm = Transformer.from_crs(IBGE_CRS, NET_CRS, always_xy=True).transform
    reader = shapefile.Reader(str(ibge_path))
    fields = [f[0] for f in reader.fields[1:]]
    i_name, i_title = fields.index("NM_LOG"), fields.index("NM_TIT_LOG")
    ibge: dict[str, list] = {}
    n_segments = 0
    prepared = shapely.prepared.prep(mask)
    for sr in reader.iterShapeRecords():
        if not sr.shape.points:
            continue
        name = (sr.record[i_name] or "").strip()
        title = (sr.record[i_title] or "").strip()
        geom = transform(ibge_utm, shape(sr.shape.__geo_interface__))
        if not prepared.intersects(geom):
            continue
        n_segments += 1
        if not name or "SEM DENOMINA" in name.upper():
            continue
        key = normalise_name(f"{title} {name}")
        if key:
            entry = ibge.setdefault(key, [set(), []])
            entry[0].add(f"{title} {name}".strip())
            entry[1].append(geom)
    log(f"ibge segments {n_segments}, keys {len(ibge)}")

    matched = sorted(set(osm) & set(ibge))
    osm_only = sorted(set(osm) - set(ibge))
    ibge_only = sorted(set(ibge) - set(osm))

    # distance from OSM samples to the same-name IBGE geometry
    dists: list[float] = []
    per_name = {}
    for key in matched:
        target = unary_union(ibge[key][1])
        ds = [pt.distance(target) for g in osm[key][1] for pt in _samples(g)]
        dists += ds
        per_name[key] = (
            statistics.median(ds),
            sum(d > THRESHOLD_M for d in ds) / len(ds),
        )
    over = sorted(
        ((k, v) for k, v in per_name.items() if v[0] > THRESHOLD_M or v[1] > 0.5),
        key=lambda kv: -kv[1][0],
    )

    # GeoSanja: geometry only, fraction of length within the threshold both ways
    gs_features = json.loads(geosanja_path.read_text(encoding="utf-8"))["features"]
    gs_parts = []
    for f in gs_features:
        geom = shape(f["geometry"])
        if geom.intersects(mask):
            gs_parts.append(geom.intersection(mask))
    gs_union = unary_union(gs_parts)
    osm_in_mask = osm_union.intersection(mask)
    osm_near_gs = osm_in_mask.intersection(gs_union.buffer(THRESHOLD_M)).length
    gs_near_osm = gs_union.intersection(osm_in_mask.buffer(THRESHOLD_M)).length

    return dict(
        corridor_mask=f"union of 4 study polygons ({NET_CRS}) buffered {MASK_BUFFER_M:g} m",
        osm_edges=len(clipped),
        osm_named_keys=len(osm),
        ibge_segments_in_mask=n_segments,
        ibge_keys=len(ibge),
        matched=len(matched),
        osm_only=len(osm_only),
        ibge_only=len(ibge_only),
        matched_samples_5m=len(dists),
        median_sample_dist_m=statistics.median(dists),
        share_samples_over_15m=sum(d > THRESHOLD_M for d in dists) / len(dists),
        matched_names_over_15m=[
            dict(
                key=k,
                names=sorted(osm[k][0]),
                median_m=round(v[0], 1),
                share_over_15m=round(v[1], 3),
            )
            for k, v in over
        ][:60],
        n_matched_names_over_15m=len(over),
        osm_within_15m_of_geosanja_frac=osm_near_gs / osm_in_mask.length,
        geosanja_within_15m_of_osm_frac=gs_near_osm / gs_union.length,
        osm_edge_types_in_mask=dict(types.most_common(15)),
        osm_edge_types_whole_net=dict(types_whole_net.most_common(15)),
        osm_edges_whole_net=n_whole_net_edges,
        geosanja_features_in_mask=len(gs_parts),
        osm_only_names=[dict(key=k, names=sorted(osm[k][0])) for k in osm_only][:MAX_LISTED],
        ibge_only_names=[dict(key=k, names=sorted(ibge[k][0])[:2]) for k in ibge_only][:MAX_LISTED],
    )


_COLLISION_THRESHOLD_M = 500.0  # median far beyond block scale => likely a reused/generic name


def render_markdown(r: dict) -> str:
    """Human-readable summary of a `run_crosscheck` result.

    The worst-names list and edge-type counts below are computed from `r`, not
    hardcoded; only the apostrophe-artefact note is a standing observation about
    the net build, not something this function can detect from `r`.
    """
    osm_examples = ", ".join(x["names"][0] for x in r["osm_only_names"][:25])

    worst = r["matched_names_over_15m"][:8]
    worst_lines = []
    for w in worst:
        far = w["median_m"] > _COLLISION_THRESHOLD_M
        label = "likely name collision" if far else "worth a look"
        worst_lines.append(
            f"  - {' / '.join(w['names'])}: median {w['median_m']:.0f} m, "
            f"{w['share_over_15m']:.0%} of samples > 15 m ({label})"
        )
    worst_block = "\n".join(worst_lines) if worst_lines else "  - (none)"

    _road_types = ("highway.service", "highway.footway", "highway.cycleway")

    def _road_counts(types: dict) -> str:
        counts = ", ".join(f"{t} {n}" for t, n in types.items() if t in _road_types)
        return counts or "(none of highway.service/footway/cycleway found)"

    mask_counts = _road_counts(r["osm_edge_types_in_mask"])
    whole_net_counts = _road_counts(r["osm_edge_types_whole_net"])

    return f"""# SJC corridor cross-check (OSM net vs IBGE faces vs GeoSanja)

Mask: union of the 4 study polygons (EPSG:31983) + 50 m. Net coords -> UTM via +384192.69 / +7414390.50 (sanity-checked: mask bounds E 406-412k, N 7.430-7.437M). GeoSanja arruamentos is in the same CRS: arruamentos.geojson carries the explicit member `crs` = `urn:ogc:def:crs:EPSG::31983`. IBGE faces are reprojected from EPSG:4674.

## Names (normalised keys; accents/spaces/leading street-type words stripped)
- Keys: OSM key = normalised OSM `name`. IBGE key = normalised NM_TIT_LOG + NM_LOG (title, e.g. CORONEL, plus name). The street type (NM_TIP_LOG) is not in the key.
- OSM edges in mask: {r['osm_edges']}; named street keys: {r['osm_named_keys']}
- IBGE segments in mask: {r['ibge_segments_in_mask']}; named keys (excl. SEM DENOMINACAO): {r['ibge_keys']}
- Matched: {r['matched']} ({r['matched']/r['osm_named_keys']:.0%} of OSM keys, {r['matched']/r['ibge_keys']:.0%} of IBGE keys). The count is approximate: generic keys (DOIS, TRES, the single-character key D) reuse the same name in different neighbourhoods and cause some false matches, while spelling variants cause misses.
- OSM-only: {r['osm_only']}; IBGE-only: {r['ibge_only']} (full lists capped at 150 in the JSON)

## Geometry on matched names (screening result)
- Method: OSM edge centreline (sumolib edge shape), clipped to the mask, sampled every 5 m; distance from each sample to the union of same-name IBGE segments. Median is per metre of OSM length, not per vertex. Screening only: one-name-one-street matching (name collisions inflate some distances) and IBGE faces are block-face lines, not centrelines.
- {r['matched_samples_5m']} samples; median distance: {r['median_sample_dist_m']:.1f} m
- Share of samples > 15 m: {r['share_samples_over_15m']:.1%}
- Names with median > 15 m or > 50% of samples > 15 m: {r['n_matched_names_over_15m']} (full list in JSON). Worst 8 by median distance:
{worst_block}

## Geometry vs GeoSanja arruamentos (no names, clipped to mask)
- {r['osm_within_15m_of_geosanja_frac']:.1%} of OSM centreline length lies within 15 m of GeoSanja
- {r['geosanja_within_15m_of_osm_frac']:.1%} of GeoSanja length lies within 15 m of OSM
- The OSM-side figure is lower because the net contains non-street ways that GeoSanja arruamentos lacks. Two counts, different scopes, both computed from the current run: for the {r['osm_edges']} edges intersecting the study mask, {mask_counts} (service is the largest non-street class; many are internal access/parking roads), plus path and track; for the whole unified net ({r['osm_edges_whole_net']} non-internal edges, by the edge `type` attribute) it is {whole_net_counts}. The 81.5% figure refers to the mask, so the mask counts apply. GeoSanja is nearly fully covered by OSM. Raw length totals are not compared: each two-way OSM street yields two edges, so lengths are not like-for-like.

## Caveats on unmatched names (not forced)
- OSM-only examples: {osm_examples}.
  Many are real streets that IBGE spells differently: abbreviations or dropped connectives, spelling variants (Benedicto/Benedito), truncated OSM names ("Antonia M. A. Reichel"), number formats ("Rua 12 C"), plus non-street names (Avenida Aeroporto, Arco da Inovacao, Deck do Banhado, Ciclovia ..., "Acesso para ..."). (A netconvert bug that double-escaped apostrophes in street names, e.g. "D&apos;Oliveira", was fixed in `arteria.network.build`; this list reflects the corrected names.)
- IBGE-only keys (title is already part of the key) are mostly genuine spelling or word-order differences from OSM (e.g. ANTONIODEPAULAFERREIRA vs OSM "Antonio Paula Ferreira", ANTONIAMONTEIROAFONSOREICHEL vs "Antonia M. A. Reichel", connectives such as DE/DA/DOS present on one side only). Normalisation was deliberately not tuned.
"""  # noqa: E501


def write_outputs(result: dict, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "crosscheck.json"
    md_path = out_dir / "crosscheck.md"
    json_path.write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(result), encoding="utf-8")
    return json_path, md_path
