"""Calibration report rendering, per city and time window (roadmap P4.7).

Renders the metric primitives from `goodness_of_fit.py` (GEH, travel-time
RMSE/MAPE) and `replication.py` (per-seed mean/spread/CI) into one Markdown
report. This module does no simulation and computes no new statistics of
its own beyond calling `arteria.calibration.replication.is_converged` on
raw per-seed values when they are supplied — it only formats what those two
modules already produced.

Convergence design call: `CalibrationReportInput` carries an optional
`raw_replications` map (metric name -> per-seed values) alongside the
required `replications` map (metric name -> precomputed `ReplicationSummary`).
When a metric's raw values are present, `render_calibration_report` calls
`is_converged` on them on demand, at the same `confidence` level the
summary was built with; a metric with no raw values renders as "unknown"
rather than guessing. This was chosen over requiring a precomputed boolean
flag so the convergence verdict can never drift from the `ReplicationSummary`
it is reported alongside.

Observed data (counts, travel times) stays outside git per ADR 0004; a
remote session only ever exercises these functions against synthetic or
hand-crafted values (ADR 0009). The rendered report always carries that
caveat forward, since a report is exactly the kind of artifact that could
otherwise be mistaken for a real finding.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from arteria.calibration.goodness_of_fit import GEH_PASS_SHARE, CalibrationFitSummary
from arteria.calibration.replication import ReplicationSummary, is_converged

DISCLAIMER = (
    "> **Disclaimer.** Numbers in this report are only as real as the data that "
    "produced them. Observed data (counts, travel times) stays outside git per "
    "ADR 0004; a remote session only ever exercises these functions against "
    "synthetic or hand-crafted values (ADR 0009). Figures produced from toy, "
    "synthetic, or fixture data in a remote session are test data, never a "
    "finding, and must never back a recommendation in the thesis or the policy "
    "report. Only a real desk-run calibration, backed by a run-provenance "
    "manifest (P0.7), counts as evidence."
)

CI_CAVEAT = (
    "> Confidence intervals above use the **normal approximation** (a fixed "
    "z-score per confidence level), not the exact Student's-t distribution — "
    "see `arteria/calibration/replication.py`. Treat them as informal, not a "
    "fully rigorous academic CI."
)


class CalibrationReportInput(BaseModel):
    city: str
    time_window: str
    fit: CalibrationFitSummary
    replications: dict[str, ReplicationSummary] = Field(default_factory=dict)
    raw_replications: dict[str, list[float]] = Field(default_factory=dict)
    notes: str | None = None


def _render_geh_section(fit: CalibrationFitSummary) -> str:
    geh = fit.geh
    verdict = "PASS" if fit.meets_geh_threshold else "FAIL"
    return "\n".join(
        [
            "## GEH (link volumes)",
            "",
            f"- Link count: {geh.link_count}",
            f"- Passing count: {geh.passing_count} / {geh.link_count} "
            f"({geh.passing_share:.1%})",
            f"- Worst GEH: {geh.worst_geh:.2f}",
            f"- **Result: {verdict}** (convention: GEH < 5 on >= "
            f"{GEH_PASS_SHARE:.0%} of links)",
        ]
    )


def _render_travel_time_section(fit: CalibrationFitSummary) -> str:
    return "\n".join(
        [
            "## Travel time",
            "",
            f"- RMSE: {fit.travel_time_rmse:.2f} s",
            f"- MAPE: {fit.travel_time_mape:.1%}",
        ]
    )


def _render_replication_section(report_input: CalibrationReportInput) -> str:
    if not report_input.replications:
        return ""

    rows = [
        "## Replications",
        "",
        "| Metric | Seeds | Mean | Stdev | CI | Confidence | Converged |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, summary in report_input.replications.items():
        raw_values = report_input.raw_replications.get(name)
        if raw_values is not None:
            converged = "yes" if is_converged(raw_values, confidence=summary.confidence) else "no"
        else:
            converged = "unknown"
        rows.append(
            f"| {name} | {summary.n_seeds} | {summary.mean:.3f} | {summary.stdev:.3f} "
            f"| [{summary.ci_low:.3f}, {summary.ci_high:.3f}] | {summary.confidence:.0%} "
            f"| {converged} |"
        )
    rows.append("")
    rows.append(CI_CAVEAT)
    return "\n".join(rows)


def render_calibration_report(report_input: CalibrationReportInput) -> str:
    """Render a `CalibrationReportInput` into a Markdown calibration report."""
    sections = [
        f"# Calibration report: {report_input.city} ({report_input.time_window})",
        "",
        DISCLAIMER,
        "",
        _render_geh_section(report_input.fit),
        "",
        _render_travel_time_section(report_input.fit),
        "",
    ]

    replication_section = _render_replication_section(report_input)
    if replication_section:
        sections.append(replication_section)
        sections.append("")

    if report_input.notes:
        sections.append("## Notes")
        sections.append("")
        sections.append(report_input.notes)
        sections.append("")

    return "\n".join(sections)


def write_calibration_report(report_input: CalibrationReportInput, path: Path) -> Path:
    """Render `report_input` and write it to `path`, creating parent directories."""
    markdown = render_calibration_report(report_input)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown)
    return path
