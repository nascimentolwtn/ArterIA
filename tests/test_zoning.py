import json
from pathlib import Path

from pyproj import Transformer

from arteria.demand.zoning import (
    EXTERNAL_ZONE_ID,
    NET_OFFSET,
    ZonePolygon,
    assign_edges_to_zones,
    build_taz_file,
    load_zones_from_study_areas,
)
from arteria.network.study_area import hull_buffer_polygon

REPO_ROOT = Path(__file__).parent.parent

# A real point inside SJC, used to build a zone polygon in WGS84 and then
# place toy net-local junctions near/far from it via the same net<->UTM
# offset the module under test uses, so the round trip is realistic.
REF_LONLAT = (-45.88, -23.18)
_TO_UTM = Transformer.from_crs(4326, 31983, always_xy=True).transform


def _net_xy(lonlat: tuple[float, float]) -> tuple[float, float]:
    utm_x, utm_y = _TO_UTM(*lonlat)
    return (utm_x - NET_OFFSET[0], utm_y - NET_OFFSET[1])


def _write_net(path: Path, junctions: dict[str, tuple[float, float]], edges: list[tuple]) -> None:
    j_xml = "".join(f'<junction id="{jid}" x="{x}" y="{y}"/>' for jid, (x, y) in junctions.items())
    e_xml = "".join(f'<edge id="{eid}" from="{f}" to="{t}"/>' for eid, f, t in edges)
    path.write_text(f"<net>{j_xml}{e_xml}</net>")


def _zone(zone_id: str, lonlat: tuple[float, float], buffer_m: float) -> ZonePolygon:
    geometry = hull_buffer_polygon([lonlat], buffer_m=buffer_m, projected_crs="EPSG:31983")
    return ZonePolygon(id=zone_id, name=zone_id.upper(), geometry=geometry)


def test_assign_edges_to_zones_matches_midpoint_inside_the_zone_polygon(tmp_path):
    near_a, near_b = (
        _net_xy(REF_LONLAT),
        (
            _net_xy(REF_LONLAT)[0] + 10,
            _net_xy(REF_LONLAT)[1] + 10,
        ),
    )
    far_a, far_b = (near_a[0] + 5000, near_a[1] + 5000), (near_a[0] + 5010, near_a[1] + 5010)

    net_path = tmp_path / "toy.net.xml"
    _write_net(
        net_path,
        {"n1": near_a, "n2": near_b, "f1": far_a, "f2": far_b},
        [("in_edge", "n1", "n2"), ("out_edge", "f1", "f2")],
    )

    zones = [_zone("z", REF_LONLAT, buffer_m=200)]
    assignment = assign_edges_to_zones(net_path, zones)

    assert assignment["in_edge"] == "z"
    assert assignment["out_edge"] == EXTERNAL_ZONE_ID


def test_assign_edges_to_zones_skips_internal_edges(tmp_path):
    near = _net_xy(REF_LONLAT)
    net_path = tmp_path / "toy.net.xml"
    _write_net(
        net_path,
        {"n1": near, "n2": (near[0] + 10, near[1] + 10)},
        [("in_edge", "n1", "n2"), (":n1_0", "n1", "n2")],
    )

    zones = [_zone("z", REF_LONLAT, buffer_m=200)]
    assignment = assign_edges_to_zones(net_path, zones)

    assert set(assignment) == {"in_edge"}


def test_load_zones_from_study_areas_skips_disabled(tmp_path):
    geometry = hull_buffer_polygon([REF_LONLAT], buffer_m=100, projected_crs="EPSG:31983")
    geojson_path = tmp_path / "study-areas.geojson"
    geojson_path.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {"id": "x", "name": "X", "enabled": True},
                        "geometry": geometry,
                    },
                    {
                        "type": "Feature",
                        "properties": {"id": "y", "name": "Y", "enabled": False},
                        "geometry": geometry,
                    },
                ],
            }
        )
    )
    zones = load_zones_from_study_areas(geojson_path)
    assert [z.id for z in zones] == ["x"]


def test_build_taz_file_writes_one_taz_per_zone_plus_external(tmp_path):
    near = _net_xy(REF_LONLAT)
    far = (near[0] + 5000, near[1] + 5000)
    net_path = tmp_path / "toy.net.xml"
    _write_net(
        net_path,
        {"n1": near, "n2": (near[0] + 10, near[1] + 10), "f1": far, "f2": (far[0] + 10, far[1])},
        [("in_edge", "n1", "n2"), ("out_edge", "f1", "f2")],
    )
    geojson_path = tmp_path / "study-areas.geojson"
    geojson_path.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {"id": "z", "name": "Z", "enabled": True},
                        "geometry": hull_buffer_polygon(
                            [REF_LONLAT], buffer_m=200, projected_crs="EPSG:31983"
                        ),
                    }
                ],
            }
        )
    )
    output_path = tmp_path / "out" / "toy.taz.xml"

    result = build_taz_file(net_path, geojson_path, output_path)

    assert result.total_edges == 2
    assert result.zone_edge_counts == {"z": 1, EXTERNAL_ZONE_ID: 1}
    assert result.empty_zones == []
    assert output_path.exists()
    written = output_path.read_text()
    assert 'id="z" edges="in_edge"' in written
    assert f'id="{EXTERNAL_ZONE_ID}" edges="out_edge"' in written


def test_build_taz_file_flags_empty_zones(tmp_path):
    near = _net_xy(REF_LONLAT)
    net_path = tmp_path / "toy.net.xml"
    _write_net(net_path, {"n1": near, "n2": (near[0] + 10, near[1] + 10)}, [("e", "n1", "n2")])
    geojson_path = tmp_path / "study-areas.geojson"
    geojson_path.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {"id": "z", "name": "Z", "enabled": True},
                        "geometry": hull_buffer_polygon(
                            [REF_LONLAT], buffer_m=200, projected_crs="EPSG:31983"
                        ),
                    },
                    {
                        "type": "Feature",
                        "properties": {"id": "empty", "name": "Empty", "enabled": True},
                        "geometry": hull_buffer_polygon(
                            [(REF_LONLAT[0] + 1, REF_LONLAT[1] + 1)],
                            buffer_m=50,
                            projected_crs="EPSG:31983",
                        ),
                    },
                ],
            }
        )
    )

    result = build_taz_file(net_path, geojson_path, tmp_path / "out.taz.xml")

    assert set(result.empty_zones) == {"empty", EXTERNAL_ZONE_ID}


def test_sjc_study_areas_geojson_loads_the_four_enabled_candidates():
    zones = load_zones_from_study_areas(REPO_ROOT / "cities" / "sjc" / "study-areas.geojson")
    assert sorted(z.id for z in zones) == ["a", "b", "c", "d"]
