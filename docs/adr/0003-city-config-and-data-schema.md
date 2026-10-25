# 0003. City config and data schema

Date: 2026-10-24
Status: Accepted (2026-10-25: owner proceeds without waiting for real traffic
counts/OD data to fill in fields like `time_windows` — confirmed
qualitatively, from direct local experience, that corridors A (Anel
Viário/Dutra spillover) and D (Jardim Colinas roundabout) carry heavy
peak-hour traffic; see "Owner acceptance" below)

## Context

Every pilot city needs the same handful of facts before any network build or demand work can start: where it is, what time windows matter, what SUMO version it was built against, and what data sources feed it, each with a license and a trust level (public vs. restricted). `docs/roadmap.md` P0.2 calls for a `cities/<city>/city.yaml` schema covering this; P1.1/P1.2 (source inventory, data requests) and the remote-session rules (data manifest: `license`, `visibility: public|restricted`, `sha256` per input, enforced by a pre-commit hook) depend on that schema existing first. Later schemas — the intervention catalog (P5.1, ADR 0006) and scenario definitions (P3.6) — follow the same validated-YAML pattern, so getting the base shape right here avoids redoing it three times.

Remote Claude sessions (ADR 0009) never see restricted data, but they do read and validate `city.yaml` and the data manifest, write schema code, and check a city's config for correctness — so the schema has to be fully expressible, and checkable, from committed files alone.

## Decision

- Define `cities/<city>/city.yaml` and `cities/<city>/data-manifest.yaml` as validated schemas (pydantic models, exported as JSON Schema for editor/CI use), not free-form YAML.
- `city.yaml` fields: bounding polygon (GeoJSON or WKT), CRS/UTM zone, one or more named time windows (e.g. `am-peak`), the pinned SUMO version, and a reference to the data manifest.
- `data-manifest.yaml` entries, one per data source: `name`, `license`, `visibility: public|restricted`, `sha256` (of the file as committed or as tracked outside git), `source`/contact, and status (requested/received/unavailable), per P1.1/P1.2.
- A `visibility: restricted` entry's `sha256` must never match a file actually present in the git index; this is enforced by a pre-commit hook run both at the desk and by remote sessions (R1), per ADR 0009/0010.
- Validation ships as library code (`arteria/network` or a dedicated `arteria/config` module) plus a CLI check (`arteria doctor` or a dedicated `arteria config validate --city <name>`), testable on toy fixtures with no real city data.
- The intervention catalog schema (ADR 0006) and scenario definitions (P3.6) reuse this validated-YAML-plus-pydantic pattern rather than inventing a new one.

## Consequences

- Easier: remote sessions can fully validate a city's config and catch a licensing/checksum mistake before it reaches the desk; a new city (P10) starts from a schema-checked template instead of free-form YAML that only fails at runtime; downstream schemas (catalog, scenarios) get a consistent shape for free.
- Harder: every new field needs a schema change and a migration note, not just an ad-hoc YAML edit; the schema has to be designed before real SJC data is in hand, so some fields are best guesses.
- Risk: over-engineering the schema before real data exposes its actual shape (flagged as a P0 risk in the roadmap) — mitigate by keeping the schema minimal and versioned, extending it as P1 data requests come back rather than anticipating every field now.

## Owner acceptance (2026-10-25)

The owner accepts this ADR as written and chooses not to wait for real
traffic counts or OD survey data (both `deferred` in
`cities/sjc/data-manifest.yaml`) before treating schema fields like
`time_windows` as usable rather than placeholder. The stated basis is
direct local experience, not measurement: corridor A (the Anel Viário,
which absorbs spillover whenever an incident closes the Dutra) and
corridor D (the Jardim Colinas roundabout/Ponte Estaiada junction) are
both known qualitatively to carry heavy peak-hour traffic — consistent with
`cities/sjc/candidate-corridors.md`'s "Qualitative first-pass read" table.
This does not extend to corridors B and C, whose listed issue is forced
detour length / one-way maze structure rather than peak congestion.

This is still qualitative, not calibration-grade: `city.yaml`'s
`time_windows.am-peak` stays a best guess (hours, not volumes) until P4
calibration against real counts, if those ever arrive — accepting this ADR
unblocks P0/P1 schema work now, it does not retroactively make the am-peak
window itself a validated calibration target.
