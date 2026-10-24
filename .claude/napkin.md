# Napkin Runbook

## Curation Rules
- Re-prioritize on every read.
- Keep recurring, high-value notes only.
- Max 10 items per category.
- Each item includes date + "Do instead".
- Only open/unresolved items are kept here. The moment an item is done, remove it from this file — it belongs in `CHANGELOG.md` (user-facing) and/or `docs/adr/` (architectural record), not here.

## Execution & Validation (Highest Priority)

None yet.

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

1. **[2026-10-24] Decide repo visibility** (remote sessions push branches directly; drives results-site exposure)
   Do instead: decide before the first remote session pushes code or data manifests (roadmap open question 5).
2. **[2026-10-24] Pick the code license** (small)
   Do instead: decide before first public release; record in an ADR if non-trivial.
3. **[2026-10-24] Benchmark dev PC against 8-core / 32 GB guideline** (small)
   Do instead: check before committing to local calibration/optimizer run plans.
4. **[2026-10-24] Owner review of ADR 0003** (Status: Proposed, unreviewed)
   Do instead: ADR 0002 and 0004 are now both Accepted. ADR 0003 (city.yaml/data-manifest
   schema) hasn't been raised yet — it's already implemented (`arteria/config.py`) and
   exercised against real SJC files, so review is a formality unless something there
   needs to change.
5. **[2026-10-24] Desk: run `nox -s smoke` for real**
   Do instead: this session's `nox -s smoke` only confirmed it skips cleanly with no
   `sumo` binary (correct for remote). At the desk, with SUMO installed, confirm it
   actually passes against a real toy network — the roadmap's P0 exit criterion needs
   both halves.
6. **[2026-10-24] Desk check: Geosanja/IBGE downloads + OSM completeness for SJC** (small, unblocks trusting P2.1 network sources)
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
