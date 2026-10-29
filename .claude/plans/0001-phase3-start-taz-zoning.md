# Start Phase 3 (Demand and baseline scenario) — first increment: zoning/TAZ + data-source ADR

## Context

Phase 2 (network build) is done (CHANGELOG [1.4], roadmap `docs/roadmap.md` "Phase 2" marked done). The user asked to "start phase 3" — roadmap's "### Phase 3 - Demand and baseline scenario" (P3.1 zoning/TAZ, P3.2 OD matrix via gravity-model fallback, P3.3 route/trip generation, P3.4 transit demand, P3.5 signal programs, P3.6 baseline scenario definition).

Phase 2 was done incrementally across several versioned commits (1.0→1.4), each closing one or two feature IDs with a real desk run, not as one giant commit. This plan follows the same shape: it closes **P3.1** for real (TAZ zoning), and unblocks **P3.2** by deciding — via a new ADR — what data stands in for population/jobs, since **no such source currently exists in `cities/sjc/data-manifest.yaml`** (confirmed by exploration: the manifest has street geometry, zoning *map* layers, and IBGE street faces, but nothing demographic/economic). P3.3-P3.6 are left as explicit next steps (napkin items), not attempted here — they depend on P3.2's actual OD matrix, which depends on the ADR being accepted and real census data being fetched.

This session is running on the desk machine (confirmed: `~/.venvs/arteria-desk` has real `sumo`/`netconvert`/`duarouter`/`od2trips` 1.28.0, `osmium` on PATH, `ARTERIA_DATA` writable) — not a sandboxed remote session — so the TAZ build runs for real against the real `cities/sjc/network/sjc.net.xml` and the already aerial-verified `cities/sjc/study-areas.geojson`, the same way P2.1/P2.7 did.

## Decision needed first: ADR 0017 (zoning + gravity-model data sources)

Draft `docs/adr/0017-zoning-and-trip-generation-data.md` (status `Proposed`, next free ADR number after 0016), following the template in `docs/adr/README.md`. Decision to propose:

- **TAZ delineation**: one TAZ per enabled study-area candidate (`a`,`b`,`c`,`d` from `cities/sjc/study-areas.geojson`, already aerial-verified per CHANGELOG [1.1]) plus one `external` TAZ covering every edge outside all four polygons (through traffic / the rest of the unified-network envelope). Reuses existing, already-vetted geometry instead of inventing a new zone layer — consistent with how corridors (`cities/sjc/corridors/`) already reuse the same polygons.
- **Production weight (population)**: IBGE Censo 2022 population by census tract ("setores censitários"), self-service download — same agency and no-contact precedent already used for `ibge-faces-logradouros` in the manifest. Recorded as a **new** `data-manifest.yaml` entry (`ibge-censo-populacao-setores`), not fetched in this increment (see Deferred below).
- **Attraction weight (jobs proxy)**: no public jobs/employment dataset exists without contacting an agency, so the ADR proposes reusing the already-downloaded `geosanja-plano-diretor-zoneamento` land-use/zoning classification (commercial/institutional/mixed vs. residential) as a density proxy for attraction, explicitly flagged as a proxy — same honesty pattern as ADR 0013's scope-limits paragraph (which already warns that neighborhood-level equity claims need real census data this proxy can't supply).
- Cross-reference ADR 0013 (gravity-model fallback already decided in principle; this ADR only fills in *which* data backs it) and flag the manifest addition.

This ADR is **Proposed**, not Accepted, in this commit — same precedent as ADR 0006 (intervention catalog schema), which stayed Proposed while its code was built anyway. P3.1 code does not depend on its acceptance (TAZ geometry is independent of the weighting data); P3.2's real gravity-model implementation and the real census download wait for owner acceptance and are logged as the next napkin item.

## P3.1 implementation: `arteria/demand/zoning.py`

Mirrors the existing module conventions (confirmed via exploration of `arteria/network/study_area.py`, `validate.py`, `config.py`):

