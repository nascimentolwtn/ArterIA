from pathlib import Path

from arteria.interventions.catalog import InterventionCatalog, load_catalog
from arteria.report.catalog_report import render_catalog_review_report

_TOY_CATALOG_PATH = Path(__file__).parent / "fixtures" / "toy-catalog.yaml"


def test_render_catalog_review_report_includes_every_entry() -> None:
    catalog = load_catalog(_TOY_CATALOG_PATH)

    report = render_catalog_review_report(catalog, city="sjc")

    assert "# Catalog Review Report: sjc" in report
    for entry in catalog.entries:
        assert entry.id in report
        assert entry.description in report


def test_render_catalog_review_report_summary_table_has_decision_checkbox() -> None:
    catalog = load_catalog(_TOY_CATALOG_PATH)

    report = render_catalog_review_report(catalog)

    assert "# Catalog Review Report" in report
    assert "☐ Approve" in report
    assert "☐ Reject" in report


def test_render_catalog_review_report_shows_cost_and_targets() -> None:
    catalog = load_catalog(_TOY_CATALOG_PATH)

    report = render_catalog_review_report(catalog)

    bus_lane = next(e for e in catalog.entries if e.id == "busline-x-bus-lane")
    assert "R$ 120,000.00" in report
    assert "edgeA" in report
    assert "edgeB" in report
    # mutual exclusions reference the other entry's id
    assert bus_lane.mutual_exclusions[0] in report


def test_render_catalog_review_report_null_cost_and_equity_render_as_placeholder() -> None:
    catalog = load_catalog(_TOY_CATALOG_PATH)

    report = render_catalog_review_report(catalog)

    turn_restriction = next(e for e in catalog.entries if e.id == "junction-y-turn-restriction")
    assert turn_restriction.equity_notes is None
    assert f"### {turn_restriction.id}" in report
    assert "Equity notes: —" in report


def test_render_catalog_review_report_empty_catalog_renders_note_not_error() -> None:
    report = render_catalog_review_report(InterventionCatalog(entries=[]))

    assert "No entries in this catalog yet." in report


def test_render_catalog_review_report_includes_adr_0006_caveat() -> None:
    catalog = load_catalog(_TOY_CATALOG_PATH)

    report = render_catalog_review_report(catalog)

    assert "ADR 0006" in report
    assert "ADR 0009" in report
