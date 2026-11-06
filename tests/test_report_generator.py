from pathlib import Path

import pytest

from arteria.evaluate.metrics import MetricSummary, TripRecord, summarize_trips
from arteria.report.generator import (
    compare_metrics,
    render_before_after_report,
    render_portfolio_report,
    write_report,
)


def _trip(
    trip_id: str, duration: float, route_length_m: float, waiting_time: float, time_loss: float
) -> TripRecord:
    return TripRecord(
        trip_id=trip_id,
        duration=duration,
        route_length_m=route_length_m,
        waiting_time=waiting_time,
        time_loss=time_loss,
    )


_BASELINE_TRIPS = [
    _trip("b1", 120.0, 1000.0, 20.0, 15.0),
    _trip("b2", 140.0, 1200.0, 25.0, 18.0),
    _trip("b3", 160.0, 1400.0, 30.0, 22.0),
]

_BETTER_TRIPS = [
    _trip("s1", 90.0, 1000.0, 10.0, 8.0),
    _trip("s2", 100.0, 1200.0, 12.0, 9.0),
    _trip("s3", 110.0, 1400.0, 14.0, 10.0),
]

_WORSE_TRIPS = [
    _trip("w1", 200.0, 1000.0, 50.0, 40.0),
    _trip("w2", 220.0, 1200.0, 55.0, 45.0),
    _trip("w3", 240.0, 1400.0, 60.0, 50.0),
]


@pytest.fixture
def baseline() -> MetricSummary:
    return summarize_trips(_BASELINE_TRIPS)


@pytest.fixture
def better_scenario() -> MetricSummary:
    return summarize_trips(_BETTER_TRIPS)


@pytest.fixture
def worse_scenario() -> MetricSummary:
    return summarize_trips(_WORSE_TRIPS)


def test_compare_metrics_computes_delta_and_percent_change(
    baseline: MetricSummary, better_scenario: MetricSummary
) -> None:
    deltas = compare_metrics(baseline, better_scenario)
    by_field = {d.field: d for d in deltas}

    assert set(by_field) == set(MetricSummary.model_fields)

    tt = by_field["mean_travel_time_s"]
    assert tt.baseline == pytest.approx(baseline.mean_travel_time_s)
    assert tt.scenario == pytest.approx(better_scenario.mean_travel_time_s)
    expected_delta = better_scenario.mean_travel_time_s - baseline.mean_travel_time_s
    assert tt.delta == pytest.approx(expected_delta)
    assert tt.delta < 0
    assert tt.percent_change == pytest.approx(tt.delta / tt.baseline)


def test_compare_metrics_zero_baseline_gives_none_percent_change() -> None:
    baseline = MetricSummary(
        n_trips=1,
        vht_hours=1.0,
        vkt_km=1.0,
        mean_travel_time_s=100.0,
        p95_travel_time_s=100.0,
        mean_delay_s=0.0,
        total_waiting_time_s=0.0,
    )
    scenario = MetricSummary(
        n_trips=1,
        vht_hours=1.0,
        vkt_km=1.0,
        mean_travel_time_s=90.0,
        p95_travel_time_s=90.0,
        mean_delay_s=5.0,
        total_waiting_time_s=0.0,
    )

    deltas = compare_metrics(baseline, scenario)
    by_field = {d.field: d for d in deltas}

    delay = by_field["mean_delay_s"]
    assert delay.baseline == 0.0
    assert delay.delta == pytest.approx(5.0)
    assert delay.percent_change is None

    waiting = by_field["total_waiting_time_s"]
    assert waiting.baseline == 0.0
    assert waiting.delta == pytest.approx(0.0)
    assert waiting.percent_change is None


def test_render_before_after_report_better_scenario_calls_out_improvement(
    baseline: MetricSummary, better_scenario: MetricSummary
) -> None:
    report = render_before_after_report(
        package_name="Downtown bus lane", baseline=baseline, scenario=better_scenario
    )

    assert "# Before/After Report: Downtown bus lane" in report
    assert "mean_travel_time_s" in report
    assert f"{baseline.mean_travel_time_s:,.2f}" in report
    assert f"{better_scenario.mean_travel_time_s:,.2f}" in report
    # total_waiting_time_s has the largest relative drop in this fixture.
    assert "largest improvement is in `total_waiting_time_s`" in report
    assert "No tracked metric moved in the wrong direction." in report
    assert "ADR 0009" in report


def test_render_before_after_report_worse_scenario_calls_out_regression(
    baseline: MetricSummary, worse_scenario: MetricSummary
) -> None:
    report = render_before_after_report(
        package_name="Bad conversion", baseline=baseline, scenario=worse_scenario
    )

    assert "# Before/After Report: Bad conversion" in report
    # mean_delay_s has the largest relative rise in this fixture.
    assert "largest regression is in `mean_delay_s`" in report
    assert "No tracked metric improved over the baseline." in report


def test_render_portfolio_report_ranks_best_package_first(
    baseline: MetricSummary, better_scenario: MetricSummary, worse_scenario: MetricSummary
) -> None:
    report = render_portfolio_report(
        baseline, {"Worse package": worse_scenario, "Better package": better_scenario}
    )

    better_pos = report.index("Better package")
    worse_pos = report.index("Worse package")
    assert better_pos < worse_pos
    # headline columns are human-labeled, not raw field names
    assert "mean_travel_time_s" not in report
    assert "ADR 0009" in report


def test_render_portfolio_report_rejects_empty_scenarios(baseline: MetricSummary) -> None:
    with pytest.raises(ValueError, match="not be empty"):
        render_portfolio_report(baseline, {})


def test_write_report_writes_exact_contents(tmp_path: Path) -> None:
    markdown = "# Some Report\n\nhello\n"
    target = tmp_path / "nested" / "report.md"

    result = write_report(markdown, target)

    assert result == target
    assert target.read_text(encoding="utf-8") == markdown
