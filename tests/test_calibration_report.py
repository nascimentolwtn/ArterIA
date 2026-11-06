from pathlib import Path

from arteria.calibration.goodness_of_fit import summarize_calibration_fit
from arteria.calibration.replication import summarize_replications
from arteria.calibration.report import (
    CalibrationReportInput,
    render_calibration_report,
    write_calibration_report,
)

PASSING_FIT = summarize_calibration_fit(
    modeled_volumes=[100.0, 200.0, 300.0],
    observed_volumes=[102.0, 198.0, 305.0],
    modeled_travel_times=[120.0, 240.0, 360.0],
    observed_travel_times=[110.0, 250.0, 340.0],
)

FAILING_FIT = summarize_calibration_fit(
    modeled_volumes=[100.0, 100.0, 100.0, 100.0],
    observed_volumes=[100.0, 100.0, 100.0, 1000.0],
    modeled_travel_times=[120.0, 240.0, 360.0],
    observed_travel_times=[110.0, 250.0, 340.0],
)


def test_render_passing_report_has_pass_verdict_and_key_figures() -> None:
    report_input = CalibrationReportInput(
        city="Sao Jose dos Campos",
        time_window="AM peak",
        fit=PASSING_FIT,
    )

    markdown = render_calibration_report(report_input)

    assert "Sao Jose dos Campos" in markdown
    assert "AM peak" in markdown
    assert "**Result: PASS**" in markdown
    assert f"{PASSING_FIT.travel_time_rmse:.2f} s" in markdown
    assert f"{PASSING_FIT.travel_time_mape:.1%}" in markdown
    assert "%" in markdown.split("MAPE:")[1].splitlines()[0]


def test_render_failing_report_has_fail_verdict() -> None:
    report_input = CalibrationReportInput(
        city="Sao Jose dos Campos",
        time_window="PM peak",
        fit=FAILING_FIT,
    )

    markdown = render_calibration_report(report_input)

    assert "**Result: FAIL**" in markdown
    assert str(FAILING_FIT.geh.passing_count) in markdown


def test_mape_is_rendered_as_a_percentage_not_a_raw_fraction() -> None:
    report_input = CalibrationReportInput(
        city="City",
        time_window="window",
        fit=PASSING_FIT,
    )

    markdown = render_calibration_report(report_input)

    assert f"{PASSING_FIT.travel_time_mape * 100:.1f}%" in markdown
    raw_fraction = f"{PASSING_FIT.travel_time_mape:.4f}"
    assert raw_fraction not in markdown


def test_replication_section_renders_mean_stdev_ci_and_confidence() -> None:
    seeds_converged = [100.0, 101.0, 99.5, 100.5, 100.2]
    seeds_not_converged = [50.0, 150.0, 20.0, 180.0]

    converged_summary = summarize_replications(seeds_converged, confidence=0.95)
    not_converged_summary = summarize_replications(seeds_not_converged, confidence=0.95)

    report_input = CalibrationReportInput(
        city="City",
        time_window="window",
        fit=PASSING_FIT,
        replications={
            "mean_travel_time_s": converged_summary,
            "mean_delay_s": not_converged_summary,
        },
        raw_replications={
            "mean_travel_time_s": seeds_converged,
            "mean_delay_s": seeds_not_converged,
        },
    )

    markdown = render_calibration_report(report_input)

    assert "mean_travel_time_s" in markdown
    assert "mean_delay_s" in markdown
    assert f"{converged_summary.mean:.3f}" in markdown
    assert f"{converged_summary.stdev:.3f}" in markdown
    assert f"{converged_summary.ci_low:.3f}" in markdown
    assert f"{converged_summary.ci_high:.3f}" in markdown
    assert "95%" in markdown
    assert "| yes |" in markdown
    assert "| no |" in markdown
    assert "normal approximation" in markdown
    assert "Student's-t" in markdown


def test_replication_without_raw_values_renders_unknown_convergence() -> None:
    summary = summarize_replications([1.0, 2.0, 3.0], confidence=0.90)
    report_input = CalibrationReportInput(
        city="City",
        time_window="window",
        fit=PASSING_FIT,
        replications={"some_metric": summary},
    )

    markdown = render_calibration_report(report_input)

    assert "| unknown |" in markdown


def test_disclaimer_is_present_and_names_the_relevant_adrs() -> None:
    report_input = CalibrationReportInput(
        city="City",
        time_window="window",
        fit=PASSING_FIT,
    )

    markdown = render_calibration_report(report_input)

    assert "Disclaimer" in markdown
    assert "ADR 0004" in markdown
    assert "ADR 0009" in markdown
    assert "never a" in markdown
    assert "finding" in markdown


def test_notes_are_included_verbatim_when_present() -> None:
    report_input = CalibrationReportInput(
        city="City",
        time_window="window",
        fit=PASSING_FIT,
        notes="Detector D-17 was out of service for the last two days of counts.",
    )

    markdown = render_calibration_report(report_input)

    assert "Detector D-17 was out of service for the last two days of counts." in markdown


def test_notes_section_absent_when_not_given() -> None:
    report_input = CalibrationReportInput(
        city="City",
        time_window="window",
        fit=PASSING_FIT,
    )

    markdown = render_calibration_report(report_input)

    assert "## Notes" not in markdown


def test_write_calibration_report_writes_file_matching_render(tmp_path: Path) -> None:
    report_input = CalibrationReportInput(
        city="City",
        time_window="window",
        fit=PASSING_FIT,
        notes="hand-crafted fixture run",
    )
    out_path = tmp_path / "nested" / "report.md"

    returned_path = write_calibration_report(report_input, out_path)

    assert returned_path == out_path
    assert out_path.exists()
    assert out_path.read_text() == render_calibration_report(report_input)
