# Changelog

All notable changes to ArterIA are documented in this file, in plain language for anyone following the project (not just contributors). Versioning follows [Semantic Versioning](https://semver.org/) once the project has a first runnable release; before that, versions mark planning milestones.

## [0.2] - 2026-10-24

### Added

- First code: the `arteria` Python package skeleton (`network/`, `demand/`, `calibration/`, `interventions/`, `optimize/`, `evaluate/`, `report/`), per ADR 0002. Each subpackage is still an empty placeholder — real content lands with its roadmap phase.
- The `arteria` CLI (Typer), starting with `arteria doctor`: reports the Python version, whether `SUMO_HOME`/`sumo`/`netconvert`/`osmium` are available, and whether `ARTERIA_DATA`/`ARTERIA_PRIVATE` are set and writable.
- Validated `city.yaml` and `data-manifest.yaml` schemas (`arteria/config.py`, per ADR 0003), exercised against `cities/sjc/`'s real files, `cities/_template/`, and toy fixtures.
- `cities/_template/` (copyable starting point for a new city) and a `cities/sjc/city.yaml` stub (placeholders for the still-open bounding polygon and time windows).
- A pre-commit safety net (`arteria/data_safety.py`, per ADR 0004): refuses to commit a file whose bytes match a `visibility: restricted` data-manifest checksum.
- `nox -s lint tests` (ruff, mypy, pytest) passing in this remote session, and `nox -s smoke` correctly skipping here (no real SUMO binary) rather than failing — the P0 exit criterion from `docs/roadmap.md`.
- ADR 0004 (data storage and versioning) accepted: confirmed local-disk-only, no Git LFS, no external object store.
- ADR 0002 (project structure) accepted, amended for multi-city flexibility: a thesis advisor or the method itself may call for validating ArterIA against more than one city, sooner than Phase 10. Pulls the city-scaffolding command and the open-data-only path forward from Phase 10 into P0 scope. Ships `arteria city new <name>`, which copies `cities/_template/` into a new, schema-validated `cities/<name>/`.

## [0.1] - 2026-10-24

### Added

- Initial project documentation: `README.md` describing the project's purpose, workflow, and pilot city (São José dos Campos, SP, Brazil).
- Research brief (`docs/research-brief-sjc.md`) covering local context, academic foundations, and a recommended method for the first pilot.
- Architecture Decision Record process (`docs/adr/`), with ADR 0001 recording the choice of SUMO as the project's traffic simulator.
- Project guidance file (`CLAUDE.md`) for AI-assisted development sessions.
- Working notes convention (`.claude/napkin.md`) for tracking open items during development.
- Phased roadmap (`docs/roadmap.md`): "remote" work is now a list of tasks the owner can hand to Claude from the phone app (drafting, coding against small test fixtures, reviews, docs), while simulation runs, GUI tools and private data stay on the desktop. The earlier plan built around GitHub Actions runners was dropped.
- Three architecture decisions drafted ahead of any code, per the roadmap's planned ADR index: project layout and task runner (`docs/adr/0002-city-agnostic-project-structure.md`), the per-city config and data schema (`docs/adr/0003-city-config-and-data-schema.md`), and where data lives and how it's versioned (`docs/adr/0004-data-storage-and-versioning.md`). All three are `Status: Proposed`, awaiting owner acceptance before Phase 0 implementation starts.
- SJC data-source inventory and request drafts (`cities/sjc/data-manifest.yaml`, `cities/sjc/data-requests.md`) for the pilot's Phase 1 data: PlanMob, the Master Plan, OD survey, FGV transit-tender studies, Linha Verde, GTFS, traffic counts, signal timing, crash data, and emergency-response data.
- Contacting SJC agencies is deferred by the owner's choice for now. In its place, three no-contact, self-service sources for the street network and road hierarchy: OpenStreetMap (the roadmap's existing P2.1 plan), the city's own Geosanja geodata portal (Master Plan/zoning map layers), and IBGE's Base de Faces de Logradouros. The Master Plan entry in the manifest moved from "needs a request" to "public, self-service download" as a result.
