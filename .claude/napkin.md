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

1. **[2026-10-25] Draw bounding polygons for the 4 SJC study areas, priority B > D > C > A**
   Do instead: owner decided (2026-10-25) all 4 candidates in
   `cities/sjc/candidate-corridors.md` are in scope, worked in that priority order.
   Candidate D confirmed as the Jardim Colinas roundabout/Ponte Estaiada. Candidate
   B's polygon connects to A's Anel Viário segment (also confirmed). Still needed
   before P2.1 OSM extraction can start on B (the first priority): an actual
   bounding polygon in `cities/sjc/city.yaml` — none of the 4 has one yet. Desk/GIS
   task, not blocked on OD data (qualitative/open-data-only path is fine for a
   polygon). A possible future extension to B (northbound DCTA↔Dutra dependency
   toward Vista Verde) is logged in `candidate-corridors.md` but out of current scope.
2. **[2026-10-24] Decide repo visibility** (remote sessions push branches directly; drives results-site exposure)
   Do instead: decide before the first remote session pushes code or data manifests (roadmap open question 5).
3. **[2026-10-24] Pick the code license** (small)
   Do instead: decide before first public release; record in an ADR if non-trivial.
4. **[2026-10-24] Benchmark dev PC against 8-core / 32 GB guideline** (small)
   Do instead: check before committing to local calibration/optimizer run plans.
5. **[2026-10-24] Owner review of ADR 0003** (Status: Proposed, unreviewed)
   Do instead: ADR 0002 and 0004 are now both Accepted. ADR 0003 (city.yaml/data-manifest
   schema) hasn't been raised yet — it's already implemented (`arteria/config.py`) and
   exercised against real SJC files, so review is a formality unless something there
   needs to change.
6. **[2026-10-24] Desk: run `nox -s smoke` for real**
   Do instead: this session's `nox -s smoke` only confirmed it skips cleanly with no
   `sumo` binary (correct for remote). At the desk, with SUMO installed, confirm it
   actually passes against a real toy network — the roadmap's P0 exit criterion needs
   both halves.
7. **[2026-10-24] Desk check: Geosanja/IBGE downloads + OSM completeness for SJC** (small, unblocks trusting P2.1 network sources)
   Do instead: `sjc.sp.gov.br/geosanja` and `ibge.gov.br` are both unreachable from this
   remote session's network policy. At the desk: confirm Geosanja still serves Master
   Plan/zoning layers and check for a distinct road-network layer; confirm IBGE's Base
   de Faces de Logradouros (2022) has moved past "preliminary"; spot-check OSM road
   completeness for the SJC area (Kontur's OSM Road Completeness map, or JOSM/QGIS vs.
   satellite) before relying on it for the pilot corridor. Update
   `cities/sjc/data-manifest.yaml` notes with what's actually found.

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