- Pure stdlib/`shapely` parsing of the net, **no `sumolib`** (keeps it testable without the `geo` extra and without a real SUMO install, same reasoning as `validate.py`'s module docstring). Parse `<location netOffset="dx,dy">` directly from the net.xml root (more robust than the hardcoded `NET_OFFSET` constant duplicated in `render.py`/`crosscheck.py`), then build each non-internal edge's midpoint from its `from`/`to` junction `x,y` (same `_is_internal` skip as `validate.py:50`), shift by the offset, and reproject net-local XY → the study-areas' CRS (EPSG:4326) with `pyproj.Transformer.from_crs(31983, 4326, always_xy=True)` (31983 is the EPSG already used for net-local coordinates in `render.py`/`crosscheck.py`).
- `assign_edges_to_zones(net_path: Path, zones: list[ZonePolygon]) -> dict[str, str]`: pure function, edge id → zone id, point-in-polygon via `shapely`, falling back to `"external"` when no polygon contains the midpoint. No real-binary call at all, so this is testable with a toy fixture net + toy polygons without any adapter/fake needed.
- `load_zones_from_study_areas(path: Path) -> list[ZonePolygon]`: reads `study-areas.geojson`, keeps only `enabled: true` features (reuses the existing `id`/`name` properties already in the file).
- `build_taz_file(net_path: Path, study_areas_path: Path, output_path: Path) -> TazBuildResult` (pydantic result: zone id → edge count, total edges, warning if any zone is empty): writes a SUMO `<tazs><taz id=... edges="..."/></tazs>` file. Orchestrator only; no subprocess/adapter needed since this is pure XML/geometry, unlike `osm_fetch.py`/`build.py`'s binary-calling functions.
- CLI: add a `demand_app = typer.Typer(...)` to `arteria/cli.py`, `app.add_typer(demand_app, name="demand")`, with `arteria demand taz --city sjc` following the existing try/except/`typer.Exit(1)` shape used by `network build`/`network rebuild`. Lazy-imports the zoning module like other commands do.
- Output path: new `cities/sjc/demand/` directory (new, since `cities/sjc/network/` is network-build-only and P3.6's `scenarios/baseline/` is a later deliverable); `cities/sjc/demand/sjc.taz.xml` is a reproducible derived artifact (from the committed `study-areas.geojson` + the reproducible `sjc.net.xml`), so it's gitignored like the other generated SUMO files — add `cities/*/demand/*.taz.xml` to `.gitignore` next to the existing `cities/*/network/*.net.xml` line. A small `cities/sjc/demand/README.md` documents the zone→edge-count summary (committed, like `cities/sjc/corridors/README.md` documents its own outputs) instead of a gitignored report.

## Tests

`tests/test_zoning.py`, following `tests/test_study_area.py`'s / `tests/test_network_validate.py`'s style (plain functions, `tmp_path`, module-level toy fixture constants):
- A hand-written toy `.net.xml` (few junctions/edges, explicit `netOffset`) + a toy 2-polygon GeoJSON (one zone covering half the edges, one `enabled: false` zone that must be ignored) → assert exact edge→zone mapping, external fallback for an edge outside both, and that a disabled zone contributes no polygon.
- A real-data sanity check mirroring `tests/test_study_area.py:86-92`'s pattern: load the actual `cities/sjc/study-areas.geojson` and confirm it parses into 4 enabled `ZonePolygon`s with the expected ids (`a`,`b`,`c`,`d`) — cheap, no real net.xml needed for this part.
- Since this is the desk session (real `sjc.net.xml` exists), also run `arteria demand taz --city sjc` for real once by hand (not as a committed pytest, to keep the suite fast/toy-sized per the roadmap's remote-suite-under-5-min rule) and sanity-check the zone/edge-count summary before committing the README.

## Docs/process updates (same commit or immediate follow-up, per CLAUDE.md working conventions)

- `docs/roadmap.md`: mark P3.1 "Status: done" with the same inline style as P2's sub-items; leave P3.2-P3.6 open.
- `CHANGELOG.md`: new version entry (0.5, "Phase 3 started: TAZ zoning") describing the real `sjc.taz.xml` run (zone edge counts) and ADR 0017 drafted.
- `.claude/napkin.md`: add an open item for "P3.2 gravity model: fetch real IBGE Censo population data once ADR 0017 is accepted; implement OD matrix + od2trips/duarouter wiring" so the next session picks it up — do **not** implement the gravity model itself now.
- Commit message follows the global commit-rules file (`/mnt/c/Users/lw_na/.claude/memory/feedback_commit_rules_global.md`) before creating the commit.
- After the commit: invoke `thesis-orchestrator` per `CLAUDE.md` (this commit carries research/methodology content — a new ADR and a roadmap-phase feature — so it is **not** one of the skip-listed purely-administrative/tooling commits).

## Verification

- `python3 -m pytest tests/test_zoning.py -q` (and the full `nox -s lint tests` / `python3 -m pytest` per the napkin's worktree note) passes.
- Real run: `arteria demand taz --city sjc` against the actual `cities/sjc/network/sjc.net.xml` (rebuild it first with `arteria network rebuild --city sjc` if it's not present/current) and `cities/sjc/study-areas.geojson`; confirm all 4 zones get a non-trivial edge count and no zone is empty, before writing the CHANGELOG numbers.
