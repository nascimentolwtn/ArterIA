import statistics

import pytest

from arteria.evaluate.metrics import MetricSummary, TripRecord, summarize_trips


def test_summarize_trips_matches_hand_computed_values() -> None:
    trips = [
        TripRecord(
            trip_id="a", duration=100.0, route_length_m=1000.0, waiting_time=5.0, time_loss=10.0
        ),
        TripRecord(
            trip_id="b", duration=200.0, route_length_m=2000.0, waiting_time=15.0, time_loss=20.0
        ),
        TripRecord(
            trip_id="c", duration=300.0, route_length_m=3000.0, waiting_time=25.0, time_loss=30.0
        ),
    ]

    summary = summarize_trips(trips)

    assert summary.n_trips == 3
    assert summary.vht_hours == pytest.approx((100.0 + 200.0 + 300.0) / 3600)
    assert summary.vkt_km == pytest.approx((1000.0 + 2000.0 + 3000.0) / 1000)
    assert summary.mean_travel_time_s == pytest.approx((100.0 + 200.0 + 300.0) / 3)
    assert summary.mean_delay_s == pytest.approx((10.0 + 20.0 + 30.0) / 3)
    assert summary.total_waiting_time_s == pytest.approx(5.0 + 15.0 + 25.0)


def test_statistics_quantiles_inclusive_index_94_is_the_p95_cut_point() -> None:
    # Sanity-check the statistics.quantiles semantics this module relies on,
    # against a known sorted series, before trusting it in summarize_trips.
    data = list(range(1, 21))  # 1..20

    quantiles = statistics.quantiles(data, n=100, method="inclusive")

    assert len(quantiles) == 99
    # Index 94 is the 95th percentile cut point (quantiles[k-1] == the k-th
    # of the n-1 cut points, i.e. index 94 == the 95th of 99 cuts).
    p95 = quantiles[94]
    assert 19.0 < p95 < 20.0


def test_summarize_trips_p95_for_1_to_20_durations() -> None:
    trips = [
        TripRecord(trip_id=str(i), duration=float(i), route_length_m=0.0)
        for i in range(1, 21)
    ]

    summary = summarize_trips(trips)

    expected_p95 = statistics.quantiles(
        [float(i) for i in range(1, 21)], n=100, method="inclusive"
    )[94]
    assert summary.p95_travel_time_s == pytest.approx(expected_p95)
    # Near the top of the 1..20 range, as expected for a 95th percentile.
    assert 19.0 < summary.p95_travel_time_s < 20.0


def test_summarize_trips_p95_for_single_trip_is_that_trips_duration() -> None:
    trips = [TripRecord(trip_id="only", duration=42.0, route_length_m=500.0)]

    summary = summarize_trips(trips)

    assert summary.n_trips == 1
    assert summary.p95_travel_time_s == 42.0
    assert summary.mean_travel_time_s == 42.0


def test_summarize_trips_rejects_empty_sequence() -> None:
    with pytest.raises(ValueError, match="not be empty"):
        summarize_trips([])


def test_summarize_trips_n_trips_matches_input_length() -> None:
    trips = [
        TripRecord(trip_id=str(i), duration=float(i), route_length_m=float(i) * 10)
        for i in range(1, 8)
    ]

    summary = summarize_trips(trips)

    assert summary.n_trips == len(trips)
    assert isinstance(summary, MetricSummary)
