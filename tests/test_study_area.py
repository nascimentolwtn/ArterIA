from pathlib import Path

import pytest
from shapely.geometry import shape

from arteria.network.study_area import (
    StudyAreaConfig,
    build_study_areas,
    hull_buffer_polygon,
    load_study_area_config,
)

REPO_ROOT = Path(__file__).parent.parent
SJC_STUDY_AREAS = REPO_ROOT / "cities" / "sjc" / "study-areas.yaml"

UTM_23S = "EPSG:32723"  # matches cities/sjc/city.yaml's crs

# Roughly central São José dos Campos, far enough apart to form a real hull.
SJC_POINT_A = (-45.8872, -23.1791)
SJC_POINT_B = (-45.8650, -23.2000)
SJC_POINT_C = (-45.9000, -23.1950)


def test_hull_buffer_polygon_contains_all_input_points():
    geometry = hull_buffer_polygon(
        [SJC_POINT_A, SJC_POINT_B, SJC_POINT_C], buffer_m=300, projected_crs=UTM_23S
    )
    polygon = shape(geometry)
    assert polygon.is_valid
    for lon, lat in (SJC_POINT_A, SJC_POINT_B, SJC_POINT_C):
        assert polygon.contains(shape({"type": "Point", "coordinates": [lon, lat]}))


def test_hull_buffer_polygon_grows_with_buffer_distance():
    small = shape(hull_buffer_polygon([SJC_POINT_A, SJC_POINT_B], 100, UTM_23S))
    large = shape(hull_buffer_polygon([SJC_POINT_A, SJC_POINT_B], 1000, UTM_23S))
    assert large.area > small.area
    assert large.contains(small)


def test_hull_buffer_polygon_degenerates_gracefully_for_a_single_point():
    geometry = hull_buffer_polygon([SJC_POINT_A], buffer_m=200, projected_crs=UTM_23S)
    polygon = shape(geometry)
    assert polygon.is_valid
    assert polygon.area > 0
    assert polygon.contains(shape({"type": "Point", "coordinates": SJC_POINT_A}))


def test_hull_buffer_polygon_rejects_no_points():
    with pytest.raises(ValueError):
        hull_buffer_polygon([], buffer_m=100, projected_crs=UTM_23S)


def test_build_study_areas_skips_disabled_candidates_by_default():
    config = StudyAreaConfig.model_validate(
        {
            "candidates": [
                {"id": "x", "name": "X", "queries": ["a"], "buffer_m": 100},
                {"id": "y", "name": "Y", "queries": ["b"], "buffer_m": 100, "enabled": False},
            ]
        }
    )
    fixture_geocoder = {"a": SJC_POINT_A, "b": SJC_POINT_B}
    result = build_study_areas(
        config, lambda q: fixture_geocoder[q], projected_crs=UTM_23S
    )
    ids = [f["properties"]["id"] for f in result["features"]]
    assert ids == ["x"]


def test_build_study_areas_includes_disabled_when_asked():
    config = StudyAreaConfig.model_validate(
        {
            "candidates": [
                {"id": "x", "name": "X", "queries": ["a"], "buffer_m": 100, "enabled": False},
            ]
        }
    )
    fixture_geocoder = {"a": SJC_POINT_A}
    result = build_study_areas(
        config, lambda q: fixture_geocoder[q], projected_crs=UTM_23S, include_disabled=True
    )
    assert [f["properties"]["id"] for f in result["features"]] == ["x"]


def test_sjc_study_areas_yaml_loads_and_has_the_four_priority_candidates():
    config = load_study_area_config(SJC_STUDY_AREAS)
    enabled_ids_by_priority = sorted(
        (c.priority, c.id) for c in config.candidates if c.enabled
    )
    assert [cid for _, cid in enabled_ids_by_priority] == ["b", "d", "c", "a"]
    disabled = [c for c in config.candidates if not c.enabled]
    assert [c.id for c in disabled] == ["b_ext_vista_verde"]
