# 0002. City-agnostic project structure

Date: 2026-10-24
Status: Accepted (2026-10-24: folder-per-city layout kept; scaffolding and the open-data-only
path pulled forward from Phase 10 into P0 — see "Multi-city flexibility" below)

## Context

ArterIA must support São José dos Campos (SJC) as the first pilot without baking SJC-specific assumptions into shared code, so that a second city (Phase 10) can be onboarded later with config/plugin changes only, not a refactor (`docs/roadmap.md` P0.1, P10). The project also runs in two very different places: a Windows 11 desktop (SUMO GUI tools, long calibration/optimizer runs, private data) and sandboxed Linux cloud sessions (toy-fixture tests only, no GUI, no private data, discarded after each session — ADR 0009). Both need the same commands to behave identically.

Two sub-decisions follow from this: how the repo is laid out, and what runs the recurring tasks (lint, tests, builds) across Windows, WSL2 and Linux without relying on tools that are awkward on Windows (`make`, `just`).

**Multi-city flexibility (added 2026-10-24).** The owner may need to add more cities sooner than Phase 10 — e.g. if a thesis advisor or the method itself calls for validating ArterIA's approach against more than one case, not just the SJC pilot. Two things follow from that, decided here rather than deferred to Phase 10:
- A city under this layout is *data and config, never code* — adding one means a new `cities/<name>/` folder, not a new package to write or install. That already made onboarding cheap; what was missing was a scaffolding command to do it (roadmap P10.1), which this ADR now treats as P0 scope rather than P10 scope (see Decision).
- Every city onboarded so far (SJC, by owner decision) starts in open-data-only mode — no municipal agency has been contacted (see `cities/sjc/data-requests.md`). If more cities are needed for validation, each one will realistically start the same way. The open-data-only path (roadmap P10.2: OSM + GTFS + public counts + synthetic demand, no OD survey) is accordingly first-class, not a fallback — `arteria/` must not assume a `data-manifest.yaml` entry is ever `received` rather than `deferred`/`unavailable`.

A heavier alternative — packaging each city as its own installable plugin (entry points, versioned on PyPI) — was considered and rejected: it adds packaging/distribution overhead a thesis-validation city doesn't need, for a decoupling the folder convention already provides (`arteria/` never imports anything from `cities/`).

**Scope stays SJC-only (owner decision, 2026-10-24).** This ADR builds the *capability* to add a city cheaply; it does not decide to use it. For now, SJC is the only city, and the thesis's evidence base is scoped accordingly — consistent with the pre-projeto's current single-case framing across all four tracks. Multi-city stays an option the owner can exercise on their own, later, as the project evolves, or one to offer an advisor once accepted into a program, if that advisor wants multi-case validation. Neither this ADR nor the `arteria city new` command is a commitment to widen the thesis's scope; that decision belongs to the owner (and, once one exists, their advisor), not to this engineering choice.

## Decision

- **Repository layout:**
  - `arteria/` — the shared Python package, city-agnostic: `network/`, `demand/`, `calibration/`, `interventions/`, `optimize/`, `evaluate/`, `report/`.
  - `cities/<city>/` — per-city data: `city.yaml` config (ADR 0003), data-source manifest, calibration artifacts, scenarios, results. `cities/_template/` seeds a new city.
  - `scripts/` — setup and platform-specific helpers only (`scripts/win/*.ps1` for Windows-only OS tasks: registry, Defender, Task Scheduler; no domain logic lives here).
  - `tests/` — unit tests against toy fixtures; no real SUMO binary or city data required to run them.
- **Task runner:** `nox`, defined in a single cross-platform `noxfile.py`, with sessions `lint`, `tests`, `smoke` (real toy-network SUMO run, desktop-only), `build-<city>`, `calibrate-<city>`. Remote Claude sessions only ever run `nox -s lint tests` (R1); everything from `smoke` onward needs a real `sumo`/`netconvert` binary and stays desktop-only.
- **Single CLI:** one Typer-based command, `arteria`, is the only entry point into `arteria/` functionality. Every subcommand takes `--city <name>`, reads `cities/<city>/city.yaml`, writes a run manifest (P0.7), and is idempotent (skips a step when input checksums are unchanged).
- **City scaffolding, pulled forward from P10.1:** `arteria city new <name>` copies `cities/_template/` to `cities/<name>/`, fills in `name`, and validates the result against the ADR 0003 schema — so adding a city for a validation case is a single command, not a manual copy-and-edit.

## Consequences

- Easier: a new city is `cities/_template/` copied and filled in, with no changes to `arteria/`; the same `nox` commands behave identically on Windows, WSL2, and remote Linux sessions, so `nox -s lint tests` is a reliable, fast remote check (ADR 0009); one CLI gives a single place to discover and document commands (`arteria doctor`, `arteria network build`, ...).
- Harder: every new feature must resist the temptation to special-case SJC inside `arteria/`; city-specific logic has to go through config (`city.yaml`), per-city plugin hooks (P10.3), or `cities/<city>/`, which takes more design upfront than a quick inline branch.
- Risk: hidden SJC-specific assumptions can still creep into shared code before a second city exists to catch them (flagged as a P10 risk); mitigate by keeping `cities/_template/` exercised in CI-equivalent tests (P10.4) as soon as it exists, not only when a real second city is onboarded.
- Easier (multi-city): a thesis-validation city can be scaffolded, filled with whatever open data exists, and run through the same `arteria` commands as SJC within minutes, not a phase-10 effort — directly useful if generalizability across cases becomes part of the thesis's evidence.
- Harder (multi-city): nothing in `arteria/` may assume a fully calibrated, municipally-sourced baseline is available; every phase from P3 (demand) onward needs an honest "what if this city only has OSM and public data" path, checked now rather than retrofitted when a second city actually shows up.
