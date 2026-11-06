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
2. **[2026-11-06] Sync the local branch to `origin/main` before fanning out parallel worktree agents**
   Do instead: a session's local feature branch can sit many commits behind `origin/main` (merged there a while ago, with unrelated sessions pushing straight to `main` since) without the session noticing — `git status` against its own `origin/<branch>` looks clean either way. Spawning worktree agents off that stale base risks assigning work already done on `main` (one of six parallel agents here correctly caught this itself for a demand-module task and stood down rather than duplicate/overwrite real code) and, separately, leaves the branch needing a `git checkout -B <branch> origin/main` + cherry-pick of every worktree commit before it can push as a clean fast-forward. `git merge-base --is-ancestor <branch-tip> origin/main` is the one-line check; run it (and `git fetch origin main`) before spawning, not after.

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

1. **[2026-10-29] P3.2/P3.3/P3.6 real run blocked on two inputs: Geosanja attraction layer and traffic counts**
   Do instead: production weights (`arteria demand population --city sjc`, real IBGE
   Censo 2022 data), P3.3's `od2trips`/`duarouter`/`routeSampler` mechanics
   (`arteria/demand/trips.py`) and P3.6's scenario schema (`ScenarioConfig`,
   `arteria/config.py`) are all done, all tested only against toy fixtures and the real
   SUMO binaries — not against real SJC data. Two things still block running any of this
   for real: (1) the attraction side (Geosanja "03 Macrozoneamento Urbano" zoning layer,
   ADR 0017 — still `Proposed`) was never downloaded (only road-hierarchy layers were);
   its portal isn't scriptable from this session (guessed GeoServer WFS endpoints need
   auth, further probing got flagged by the sandbox as access circumvention) — needs a
   desk browser session or the owner fetching it by hand. (2) real traffic counts
   (`traffic-counts` in the data manifest) are still `deferred`, no agency contact
   authorized — needed for `routeSampler`'s counts-driven calibration. Don't build any of
   P3.2/P3.3/P3.6 against placeholder data; don't scaffold a fake `scenario.yaml` either.
2. **[2026-11-04] Next C:S 1 hobby-track reproduction target: Orlando, FL theme-park/resort corridors**
   Do instead: apply `docs/local/cities-skylines.md`'s reproducible procedure to the owner's named
   areas — Parks (Disney, Universal, SeaWorld), Park hotels (Disney's Pop Century, Celebration
   Suites, Universal's Hard Rock Hotel), Outlets (Premium, Vineland). **C:S 1 hobby-track
   reproduction only** (ADR 0011/0015, illustrative, never SUMO evidence) — not a decision to
   onboard Orlando as a second real ArterIA city/pipeline (the "scope stays SJC-only" directive
   below still governs the actual evidence pipeline). Size deliberately before building: these
   named areas are spread far wider than one compact corridor and are landmark footprints, not
   a priori street corridors, so expect (a) geocoding each landmark first to even pick bboxes,
   and (b) several separate crops/saves (one per park/hotel/outlet cluster, or a few combined
   like SJC's B+D) rather than one map — same ~7,000-8,000-way practical import ceiling and
   ~32,768 segment/node hardcoded cap apply (docs/local/cities-skylines.md, ADR 0011 third
   revision), and Orlando's resort-and-parking-lot road density won't obviously scale the same
   way SJC's did.
3. **[2026-10-29] P3.4 (transit demand) has nothing to build: no public SJC GTFS feed**
   Do instead: P3.4 depends on P2.6 (public-transport layer), already recorded as
   "blocked on data, not implemented" — no public SJC GTFS feed was found. Nothing in
   P3.4 is buildable without it (not even mechanics-only, since P2.6's own GTFS-import
   wrapper, roadmap L12, is itself unbuilt and belongs to the already-closed Phase 2, not
   Phase 3). Wait for a feed or owner direction before touching this.
4. **[2026-11-06] Wire P5.4's `validity.py` into `apply.py`'s catalog-entry dispatcher** (small)
   Do instead: `arteria/interventions/validity.py`'s `check_validity()` exists and is tested,
   but nothing calls it — `apply_intervention()` returns a transform's result without checking
   it. Needs a design call this session didn't make: which named emergency/transit/pedestrian
   routes to check against for a given city (probably a `cities/<city>/` config addition, not a
   hardcoded list), and whether a broken-validity result should raise or just annotate the
   `ApplyResult`.
5. **[2026-11-06] Phase 7 optimizer: ADR 0008 unwritten; optuna/baselines, parallel evaluation, MLflow tracking all still open** (medium)
   Do instead: `arteria/optimize/{problem,nsga2,cache}.py` (R9) cover P7.1-P7.3/P7.6/P7.7 only
   as far as "NSGA-II + a stub evaluator + a package cache" — see `docs/roadmap.md`'s P7.x
   status notes for the exact gaps. Worth drafting ADR 0008 (optimization architecture) now that
   there's a real implementation to document, before adding optuna/BoTorch, random/greedy
   baselines, a process-pool backend, or MLflow-style tracking on top.

## User Directives

1. **[2026-10-24] Keep responses concise; avoid trailing summaries**
   Do instead: State results directly and focus on relevant updates only.
2. **[2026-11-06] No PR: merge the designated branch straight into `main` and push**
   Do instead: the owner reviews from the phone app, not via GitHub PR review — opening a PR
   adds a step they can't act on there. Once the designated branch's work is committed, pushed,
   and tests pass, merge it directly into `main` (fast-forward when possible) and push `main`,
   rather than stopping at a pushed branch waiting for a PR. The owner reviews after the fact and
   asks for changes/a revert if needed.
3. **[2026-10-24] Don't contact SJC agencies yet**
   Do instead: use open/self-service data (OSM, Geosanja, IBGE — see
   `cities/sjc/data-manifest.yaml`) for now; the drafts in
   `cities/sjc/data-requests.md` stay unsent until the owner says otherwise.
4. **[2026-10-24] Scope stays SJC-only; multi-city is an option, not a plan**
   Do instead: `arteria city new` (ADR 0002) makes a second city cheap to add, but don't
   onboard one unprompted. The owner decides if/when — either on their own as the
   project evolves, or to offer an advisor once accepted into a program. Don't treat
   any thesis track's "should this widen to N cities?" open question as answered.
