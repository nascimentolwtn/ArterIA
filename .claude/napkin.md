# Napkin Runbook

## Curation Rules
- Re-prioritize on every read.
- Keep recurring, high-value notes only.
- Max 10 items per category.
- Each item includes date + "Do instead".
- Only open/unresolved items are kept here. The moment an item is done, remove it from this file — it belongs in `CHANGELOG.md` (user-facing) and/or `docs/adr/` (architectural record), not here.

## Execution & Validation (Highest Priority)

1. **[2026-10-25] Parallel worktree agents: `pip install -e .` is not worktree-safe here**
   Do instead: there's no per-worktree venv in this container — `pip install -e .` writes a single shared, system-wide editable link, so concurrent `pip install -e .` calls from sibling worktrees race and can point the installed `arteria` at the wrong path. Also, `pytest` installed as a `uv tool` can't see that editable install at all. Run `python3 -m pytest` (or set `PYTHONPATH` to the worktree root) instead of reinstalling per worktree; only reinstall editable once, from the final merged repo path, after parallel work lands.

## Roadmap & Status

See `README.md` for current status, `docs/roadmap.md` for the phased plan (P0-P10, remote R1-R21 = tasks for Claude app sessions, local L1-L25), and `docs/` for research material.

## Reference Documentation

None yet.

## Backlog Workflow

When adding new backlog items:
1. **Add napkin summary** — brief one-liner with date + impact + estimate (goes in "Backlog Features" below)
2. **Add detailed spec if needed** — for an architectural or irreversible decision, write an ADR in `docs/adr/`
3. **Update status** — reflect near-term priority changes in `README.md`

## Bug Fixes (Next Priority)

None open.

## Backlog Features

1. **[2026-10-29] P3.2 gravity model blocked on the Geosanja attraction-proxy layer**
   Do instead: production weights are done (`arteria demand population --city sjc`,
   `arteria/demand/population.py`, real IBGE Censo 2022 data, `ibge-censo-populacao-setores`
   in the manifest). The attraction side (Geosanja "03 Macrozoneamento Urbano" zoning layer,
   per ADR 0017 — still `Proposed`) was never actually downloaded (only road-hierarchy layers
   were); its portal isn't scriptable from this session (guessed GeoServer WFS endpoints need
   auth, and probing further got flagged by the sandbox as access circumvention). Needs either
   a desk browser session or the owner fetching the layer by hand before the gravity model
   (`od2trips`/`duarouter` wiring, P3.2/P3.3) can be built. Don't build it against placeholder
   attraction weights.

## User Directives

1. **[2026-10-24] Keep responses concise; avoid trailing summaries**
   Do instead: State results directly and focus on relevant updates only.
2. **[2026-10-24] Don't contact SJC agencies yet**
   Do instead: use open/self-service data (OSM, Geosanja, IBGE — see
   `cities/sjc/data-manifest.yaml`) for now; the drafts in
   `cities/sjc/data-requests.md` stay unsent until the owner says otherwise.
3. **[2026-10-24] Scope stays SJC-only; multi-city is an option, not a plan**
   Do instead: `arteria city new` (ADR 0002) makes a second city cheap to add, but don't
   onboard one unprompted. The owner decides if/when — either on their own as the
   project evolves, or to offer an advisor once accepted into a program. Don't treat
   any thesis track's "should this widen to N cities?" open question as answered.
