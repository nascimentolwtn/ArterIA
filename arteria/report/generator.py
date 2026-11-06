"""Before/after report generation for stakeholders (roadmap P6.6 / R11).

Turns a pair of `MetricSummary` objects (see `arteria/evaluate/metrics.py`)
into Markdown reports: a single-package before/after table with a narrative
callout, and a multi-package portfolio ranking. Maps and charts are out of
scope here — no plotting/GUI library is available remotely (ADR 0009) — so
only the tables half of P6.6 lands in this module; a future desk session
can add the visual half.

A remote session only ever has synthetic or hand-crafted `MetricSummary`
inputs to render, never real SUMO simulation output (ADR 0009), so every
report this module produces carries that caveat in its closing disclaimer
rather than presenting the numbers as evidence for a real recommendation.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from arteria.evaluate.metrics import MetricSummary

#: Fields where a *decrease* is the improvement direction (travel time,
#: delay, waiting time, and vehicle-hours/kilometers traveled). `n_trips` is
#: a volume count, not a performance metric with a fixed good/bad direction,
#: so it is intentionally left out of this convention and never called out
#: as an improvement or regression in the narrative text.
_LOWER_IS_BETTER = {
    "vht_hours",
    "vkt_km",
    "mean_travel_time_s",
    "p95_travel_time_s",
    "mean_delay_s",
    "total_waiting_time_s",
}

_DISCLAIMER = (
    "**Caveat:** these figures are illustrative/synthetic unless this report "
    "was explicitly built from a real, manifest-backed desk run (see ADR "
    "0009). A remote session never has real SUMO simulation output to draw "
    "on, so the numbers above are not evidence for an actual street-network "
    "recommendation."
)


class MetricDelta(BaseModel):
    field: str
    baseline: float
    scenario: float
    delta: float
    percent_change: float | None


def compare_metrics(baseline: MetricSummary, scenario: MetricSummary) -> list[MetricDelta]:
    """Compare every `MetricSummary` field between a baseline and a scenario.

    One `MetricDelta` per field, in `MetricSummary`'s declared order.
    `delta = scenario - baseline`; `percent_change = delta / baseline` when
    `baseline != 0`, else `None` (percent change is undefined there, not a
    divide-by-zero crash).
    """
    deltas = []
    for name in MetricSummary.model_fields:
        baseline_value = float(getattr(baseline, name))
        scenario_value = float(getattr(scenario, name))
        delta = scenario_value - baseline_value
        percent_change = delta / baseline_value if baseline_value != 0 else None
        deltas.append(
            MetricDelta(
                field=name,
                baseline=baseline_value,
                scenario=scenario_value,
                delta=delta,
                percent_change=percent_change,
            )
        )
    return deltas


def _format_percent(percent_change: float | None) -> str:
    if percent_change is None:
        return "n/a"
    return f"{percent_change * 100:+.1f}%"


def _format_number(value: float) -> str:
    return f"{value:,.2f}"


def _largest_relative_mover(
    deltas: list[MetricDelta], *, improvement: bool
) -> MetricDelta | None:
    """The largest-magnitude relative mover in the requested direction, if any.

    `improvement=True` picks the biggest relative improvement (a decrease on
    a `_LOWER_IS_BETTER` field); `improvement=False` picks the biggest
    relative regression (an increase on one of those fields). Fields outside
    `_LOWER_IS_BETTER`, or with an undefined (`None`) percent change, are not
    candidates — there is nothing sensible to call "better" or "worse" there.
    """
    candidates = [
        d
        for d in deltas
        if d.field in _LOWER_IS_BETTER
        and d.percent_change is not None
        and ((d.percent_change < 0) if improvement else (d.percent_change > 0))
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda d: abs(d.percent_change or 0.0))


def _narrative(deltas: list[MetricDelta]) -> str:
    best = _largest_relative_mover(deltas, improvement=True)
    worst = _largest_relative_mover(deltas, improvement=False)

    sentences = []
    if best is not None:
        sentences.append(
            f"The largest improvement is in `{best.field}`, down "
            f"{_format_percent(best.percent_change)} from baseline."
        )
    else:
        sentences.append("No tracked metric improved over the baseline.")

    if worst is not None:
        sentences.append(
            f"The largest regression is in `{worst.field}`, up "
            f"{_format_percent(worst.percent_change)} from baseline."
        )
    else:
        sentences.append("No tracked metric moved in the wrong direction.")

    return " ".join(sentences)


def render_before_after_report(
    *, package_name: str, baseline: MetricSummary, scenario: MetricSummary
) -> str:
    """Render a Markdown before/after report for one intervention package.

    Includes a per-field comparison table, a narrative paragraph calling out
    the largest relative improvement and regression (see `_LOWER_IS_BETTER`
    for the improvement-direction convention), and the standard synthetic-
    data disclaimer.
    """
    deltas = compare_metrics(baseline, scenario)

    rows = [
        f"| {d.field} | {_format_number(d.baseline)} | {_format_number(d.scenario)} | "
        f"{_format_number(d.delta)} | {_format_percent(d.percent_change)} |"
        for d in deltas
    ]

    lines = [
        f"# Before/After Report: {package_name}",
        "",
        "| Metric | Baseline | Scenario | Delta | % Change |",
        "| --- | --- | --- | --- | --- |",
        *rows,
        "",
        _narrative(deltas),
        "",
        _DISCLAIMER,
    ]
    return "\n".join(lines) + "\n"


def render_portfolio_report(
    baseline: MetricSummary, scenarios: dict[str, MetricSummary]
) -> str:
    """Render a Markdown report ranking several packages against one baseline.

    Packages are ranked by `mean_travel_time_s` improvement, best (biggest
    reduction) first; each row also shows the `vht_hours` delta/percent
    change as a second headline column. Raises `ValueError` if `scenarios`
    is empty.
    """
    if not scenarios:
        raise ValueError("scenarios must not be empty")

    ranked = sorted(
        scenarios.items(),
        key=lambda item: item[1].mean_travel_time_s - baseline.mean_travel_time_s,
    )

    rows = []
    for package_name, scenario in ranked:
        by_field = {d.field: d for d in compare_metrics(baseline, scenario)}
        travel_time = by_field["mean_travel_time_s"]
        vht = by_field["vht_hours"]
        rows.append(
            f"| {package_name} | {_format_number(travel_time.delta)} | "
            f"{_format_percent(travel_time.percent_change)} | {_format_number(vht.delta)} | "
            f"{_format_percent(vht.percent_change)} |"
        )

    lines = [
        "# Portfolio Comparison Report",
        "",
        "Ranked by mean travel time improvement (largest reduction first).",
        "",
        "| Package | Mean Travel Time Δ (s) | % Change | VHT Δ (hours) | % Change |",
        "| --- | --- | --- | --- | --- |",
        *rows,
        "",
        _DISCLAIMER,
    ]
    return "\n".join(lines) + "\n"


def write_report(markdown: str, path: Path) -> Path:
    """Write a rendered Markdown report to `path`, creating parent directories.

    Per `docs/roadmap.md`'s R11 convention, only reports committed under
    `results/published/` are treated as published, and only after owner
    review — this function writes wherever it is told and does not enforce
    or check that convention itself.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    return path
