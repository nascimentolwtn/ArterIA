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

1. **[2026-10-25] Desk: run the full studyarea -> osm fetch -> network build chain for real**
   Do instead: all the code exists now — `docs/local/sjc-quickstart.md` is the exact
   sequence (`arteria studyarea build` -> `arteria osm fetch --candidate b` ->
   `arteria network build` -> `arteria network validate` -> `netedit`/`sumo-gui` ->
   `randomTrips.py` for a quick visual). None of it has run against real
   `sumo`/`netconvert`/`osmium`/Nominatim/Geofabrik yet (ADR 0009: no network, no
   binaries remotely) — this is the first real contact. Expect to need to adjust
   `default_netconvert_options()` (`arteria/network/build.py`) against the installed
   `netconvert --help`, and the `osmium extract` flags against `osmium --help`; note
   whatever changes in a commit so the next remote session doesn't reintroduce the
   same unverified assumption. Treat all output as draft/uncalibrated — check the
   study-area polygon against satellite imagery/OSM, and don't treat `randomTrips.py`
   traffic as anything but a routability sanity check.
2. **[2026-10-24] Benchmark dev PC against 8-core / 32 GB guideline** (small)
   Do instead: check before committing to local calibration/optimizer run plans.
3. **[2026-10-24] Desk: run `nox -s smoke` for real**
   Do instead: this session's `nox -s smoke` only confirmed it skips cleanly with no
   `sumo` binary (correct for remote). At the desk, with SUMO installed, confirm it
   actually passes against a real toy network — the roadmap's P0 exit criterion needs
   both halves.
4. **[2026-10-26] Reconcile Windows-native roadmap L-items with ADR 0014 (WSL2-primary desk)** (small)
   Do instead: L4 (long paths), L5 (Defender exclusions), L7 (power hygiene/Task
   Scheduler), L18 (scheduled runs), and L24's BitLocker aside were all written as
   Windows-native `scripts/win/*.ps1`/registry/Task Scheduler items. Under ADR 0014
   (WSL2 sole primary, repo + `ARTERIA_DATA` on native `ext4`) L4/L5 are already
   N/A (see `docs/local/setup-and-daily-commands.md`); L7/L18 need a
   `scripts/linux/...` + systemd-timer/`cron` equivalent instead of `powercfg`/Task
   Scheduler, and L24 needs VeraCrypt's Linux client (or `age`) instead of the
   BitLocker note. Update `docs/roadmap.md`'s L-item table once the actual
   desk scripts get written (L1/L6/L7/L18/L24), not before.
5. **[2026-10-24] Desk check: Geosanja/IBGE downloads + OSM completeness for SJC** (small, unblocks trusting P2.1 network sources)
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
