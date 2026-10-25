"""Stochastic replication / confidence-interval helpers (roadmap P4.6).

A calibrated baseline is run with multiple random seeds; this module
summarizes a metric's values across seeds into a mean, spread, and
confidence interval, plus a simple convergence check, so a future
calibration report (P4.7) and the optimizer's replicated runs (P7) can
decide whether enough seeds have been run.

The confidence interval uses the **normal approximation** (a fixed
z-score per confidence level), not the exact Student's-t distribution —
there is no scipy dependency in this project. This makes the interval
informal, not a fully rigorous academic CI; it is only reliable for a
reasonable number of seeds. A future P4.7 report can swap in scipy's
t-distribution if that precision is ever needed.

Observed data stays outside git per ADR 0004; a remote session only
ever exercises these functions against synthetic or hand-crafted values
(ADR 0009).
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence
from math import sqrt

from pydantic import BaseModel

#: Two-sided normal-distribution z-score per supported confidence level.
#: Normal approximation only — see module docstring.
_Z_SCORES: dict[float, float] = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}


class ReplicationSummary(BaseModel):
    n_seeds: int
    mean: float
    stdev: float
    standard_error: float
    confidence: float
    ci_low: float
    ci_high: float


def summarize_replications(
    values: Sequence[float], *, confidence: float = 0.95
) -> ReplicationSummary:
    """Summarize a metric's values across random seeds into mean/spread/CI.

    Uses the normal approximation (see module docstring), not the exact
    Student's-t distribution. `confidence` must be one of the supported
    keys of `_Z_SCORES` (0.90, 0.95, 0.99). Requires at least 2 values.
    """
    if confidence not in _Z_SCORES:
        supported = sorted(_Z_SCORES)
        raise ValueError(f"confidence must be one of {supported}, got {confidence}")
    if len(values) < 2:
        raise ValueError("need at least 2 replications")

    n = len(values)
    mean = statistics.mean(values)
    stdev = statistics.stdev(values)
    standard_error = stdev / sqrt(n)
    z = _Z_SCORES[confidence]
    half_width = z * standard_error
    return ReplicationSummary(
        n_seeds=n,
        mean=mean,
        stdev=stdev,
        standard_error=standard_error,
        confidence=confidence,
        ci_low=mean - half_width,
        ci_high=mean + half_width,
    )


def is_converged(
    values: Sequence[float],
    *,
    confidence: float = 0.95,
    relative_tolerance: float = 0.05,
) -> bool:
    """Whether enough seeds have been run for a stable estimate of the mean.

    Converged when the confidence interval's half-width is within
    `relative_tolerance` of the mean's magnitude. When `mean == 0`, the
    relative check is undefined (would divide by zero); in that case,
    converged only if the half-width is exactly zero.
    """
    summary = summarize_replications(values, confidence=confidence)
    z = _Z_SCORES[confidence]
    half_width = z * summary.standard_error

    if summary.mean == 0:
        return half_width == 0.0
    return half_width <= relative_tolerance * abs(summary.mean)
