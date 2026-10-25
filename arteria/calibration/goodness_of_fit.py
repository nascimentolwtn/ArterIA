"""Goodness-of-fit metrics for calibration (roadmap P4.5).

Standard calibration metrics comparing modeled traffic to observed
counts/travel times: the GEH statistic (link volumes) and RMSE/MAPE
(travel times). These are metric primitives only — the HTML calibration
report (P4.7) that renders them per city/time-window lands separately.

Observed data (counts, travel times) stays outside git per ADR 0004; a
remote session only ever exercises these functions against synthetic or
hand-crafted values (ADR 0009).
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from pydantic import BaseModel

GEH_THRESHOLD = 5.0
GEH_PASS_SHARE = 0.85


def geh(modeled: float, observed: float) -> float:
    """The GEH statistic for one link: `sqrt(2*(M-C)^2/(M+C))`.

    Both zero (no modeled or observed volume on the link) is treated as a
    perfect match (GEH = 0) rather than a division by zero.
    """
    total = modeled + observed
    if total == 0:
        return 0.0
    return math.sqrt(2 * (modeled - observed) ** 2 / total)


class GehSummary(BaseModel):
    link_count: int
    passing_count: int
    passing_share: float
    worst_geh: float

    @property
    def meets_threshold(self) -> bool:
        """Whether the standard acceptance convention (GEH < 5 on >= 85% of links) holds."""
        return self.passing_share >= GEH_PASS_SHARE


def summarize_geh(
    modeled: Sequence[float],
    observed: Sequence[float],
    *,
    threshold: float = GEH_THRESHOLD,
) -> GehSummary:
    """Per-link GEH over paired modeled/observed volumes, with pass/fail counts.

    `modeled` and `observed` must be the same length and link-aligned (same
    order); a link's GEH value "passes" when it is strictly below `threshold`.
    """
    if len(modeled) != len(observed):
        raise ValueError("modeled and observed must have the same length")
    if len(modeled) == 0:
        raise ValueError("modeled and observed must not be empty")

    values = [geh(m, o) for m, o in zip(modeled, observed, strict=True)]
    link_count = len(values)
    passing_count = sum(1 for v in values if v < threshold)
    return GehSummary(
        link_count=link_count,
        passing_count=passing_count,
        passing_share=passing_count / link_count,
        worst_geh=max(values),
    )


def travel_time_rmse(modeled: Sequence[float], observed: Sequence[float]) -> float:
    """Root-mean-square error between modeled and observed travel times."""
    if len(modeled) != len(observed):
        raise ValueError("modeled and observed must have the same length")
    if len(modeled) == 0:
        raise ValueError("modeled and observed must not be empty")

    squared_errors = [(m - o) ** 2 for m, o in zip(modeled, observed, strict=True)]
    return math.sqrt(sum(squared_errors) / len(squared_errors))


def travel_time_mape(modeled: Sequence[float], observed: Sequence[float]) -> float:
    """Mean absolute percentage error between modeled and observed travel times.

    Expressed as a fraction (0.1 == 10%), not multiplied by 100. Every
    `observed` value must be non-zero — a zero observed travel time has no
    well-defined percentage error.
    """
    if len(modeled) != len(observed):
        raise ValueError("modeled and observed must have the same length")
    if len(modeled) == 0:
        raise ValueError("modeled and observed must not be empty")
    if any(o == 0 for o in observed):
        raise ValueError("observed travel times must be non-zero to compute a percentage error")

    percentage_errors = [
        abs(m - o) / o for m, o in zip(modeled, observed, strict=True)
    ]
    return sum(percentage_errors) / len(percentage_errors)


class CalibrationFitSummary(BaseModel):
    geh: GehSummary
    travel_time_rmse: float
    travel_time_mape: float

    @property
    def meets_geh_threshold(self) -> bool:
        return self.geh.meets_threshold


def summarize_calibration_fit(
    *,
    modeled_volumes: Sequence[float],
    observed_volumes: Sequence[float],
    modeled_travel_times: Sequence[float],
    observed_travel_times: Sequence[float],
    geh_threshold: float = GEH_THRESHOLD,
) -> CalibrationFitSummary:
    """Combine link-volume GEH and travel-time RMSE/MAPE into one fit summary.

    Volumes and travel times are independent paired series (they may cover
    different links/routes, and need not be the same length as each other)
    — this is the shape a future P4.7 report would read to decide whether a
    baseline meets the calibration thresholds (ADR 0005).
    """
    return CalibrationFitSummary(
        geh=summarize_geh(modeled_volumes, observed_volumes, threshold=geh_threshold),
        travel_time_rmse=travel_time_rmse(modeled_travel_times, observed_travel_times),
        travel_time_mape=travel_time_mape(modeled_travel_times, observed_travel_times),
    )
