import statistics

import pytest

from arteria.calibration.replication import is_converged, summarize_replications


def test_summarize_replications_matches_hand_computed_values() -> None:
    values = [10.0, 12.0, 11.0, 13.0, 9.0]

    summary = summarize_replications(values)

    assert summary.n_seeds == 5
    assert summary.mean == pytest.approx(statistics.mean(values))
    assert summary.stdev == pytest.approx(statistics.stdev(values))
    assert summary.ci_low < summary.mean < summary.ci_high


def test_summarize_replications_rejects_unsupported_confidence() -> None:
    with pytest.raises(ValueError, match="0.9"):
        summarize_replications([1.0, 2.0], confidence=0.80)


def test_summarize_replications_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        summarize_replications([])


def test_summarize_replications_rejects_single_value() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        summarize_replications([5.0])


def test_is_converged_true_for_a_tight_consistent_series() -> None:
    values = [100.0, 100.1, 99.9, 100.0, 100.05, 99.95, 100.02, 99.98, 100.01, 99.99]

    assert is_converged(values) is True


def test_is_converged_false_for_a_widely_scattered_series() -> None:
    values = [10.0, 90.0, 20.0, 80.0, 5.0, 95.0, 30.0, 70.0, 1.0, 99.0]

    assert is_converged(values) is False


def test_is_converged_mean_zero_with_zero_spread_is_converged() -> None:
    values = [0.0, 0.0, 0.0, 0.0]

    assert is_converged(values) is True


def test_is_converged_mean_zero_with_nonzero_spread_is_not_converged() -> None:
    values = [-5.0, 5.0, -5.0, 5.0]

    assert is_converged(values) is False
