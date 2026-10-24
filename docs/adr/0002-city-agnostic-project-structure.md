# 0002. City-agnostic project structure

Date: 2026-10-24
Status: Proposed

## Context

ArterIA must support São José dos Campos (SJC) as the first pilot without baking SJC-specific assumptions into shared code, so that a second city (Phase 10) can be onboarded later with config/plugin changes only, not a refactor (`docs/roadmap.md` P0.1, P10). The project also runs in two very different places: a Windows 11 desktop (SUMO GUI tools, long calibration/optimizer runs, private data) and sandboxed Linux cloud sessions (toy-fixture tests only, no GUI, no private data, discarded after each session — ADR 0009). Both need the same commands to behave identically.

Two sub-decisions follow from this: how the repo is laid out, and what runs the recurring tasks (lint, tests, builds) across Windows, WSL2 and Linux without relying on tools that are awkward on Windows (`make`, `just`).

## Decision

- **Repository layout:**
  - `arteria/` — the shared Python package, city-agnostic: `network/`, `demand/`, `calibration/`, `interventions/`, `optimize/`, `evaluate/`, `report/`.
  - `cities/<city>/` — per-city data: `city.yaml` config (ADR 0003), data-source manifest, calibration artifacts, scenarios, results. `cities/_template/` seeds a new city.
  - `scripts/` — setup and platform-specific helpers only (`scripts/win/*.ps1` for Windows-only OS tasks: registry, Defender, Task Scheduler; no domain logic lives here).
  - `tests/` — unit tests against toy fixtures; no real SUMO binary or city data required to run them.
- **Task runner:** `nox`, defined in a single cross-platform `noxfile.py`, with sessions `lint`, `tests`, `smoke` (real toy-network SUMO run, desktop-only), `build-<city>`, `calibrate-<city>`. Remote Claude sessions only ever run `nox -s lint tests` (R1); everything from `smoke` onward needs a real `sumo`/`netconvert` binary and stays desktop-only.
- **Single CLI:** one Typer-based command, `arteria`, is the only entry point into `arteria/` functionality. Every subcommand takes `--city <name>`, reads `cities/<city>/city.yaml`, writes a run manifest (P0.7), and is idempotent (skips a step when input checksums are unchanged).

## Consequences

- Easier: a new city is `cities/_template/` copied and filled in, with no changes to `arteria/`; the same `nox` commands behave identically on Windows, WSL2, and remote Linux sessions, so `nox -s lint tests` is a reliable, fast remote check (ADR 0009); one CLI gives a single place to discover and document commands (`arteria doctor`, `arteria network build`, ...).
- Harder: every new feature must resist the temptation to special-case SJC inside `arteria/`; city-specific logic has to go through config (`city.yaml`), per-city plugin hooks (P10.3), or `cities/<city>/`, which takes more design upfront than a quick inline branch.
- Risk: hidden SJC-specific assumptions can still creep into shared code before a second city exists to catch them (flagged as a P10 risk); mitigate by keeping `cities/_template/` exercised in CI-equivalent tests (P10.4) as soon as it exists, not only when a real second city is onboarded.
