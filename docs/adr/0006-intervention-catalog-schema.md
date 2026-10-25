# 0006. Intervention catalog schema

Date: 2026-10-25
Status: Proposed

## Context

`docs/roadmap.md` P5.1 calls for a catalog schema covering every candidate
street intervention a city considers: type, target edges/junctions,
transform-specific parameters, cost estimate, complexity, legal/property
constraints, safety, emergency access, equity notes, expected beneficiaries/
losers, and mutual exclusions between candidates. The catalog is the object
a human planner audits — one entry per candidate intervention, with its
feasibility, constraint, and equity fields reviewed — before any package of
entries is handed to the upper-level optimizer (P7). Getting this schema
right now matters because P5.3 (candidate generation) and P5.6 (catalog
review report) both read and write against it, and a wrong shape would need
a migration pass across both.

The catalog spans ten structurally different intervention mechanics (P5.2):
a one-way conversion needs a direction, a bus lane needs a lane index and an
`allow`/`disallow` vClass list, a reversible lane needs a time-of-day
schedule, a new connector needs geometry — no single flat set of typed
fields covers all of them without either a large sparse schema or ten
near-duplicate sub-schemas.

Like the rest of P5 (per ADR 0003's remote-session boundary, elaborated in
ADR 0009), this schema module is exercised only against the toy fixture
(`tests/fixtures/toy-catalog.yaml`); it never touches a real city's network
or restricted municipal data.

## Decision

- `arteria/interventions/catalog.py` follows the same validated-YAML-plus-
  pydantic pattern as `arteria/config.py` (ADR 0003): `CatalogEntry` and
  `InterventionCatalog` pydantic v2 models, a closed `InterventionType`
  `Literal` matching the ten P5.2 transform types, a closed `Complexity`
  `Literal`, and a `load_catalog(path)` loader (`yaml.safe_load` +
  `model_validate`).
- `CatalogEntry.parameters` is a free-form `dict`, not a per-type sub-schema.
  Forcing one typed sub-model per intervention type now, before P5.2's
  transform library and P5.3's candidate generation have exercised more
  than a couple of these mechanics in real code, would be premature: the
  likely shape of "reversible lane schedule" or "new connector geometry"
  parameters is still a guess, and a wrong typed schema is more costly to
  revise than a wrong dict key.
- `legal_constraints`, `safety_notes`, `emergency_access_notes`, and
  `equity_notes` stay free text (a list of strings or an optional string),
  not a structured rules engine. At this stage, judging whether a
  constraint blocks an intervention, or weighing an equity trade-off, is a
  human review step for the planner (P5.6), not something ArterIA encodes
  as machine-checkable rules — doing so would require a legal/equity
  ruleset this project has no mandate or data to build yet.
- `mutual_exclusions` is validated for referential integrity at load time:
  a `model_validator(mode="after")` on `InterventionCatalog` rejects any
  entry whose `mutual_exclusions` list names an id absent from the
  catalog, or names the entry's own id, collecting every bad reference
  into one `ValueError` rather than failing on the first.
- As with every other P5 module, this schema and its tests run only against
  `tests/fixtures/toy-catalog.yaml`; no real city's catalog is required or
  read here (ADR 0009).

## Consequences

- Easier: the catalog schema ships now, unblocking P5.3 (candidate
  generation can target `CatalogEntry` immediately), P5.6 (the catalog
  review report has a stable object to render), and eventually P7 (the
  optimizer's decision vector indexes into validated catalog entries).
  Referential-integrity checking of `mutual_exclusions` catches a
  planner's or generator's bad id at load time instead of silently
  allowing an invalid package downstream.
- Harder: a free-form `parameters` dict means pydantic cannot catch a
  missing or misspelled transform parameter (e.g. `lane_index` vs.
  `laneIndex`) at the catalog level — that validation currently lives in
  each P5.2 transform function instead, so a bad catalog entry surfaces
  later than it would with per-type sub-models. Likewise, free-text
  constraint/equity fields cannot be queried or filtered on structure
  (e.g. "find every entry a given legal constraint blocks"); a planner
  currently has to read the text.
- Risk/trade-off: if a handful of intervention types turn out to dominate
  the real catalog (e.g. bus lanes and one-way conversions are most of
  P5.3's generated candidates), it may be worth tightening `parameters`
  into per-type sub-models for just those types once their real shape is
  known from P5.2/P5.3 usage, rather than guessing all ten shapes now.
