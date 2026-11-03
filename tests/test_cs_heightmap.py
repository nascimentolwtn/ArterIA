from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from arteria.cs.heightmap import (
    CS1_MAX_HEIGHT_M,
    HeightmapError,
    build_heightmap,
    fetch_elevation_grid,
    heightmap_image_from_grid,
    write_heightmap,
)


def _flat_query_fn(points):
    return [100.0 for _ in points]


def _by_position_query_fn(points):
    # Elevation == point index, so row/column order is checkable.
    return [float(i) for i in range(len(points))]


def test_fetch_elevation_grid_shape_and_order():
    grid = fetch_elevation_grid(
        west=-46.0,
        south=-23.3,
        east=-45.8,
        north=-23.1,
        grid_size=4,
        query_fn=_by_position_query_fn,
    )
    assert grid.shape == (4, 4)
    # Row-major fill: grid[0, 0] is the first point queried (north-west corner).
    assert grid[0, 0] == 0.0
    assert grid[0, 1] == 1.0
    assert grid[1, 0] == 4.0


def test_fetch_elevation_grid_mismatched_length_raises():
    with pytest.raises(HeightmapError, match="elevations for"):
        fetch_elevation_grid(
            west=-46.0,
            south=-23.3,
            east=-45.8,
            north=-23.1,
            grid_size=4,
            query_fn=lambda pts: [1.0],
        )


def test_heightmap_image_from_grid_scales_to_16_bit_range():
    grid = np.array([[0.0, CS1_MAX_HEIGHT_M], [CS1_MAX_HEIGHT_M / 2, 50.0]])
    image = heightmap_image_from_grid(grid, size_px=8, rotate_180=False)
    assert image.mode == "I;16"
    assert image.size == (8, 8)
    arr = np.array(image)
    assert arr.min() >= 0
    assert arr.max() <= 65535
    # Top-left corner (0 m) stays near the low end; top-right (max_height_m) near the high end.
    assert arr[0, 0] < 5000
    assert arr[0, -1] > 60000


def test_heightmap_image_from_grid_clamps_out_of_range():
    grid = np.array([[-50.0, CS1_MAX_HEIGHT_M * 2]])
    image = heightmap_image_from_grid(grid, size_px=4, rotate_180=False)
    arr = np.array(image)
    assert arr.min() >= 0
    assert arr.max() <= 65535


def test_heightmap_image_from_grid_rotate_180_flips_corners():
    grid = np.array([[0.0, 1000.0], [1000.0, 0.0]])
    plain = np.array(heightmap_image_from_grid(grid, size_px=4, rotate_180=False))
    rotated = np.array(heightmap_image_from_grid(grid, size_px=4, rotate_180=True))
    assert plain[0, 0] == rotated[-1, -1]


def test_build_heightmap_end_to_end_with_fake_query_fn():
    image = build_heightmap(
        west=-46.0,
        south=-23.3,
        east=-45.8,
        north=-23.1,
        user_agent="test",
        grid_size=3,
        size_px=16,
        query_fn=_flat_query_fn,
    )
    assert image.size == (16, 16)
    arr = np.array(image)
    # Flat 100 m everywhere should land at the same scaled value throughout.
    assert arr.min() == arr.max()


def test_write_heightmap_round_trips_16_bit(tmp_path: Path):
    grid = np.array([[0.0, CS1_MAX_HEIGHT_M]])
    image = heightmap_image_from_grid(grid, size_px=4, rotate_180=False)
    out_path = write_heightmap(image, tmp_path / "sub" / "heightmap.png")
    assert out_path.exists()
    reloaded = Image.open(out_path)
    assert reloaded.mode == "I;16"
    assert reloaded.size == (4, 4)
