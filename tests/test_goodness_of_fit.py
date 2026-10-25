import math

import pytest

from arteria.calibration.goodness_of_fit import (
    geh,
    summarize_calibration_fit,
    summarize_geh,
    travel_time_mape,
    travel_time_rmse,
)


def test_geh_is_zero_for_a_perfect_match() -> None:
    assert geh(100.0, 100.0) == 0.0


def test_geh_zero_and_zero_is_a_perfect_match_not_a_division_error() -> None:
    assert geh(0.0, 0.0) == 0.0


def test_geh_matches_hand_computed_value() -> None:
    # GEH(110, 100) = sqrt(2*(10)^2/210) = sqrt(200/210)
    assert geh(110.0, 100.0) == pytest.approx(math.sqrt(200 / 210))


def test_summarize_geh_small_deviation_passes_threshold() -> None:
    modeled = [100.0, 200.0, 300.0]
    observed = [102.0, 198.0, 305.0]

    summary = summarize_geh(modeled, observed)

    assert summary.link_count == 3
    assert summary.passing_count == 3
    assert summary.passing_share == 1.0
    assert summary.meets_threshold is True


def test_summarize_geh_large_deviation_fails_threshold() -> None:
    modeled = [100.0, 100.0, 100.0, 100.0]
    observed = [100.0, 100.0, 100.0, 1000.0]

    summary = summarize_geh(modeled, observed)

    assert summary.link_count == 4
    assert summary.passing_count == 3
    assert summary.passing_share == 0.75
    assert summary.meets_threshold is False  # below the 85% convention
    assert summary.worst_geh > 5.0


def test_summarize_geh_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        summarize_geh([1.0, 2.0], [1.0])


def test_summarize_geh_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="not be empty"):
        summarize_geh([], [])


def test_travel_time_rmse_is_zero_for_a_perfect_match() -> None:
    assert travel_time_rmse([60.0, 90.0], [60.0, 90.0]) == 0.0


def test_travel_time_rmse_matches_hand_computed_value() -> None:
    # errors: 10, -10 -> squared: 100, 100 -> mean 100 -> sqrt 10
    assert travel_time_rmse([70.0, 80.0], [60.0, 90.0]) == pytest.approx(10.0)


def test_travel_time_mape_matches_hand_computed_value() -> None:
    # |70-60|/60 = 1/6, |90-100|/100 = 0.1 -> mean = (1/6 + 0.1) / 2
    expected = (abs(70.0 - 60.0) / 60.0 + abs(90.0 - 100.0) / 100.0) / 2
    assert travel_time_mape([70.0, 90.0], [60.0, 100.0]) == pytest.approx(expected)


def test_travel_time_mape_rejects_zero_observed() -> None:
    with pytest.raises(ValueError, match="non-zero"):
        travel_time_mape([10.0], [0.0])


def test_summarize_calibration_fit_combines_volume_and_travel_time_metrics() -> None:
    summary = summarize_calibration_fit(
        modeled_volumes=[100.0, 200.0],
        observed_volumes=[102.0, 198.0],
        modeled_travel_times=[70.0, 80.0],
        observed_travel_times=[60.0, 90.0],
    )

    assert summary.geh.link_count == 2
    assert summary.meets_geh_threshold is True
    assert summary.travel_time_rmse == pytest.approx(10.0)
    assert summary.travel_time_mape > 0.0
