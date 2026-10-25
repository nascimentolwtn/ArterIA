"""Trip-level evaluation metrics for before/after comparison (roadmap P6.2).

Real SUMO runs write a `tripinfo.xml` with one record per completed trip.
This module turns a sequence of such (already-parsed) trip records into the
aggregate metrics a before/after comparison needs: VHT, VKT, mean and P95
travel time, mean delay, and total waiting time. It does not parse
`tripinfo.xml` itself — that XML-reading glue is future work — so it is
fully testable on synthetic data.

A remote session only ever exercises these functions against synthetic or
hand-crafted trip records, never real SUMO simulation output (ADR 0009).
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence

from pydantic import BaseModel


class TripRecord(BaseModel):
    trip_id: str
    duration: float
    route_length_m: float
    waiting_time: float = 0.0
    time_loss: float = 0.0


class MetricSummary(BaseModel):
    n_trips: int
    vht_hours: float
    vkt_km: float
    mean_travel_time_s: float
    p95_travel_time_s: float
    mean_delay_s: float
    total_waiting_time_s: float


def summarize_trips(trips: Sequence[TripRecord]) -> MetricSummary:
    """Aggregate a sequence of completed-trip records into summary metrics.

    `vht_hours` and `vkt_km` are totals over all trips (vehicle-hours/
    vehicle-kilometers traveled); the rest are per-trip means/percentiles.
    """
    if len(trips) == 0:
        raise ValueError("trips must not be empty")

    durations = [trip.duration for trip in trips]
    route_lengths = [trip.route_length_m for trip in trips]
    waiting_times = [trip.waiting_time for trip in trips]
    time_losses = [trip.time_loss for trip in trips]

    if len(durations) == 1:
        p95_travel_time_s = durations[0]
    else:
        p95_travel_time_s = statistics.quantiles(durations, n=100, method="inclusive")[94]

    return MetricSummary(
        n_trips=len(trips),
        vht_hours=sum(durations) / 3600,
        vkt_km=sum(route_lengths) / 1000,
        mean_travel_time_s=statistics.mean(durations),
        p95_travel_time_s=p95_travel_time_s,
        mean_delay_s=statistics.mean(time_losses),
        total_waiting_time_s=sum(waiting_times),
    )
