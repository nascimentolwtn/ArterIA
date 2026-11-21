"""Catalog review report for planners (roadmap P5.6).

Turns an `InterventionCatalog` (`arteria/interventions/catalog.py`, P5.1/ADR
0006) into a Markdown report a planner can read top to bottom and mark
decisions on: a summary table for quick scanning (id, type, complexity,
cost, targets, mutual exclusions, a blank decision checkbox) followed by one
detail section per entry carrying the free-text legal/safety/equity fields
ADR 0006 deliberately left as human-judgment prose rather than structured,
machine-checkable rules.

Only the table half of P5.6 lands here, same reasoning as
`arteria/report/generator.py`'s before/after report: no map/plotting
library is available remotely (ADR 0009), so the map half of "table + map"
is future desk-session work.
"""

from __future__ import annotations

from arteria.interventions.catalog import CatalogEntry, InterventionCatalog

_DISCLAIMER = (
    "**Caveat:** catalog entries are reviewed here as structured data, but "
    "`legal_constraints`, `safety_notes`, `emergency_access_notes`, and "
    "`equity_notes` are free text by design (ADR 0006) — judging whether a "
    "constraint blocks an intervention, or weighing an equity trade-off, is "
    "a human review step, not something this report decides. If this "
    "catalog is a toy/fixture catalog rather than a real, manifest-backed "
    "city catalog (ADR 0009), no decision made from it should be treated as "
    "a real planning outcome."
)


def _format_cost(cost_estimate_brl: float | None) -> str:
    if cost_estimate_brl is None:
        return "n/a"
    return f"R$ {cost_estimate_brl:,.2f}"


def _format_list(values: list[str]) -> str:
    return ", ".join(values) if values else "—"


def _format_targets(entry: CatalogEntry) -> str:
    targets = entry.target_edges + entry.target_junctions
    return _format_list(targets)


def _render_summary_table(entries: list[CatalogEntry]) -> str:
    rows = [
        "| ID | Type | Complexity | Cost estimate | Targets | Mutual exclusions | Decision |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        rows.append(
            f"| {entry.id} | {entry.type} | {entry.complexity} | "
            f"{_format_cost(entry.cost_estimate_brl)} | {_format_targets(entry)} | "
            f"{_format_list(entry.mutual_exclusions)} | ☐ Approve  ☐ Reject |"
        )
    return "\n".join(rows)


def _render_entry_detail(entry: CatalogEntry) -> str:
    lines = [
        f"### {entry.id}",
        "",
        entry.description,
        "",
        f"- Type: {entry.type}",
        f"- Complexity: {entry.complexity}",
        f"- Cost estimate: {_format_cost(entry.cost_estimate_brl)}",
        f"- Target edges: {_format_list(entry.target_edges)}",
        f"- Target junctions: {_format_list(entry.target_junctions)}",
        f"- Legal constraints: {_format_list(entry.legal_constraints)}",
        f"- Safety notes: {entry.safety_notes or '—'}",
        f"- Emergency access notes: {entry.emergency_access_notes or '—'}",
        f"- Equity notes: {entry.equity_notes or '—'}",
        f"- Expected beneficiaries: {_format_list(entry.expected_beneficiaries)}",
        f"- Expected losers: {_format_list(entry.expected_losers)}",
        f"- Mutual exclusions: {_format_list(entry.mutual_exclusions)}",
    ]
    return "\n".join(lines)


def render_catalog_review_report(catalog: InterventionCatalog, *, city: str | None = None) -> str:
    """Render an `InterventionCatalog` into a Markdown catalog review report.

    A summary table (one row per entry, with a blank decision checkbox)
    comes first for quick scanning, followed by one detail section per
    entry carrying the free-text fields ADR 0006 left for human judgment.
    An empty catalog renders a short note rather than an error — an
    as-yet-unpopulated catalog is a normal state, not a caller mistake.
    """
    title = f"# Catalog Review Report: {city}" if city else "# Catalog Review Report"
    sections = [title, "", _DISCLAIMER, ""]

    if not catalog.entries:
        sections.append("No entries in this catalog yet.")
        return "\n".join(sections) + "\n"

    sections.append(_render_summary_table(catalog.entries))
    sections.append("")
    sections.append("## Entry details")
    sections.append("")
    for entry in catalog.entries:
        sections.append(_render_entry_detail(entry))
        sections.append("")

    return "\n".join(sections) + "\n"
