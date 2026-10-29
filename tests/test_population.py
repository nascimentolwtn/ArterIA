import json
import sqlite3
import struct

import pytest
import shapely

from arteria.demand.population import (
    IBGE_SETORES_GPKG_URL_TEMPLATE,
    Setor,
    build_population_summary,
    download_setores_gpkg,
    load_setores,
    population_by_zone,
)
from arteria.demand.zoning import EXTERNAL_ZONE_ID, ZonePolygon


def _gpkg_blob(lon: float, lat: float) -> bytes:
    """A minimal GeoPackage geometry blob (no envelope) wrapping a WKB point,
    matching what `_gpkg_geometry_to_point` expects to unwrap."""
    header = b"GP" + bytes([0]) + bytes([0b00000001])  # version 0, little-endian, no envelope
    srs_id = struct.pack("<i", 4326)
    return header + srs_id + shapely.to_wkb(shapely.Point(lon, lat))


def _make_gpkg(path, rows: list[tuple[str, str, int, float, float]]) -> None:
    """rows: (CD_SETOR, CD_MUN, V0001, lon, lat)."""
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE setores (CD_SETOR TEXT, CD_MUN TEXT, V0001 INTEGER, geom BLOB)")
    for setor_id, mun, pop, lon, lat in rows:
        con.execute(
            "INSERT INTO setores VALUES (?, ?, ?, ?)",
            (setor_id, mun, pop, _gpkg_blob(lon, lat)),
        )
    con.commit()
    con.close()


def test_download_setores_gpkg_uses_the_uf_template_and_injected_download(tmp_path):
    calls = []

    def fake_download(url: str, dest) -> None:
        calls.append(url)
        dest.write_bytes(b"fake-gpkg")

    dest = tmp_path / "SP_setores_CD2022.gpkg"
    result = download_setores_gpkg("SP", dest, download=fake_download)

    assert result == dest
    assert dest.read_bytes() == b"fake-gpkg"
    assert calls == [IBGE_SETORES_GPKG_URL_TEMPLATE.format(uf="SP")]


def test_load_setores_filters_by_municipality_and_decodes_geometry(tmp_path):
    gpkg_path = tmp_path / "toy.gpkg"
    _make_gpkg(
        gpkg_path,
        [
            ("354990405000001", "3549904", 285, -45.88, -23.18),
            ("354990405000002", "3549904", 299, -45.87, -23.19),
            ("999999905000001", "9999999", 100, -46.0, -23.0),  # different municipality
        ],
    )

    setores = load_setores(gpkg_path, "setores", "3549904")

    assert len(setores) == 2
    assert {s.id for s in setores} == {"354990405000001", "354990405000002"}
    first = next(s for s in setores if s.id == "354990405000001")
    assert first.population == 285
    assert first.lon == pytest.approx(-45.88)
    assert first.lat == pytest.approx(-23.18)


def test_population_by_zone_sums_setores_inside_each_polygon(tmp_path):
    setores = [
        Setor(id="in_a", population=100, lon=-45.880, lat=-23.180),
        Setor(id="in_a_2", population=50, lon=-45.881, lat=-23.181),
        Setor(id="outside", population=30, lon=-45.950, lat=-23.300),
    ]
    zone_a = ZonePolygon(
        id="a",
        name="A",
        geometry={
            "type": "Polygon",
            "coordinates": [
                [
                    [-45.90, -23.17],
                    [-45.90, -23.19],
                    [-45.86, -23.19],
                    [-45.86, -23.17],
                    [-45.90, -23.17],
                ]
            ],
        },
    )

    totals = population_by_zone(setores, [zone_a])

    assert totals == {"a": 150, EXTERNAL_ZONE_ID: 30}


def test_build_population_summary_joins_zones_and_setores(tmp_path):
    city_dir = tmp_path / "city"
    city_dir.mkdir()
    (city_dir / "study-areas.geojson").write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {"id": "a", "name": "A", "enabled": True},
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [-45.90, -23.17],
                                    [-45.90, -23.19],
                                    [-45.86, -23.19],
                                    [-45.86, -23.17],
                                    [-45.90, -23.17],
                                ]
                            ],
                        },
                    }
                ],
            }
        )
    )
    gpkg_path = tmp_path / "toy.gpkg"
    _make_gpkg(
        gpkg_path,
        [
            ("354990405000001", "3549904", 285, -45.880, -23.180),
            ("354990405000002", "3549904", 30, -45.950, -23.300),
        ],
    )

    summary = build_population_summary(city_dir, "3549904", "setores", gpkg_path)

    assert summary.setor_count == 2
    assert summary.total_population == 315
    assert summary.population_by_zone == {"a": 285, EXTERNAL_ZONE_ID: 30}
