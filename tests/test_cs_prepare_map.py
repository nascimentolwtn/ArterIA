from pathlib import Path

import pytest

from arteria.cs.prepare_map import (
    CS1_MAX_TILE_KM,
    PrepareMapError,
    compute_map_prep,
    write_map_prep,
)

TOY_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"corridor": "A"},
            "geometry": {
                "type": "LineString",
                "coordinates": [[-45.90, -23.20], [-45.89, -23.19]],
            },
        },
        {
            "type": "Feature",
            "properties": {"corridor": "B"},
            "geometry": {
                "type": "LineString",
                "coordinates": [[-45.80, -23.10], [-45.70, -23.00]],
            },
        },
    ],
}


def test_compute_map_prep_centers_on_requested_corridor():
    result = compute_map_prep(TOY_GEOJSON, city="sjc", corridor_id="A", size_km=18.0)
    assert result.corridor_id == "A"
    assert result.west < -45.895 < result.east
    assert result.south < -23.195 < result.north
    assert result.warning is None


def test_compute_map_prep_unknown_corridor_raises():
    with pytest.raises(PrepareMapError, match="available"):
        compute_map_prep(TOY_GEOJSON, city="sjc", corridor_id="Z")


def test_compute_map_prep_warns_when_tile_too_big():
    result = compute_map_prep(TOY_GEOJSON, city="sjc", corridor_id="A", size_km=40.0)
    assert result.warning is not None
    assert str(CS1_MAX_TILE_KM) in result.warning or f"{40.0:g}" in result.warning


def test_compute_map_prep_warns_when_corridor_does_not_fit_tile():
    # B spans roughly 11 km east-west and 11 km north-south; a 1 km tile can't hold it.
    result = compute_map_prep(TOY_GEOJSON, city="sjc", corridor_id="B", size_km=1.0)
    assert result.warning is not None
    assert "does not fully fit" in result.warning


def test_compute_map_prep_all_uses_every_feature():
    result = compute_map_prep(TOY_GEOJSON, city="sjc", corridor_id="all", size_km=18.0)
    assert result.corridor_id == "all"


def test_write_map_prep_writes_under_corridor_subdir(tmp_path: Path):
    result = compute_map_prep(TOY_GEOJSON, city="sjc", corridor_id="A", size_km=18.0)
    out_path = write_map_prep(result, tmp_path)
    assert out_path == tmp_path / "sjc" / "a" / "map-prep.md"
    text = out_path.read_text(encoding="utf-8")
    assert "C:S 1 map prep" in text
    assert "Overpass/Cimtographer" in text
