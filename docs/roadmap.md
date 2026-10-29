# ArterIA Roadmap

Status: Draft (phased plan; implementation is ahead of it in places — see `CHANGELOG.md`). Date: 2026-10-24 (revised 2026-10-24: Remote features reframed as Claude app sessions, no GitHub Actions; revised 2026-10-25: version bumped to 0.3; revised 2026-10-28: Phase 2 exit criteria met; revised 2026-10-29: Phase 3 started (P3.1 zoning done), version bumped to 1.5 — this line had fallen out of sync with `CHANGELOG.md`'s actual versioning, which moved to 1.x at the first real end-to-end run [1.0] rather than following the 0.x-per-phase scheme below literally; treat `CHANGELOG.md` as authoritative for the real version; revised 2026-10-29 (same day): P3.2 production weights and P3.3 trip-generation mechanics done, version bumped to 1.6). Current version: 1.6 (Phase 3, demand and baseline scenario, in progress; P3.2's attraction side and P3.3's real run both blocked on data — see P3.2/P3.3 status notes).

This roadmap turns the method in `docs/research-brief-sjc.md` (Phases 1-6) into a phased plan for a **reusable, multi-city** tool, with São José dos Campos (SJC) as the first pilot. It follows ADR 0001 (SUMO as the lower-level simulator, Python as the implementation language). Each phase lists goals, features (with IDs used in the Remote/Local sections), dependencies, deliverables, exit criteria and risks.

Feature IDs: `P<phase>.<n>`. Planned ADRs are marked **[ADR]**.

## Phases

### Phase 0 - Foundations and city-agnostic skeleton

**Goals:** have a repo layout, tooling and conventions so that the first line of pilot code lands in the right place and a second city can be added without refactoring.

**Features**
- P0.1 Repository layout: `arteria/` (shared Python package: `network/`, `demand/`, `calibration/`, `interventions/`, `optimize/`, `evaluate/`, `report/`), `cities/<city>/` (config, raw-data manifest, calibration, scenarios, results), `scripts/`, `tests/`. **[ADR 0002: city-agnostic project structure]**
- P0.2 City config schema (`cities/<city>/city.yaml`): bounding polygon, CRS/UTM zone, time windows (e.g. AM peak), data-source manifest with licenses and credits, SUMO version pin. **[ADR 0003: city config and data schema]**
- P0.3 Python environment: pinned dependencies (`pyproject.toml`, `uv` or `pip-tools`), SUMO version pin and `SUMO_HOME` discovery, `sumolib`/`traci` (or `libsumo`) usage.
- P0.4 Quality gates: `ruff`, `mypy` (lenient at first), `pytest`, pre-commit hooks.
- P0.5 Quality-gate runner: `nox -s lint tests` (lint + unit tests on toy fixtures, real SUMO calls stubbed behind an adapter per ADR 0009), run at the desk and in remote Claude sessions (R1); a separate `nox -s smoke` toy-network SUMO run (real `sumo`/`netconvert` binary) is desktop-only. Hosted CI/GitHub Actions is decided against, not deferred: remote sessions plus the desktop cover every check (ADR 0009).
- P0.6 Data policy: what is committed (configs, small fixtures, manifests, checksums) vs. kept out of git (raw OSM, OD microdata, large outputs); optional Git LFS or external storage (DVC/object storage). **[ADR 0004: data storage and versioning]**
- P0.7 Run provenance: every simulation/optimization run writes a manifest (git SHA, SUMO version, seed, config hash, input checksums).
- P0.8 License decision for code (TBD in README) and data attribution (ODbL for OSM).

**Dependencies:** none.
**Deliverables:** skeleton package, `cities/sjc/city.yaml` stub, `cities/_template/`, `nox -s lint tests` passing both at the desk and in a remote Claude session, `nox -s smoke` (real toy-network SUMO run) passing at the desk, ADRs 0002-0004.
**Exit criteria:** `pytest` passes locally and in a remote Claude session (no real SUMO binary needed there); a toy SUMO run (`nox -s smoke`) passes at the desk (verified 2026-10-26 on WSL2 with SUMO from the `eclipse-sumo` PyPI wheel: `netconvert` + `sumo` on `tests/fixtures/smoke/`, 50 vehicles completed); a contributor can create `cities/<new>/` from the template in under 30 minutes.
**Risks:** over-engineering before real data is seen (mitigate: keep schemas minimal, version them); SUMO version drift between local Windows and Linux (WSL2) (mitigate: pin version, test both; remote sessions never run real SUMO, so they carry no drift risk).

### Phase 1 - Study-area selection (pilot SJC)

**Goals:** choose one or two pilot corridors/neighborhoods in SJC where data exists and interventions are plausible (brief Phase 1).

**Features**
- P1.1 Source inventory: PlanMob SJC diagnostic/prognostic, Master Plan (LC 612/2018), OD survey, FGV transit-tender studies, Linha Verde, GTFS (if available), counts, signal plans, crash data, emergency routes. Record availability, format, license and contact in the city data manifest.
- P1.2 Data requests to the municipality (Ipplan, Secretaria de Mobilidade Urbana, Urbam) and transit operator; track status. **Deferred 2026-10-24:** the owner chose not to contact any agency at this stage; drafts are logged in `cities/sjc/data-requests.md` for later. The street-network need this partly covered is no longer blocked by it — see P2.1.
- P1.3 Corridor scoring matrix using the brief's criteria (congestion, commute flow, bus corridors, active-mode demand, low land acquisition, count/signal availability).
- P1.4 Study-area polygon(s) and buffer zone (for boundary effects and diverted traffic).
- P1.5 Problem statement per corridor (which research questions 1-7 it addresses).

**Dependencies:** P0.2 (manifest format).
**Deliverables:** `cities/sjc/data-manifest.yaml`, corridor scoring note, selected polygon(s) (GeoJSON), thesis chapter input.
**Exit criteria:** pilot area agreed (advisor/stakeholders), minimum data available for calibration (at least link counts or travel times on main links for one peak period).
**Risks:** municipal data not released or delayed (mitigate: plan an OSM + open-data-only fallback with synthetic demand and travel times from public routing/probe sources); scope too large for microsimulation (mitigate: corridor + buffer, mesoscopic for buffer).

### Phase 2 - Network build

**Goals:** a clean, reproducible SUMO network of the study area built from OSM, with local corrections kept as code/patches rather than manual one-off edits.

**Features**
- P2.1 OSM extraction: clip by polygon from Geofabrik/Overpass, pinned snapshot date and checksum. No municipal contact needed; cross-check completeness/road hierarchy against Geosanja's self-service Master Plan/zoning layers and IBGE's Base de Faces de Logradouros (both public, no request required — see `cities/sjc/data-manifest.yaml`), and against satellite imagery, before trusting raw OSM alone for a corridor with no field verification.
  - **Status 2026-10-28: done.** Pinned in `cities/sjc/network/osm-snapshot.yaml` (source + extract sha256, PBF data timestamp); `arteria osm fetch` fails on a mismatch, `--update-snapshot` re-pins. Geometry cross-check against IBGE/GeoSanja has been run (`arteria network crosscheck --city sjc`, results in `data/crosscheck/crosscheck.md`); corridors aerial-checked by the owner 2026-10-27.
- P2.2 `netconvert` pipeline with versioned options (typemaps, junction joining, ramp guessing, TLS guessing, sidewalks/bike lanes, public transport stops from OSM).
  - **Status 2026-10-27: done** (SUMO 1.28 flag set in `default_netconvert_options()`; PT stops and sidewalks not yet added).
- P2.3 Network corrections as patch files (`.nod/.edg/.con/.tll` plain XML or `netconvert` patch inputs) applied on top of the generated net, so rebuilds from new OSM are reproducible.
  - **Status 2026-10-27: mechanism done, no patches yet.** SUMO 1.28 has no `--patch-files`; patches in `cities/sjc/network/patches/manifest.yaml` run as a second `netconvert` pass over the OSM-built net (`--sumo-net-file` + plain-XML files). Tested, including against real `netconvert`.
- P2.4 Manual inspection and fixes in `netedit` for complex junctions, exported back into patch files.
  - Not started (no junction fix needed so far); needs the owner's desk GUI session (`netedit`).
- P2.5 Network validation checks: connectivity, dead ends, lane counts (the validator does not compare against aerial evidence; the aerial check was a manual Google Earth check, see CHANGELOG [1.1]), one-way status, turn restrictions, speed limits, TLS presence.
  - **Status 2026-10-27: done on the unified net**: 0 errors, 127 warnings (74 dead ends, 52 TLS junctions without `<tlLogic>` that no connection uses, 1 routability summary: 93.1% of junctions in the main component), 1 info. No blocking issues.
- P2.6 Public transport layer: GTFS import (`gtfs2pt.py`) or manual bus routes/stops/frequencies.
  - **Status 2026-10-27: blocked on data, not implemented.** No public SJC GTFS found (see `cities/sjc/data-manifest.yaml`).
- P2.7 Network diff/report (edges, lanes, junctions changed between builds) and map renders.
  - **Status 2026-10-28: done.** Diff (`arteria network diff --old --new`, JSON + markdown; also run by `network rebuild`) and map renders (`arteria network render --city sjc`, PNGs in `data/renders/`).

**Dependencies:** P1.4 (polygon), P0.3.
**Deliverables:** `cities/sjc/network/` build script + patches, generated `.net.xml` (artifact, not necessarily committed), validation report.
**Exit criteria:** a one-command rebuild reproduces the same net from a pinned OSM snapshot; validation report has no blocking issues; key corridors verified against aerial imagery/field notes.
**Status 2026-10-28: exit criteria met, phase done.** `arteria network rebuild --city sjc` reproduces the pinned net; validation is 0 errors (127 warnings, none blocking); corridors A-D aerial-verified 2026-10-27; geometry/name cross-checked against IBGE/GeoSanja (P2.1); a netconvert name-escaping bug found during that cross-check was fixed and the net rebuilt (CHANGELOG [1.3]). P2.4 (netedit) and P2.6 (GTFS) stay open as deferred, non-blocking items: no complex junction has needed a manual fix yet, and no public SJC GTFS feed exists.
**Risks:** OSM quality gaps in Brazilian cities (lanes, turn restrictions missing); junction-joining artifacts; GTFS unavailable.

### Phase 3 - Demand and baseline scenario

**Goals:** a baseline demand for the chosen time window(s), consistent with available OD data and counts.

**Features**
- P3.1 Zoning: map OD survey zones to the study area and buffer; TAZ file (`.taz.xml`).
  - **Status 2026-10-29: done.** `arteria demand taz --city sjc` (`arteria/demand/zoning.py`) assigns every network edge to one of the four aerial-verified study-area polygons or to a catch-all `external` zone, by point-in-polygon test of the edge's midpoint, and writes a SUMO `.taz.xml`. Run for real on the unified net: 14,225 edges split a=1,146, b=3,020, c=1,786, d=1,103, external=7,170; no zone empty. See `cities/sjc/demand/README.md`. No OD-survey zones exist to map (ADR 0013), so the TAZ layer reuses the existing study-area geometry instead (ADR 0017).
- P3.2 OD matrix preparation: from OD survey (expanded), or fallback trip generation (population/jobs) with gravity model; time-of-day profile.
  - **Status 2026-10-29: production weights done; attraction data still missing; gravity model not built.** `docs/adr/0017-zoning-and-trip-generation-data.md` (Proposed) names IBGE Censo 2022 population by census tract for production and the Geosanja zoning/land-use layer as an attraction proxy. `arteria demand population --city sjc` (`arteria/demand/population.py`) downloads the real IBGE setor GeoPackage and sums population into the same four TAZs: a=13,499, b=36,391, c=24,516, d=22,702, external=599,946 (1,554 census tracts; see `cities/sjc/demand/README.md`, `ibge-censo-populacao-setores` in the data manifest). The attraction-side proxy (Geosanja zoning layer) has not been obtained — the portal isn't scriptable from this session — so the gravity model itself (needs both weights) is still not built.
- P3.3 Route/trip generation: `od2trips`, `duarouter`, or `routeSampler` (counts-driven) and `flowrouter`.
  - **Status 2026-10-29: mechanics done, real run blocked on two upstream inputs.** `arteria/demand/trips.py` wraps the real `od2trips`, `duarouter` and `routeSampler.py` tools behind the same injected-`run` seam as `network/build.py` (ADR 0009), with `arteria demand od2trips`/`duarouter`/`routesampler` CLI commands; a desk-only real-binary round trip (toy OD matrix -> trips -> routes -> counts-sampled routes) passes against the real SUMO 1.28.0 install. Not run for real against SJC: P3.3 needs a real OD matrix (P3.2's gravity model, still blocked on the Geosanja attraction-side proxy, ADR 0017) and real counts (`traffic-counts`, still `deferred`) — until either exists this only has real use against externally supplied or synthetic inputs. `flowrouter` is not wired (no identified use case yet without real counts).
- P3.4 Transit demand and vehicles (buses from P2.6), optional pedestrians/bikes.
- P3.5 Traffic signal programs: field timings where available, else SUMO guessed programs flagged as uncalibrated.
  - **Status 2026-10-29: no-field-data path already in place; field path deferred.** Every real build already runs `netconvert`'s TLS-guessing flags (`default_netconvert_options()`, P2.2) and `arteria network validate` already reports unprogrammed TLS junctions (P2.5); `signal-timing-plans` in `cities/sjc/data-manifest.yaml` is `deferred` (no agency contact authorized) and its own notes already say guessed programs are used and flagged uncalibrated. No new code needed until field timings are obtained.
- P3.6 Baseline scenario definition (`cities/sjc/scenarios/baseline/`), with seeds and replication counts.

**Dependencies:** P2, P1.1 data.
**Deliverables:** baseline scenario runnable headless (`sumo`) and in `sumo-gui`.
**Exit criteria:** baseline runs to completion without gridlock/teleport spikes above a defined threshold; demand totals match OD/control totals within tolerance.
**Risks:** outdated OD survey; boundary demand unknown; signal timings unknown.

### Phase 4 - Calibration and validation

**Goals:** a baseline that matches observed link volumes, turning movements, queues and travel times well enough to compare scenarios (brief Phase 2 calibration targets).

**Features**
- P4.1 Observation dataset: counts by hour/direction, turning movements, travel times (field, probe, or public routing APIs within ToS), queue observations, bus running times.
- P4.2 Detector mapping: place SUMO induction loops/E2/E3 detectors at count locations.
- P4.3 Demand calibration: `routeSampler`, `cadyts`-style or custom OD adjustment; dynamic user equilibrium (`duaIterate.py`) or `marouter`.
- P4.4 Parameter calibration: car-following/lane-change parameters and speed factors; optimizer (e.g. SPSA, Bayesian optimization) over a parameter vector.
- P4.5 Goodness-of-fit metrics: GEH (< 5 for 85% of links), RMSE/MAPE on travel times, scatter plots; split calibration vs. validation data.
- P4.6 Stochastic replication policy: number of seeds, confidence intervals, convergence check.
- P4.7 Calibration report (auto-generated) per city and time window.

**Dependencies:** P3, P4.1 data.
**Deliverables:** calibrated baseline + calibration report; **[ADR 0005: calibration targets and acceptance thresholds]**.
**Exit criteria:** meets agreed thresholds on held-out validation data; replication variance quantified.
**Risks:** insufficient observations (mitigate: travel-time-only calibration, honest uncertainty); long calibration runtimes (mitigate: mesoscopic mode, parallel seeds, smaller windows).

### Phase 5 - Intervention catalog

**Goals:** a constrained, auditable catalog of feasible interventions, each expressible as a deterministic network/demand transform (brief Phase 3).

**Features**
- P5.1 Intervention schema (YAML/JSON): type, target edges/junctions, parameters, cost estimate, complexity, legal/property constraints, safety, emergency access, equity notes, expected beneficiaries/losers, mutual exclusions. **[ADR 0006: intervention catalog schema]**
- P5.2 Transform library (shared): one-way conversion, reversible/tidal lane (time-dependent), bus lane (`allow`/`disallow` vClass), lane reallocation (car to bike/ped), protected bike corridor, pedestrian street/shared street, turn restriction (connection removal), new connector edge (only from a pre-approved list), signal retiming and transit signal priority, intersection redesign templates.
- P5.3 Candidate generation per city: rules (e.g. edges with parallel alternatives for one-way pairs, corridors with bus frequency > X for bus lanes) plus manual expert entries; feasibility filter.
- P5.4 Validity checks after each transform: connectivity, emergency-route continuity, transit-route continuity, pedestrian continuity.
- P5.5 Cost model: unit costs per intervention type (municipal/SINAPI references), editable per city.
- P5.6 Catalog review UI/report (table + map) for planners to approve/reject candidates.

**Dependencies:** P2 (network), P3 (transit routes), P4 for meaningful evaluation.
**Deliverables:** `arteria/interventions/`, `cities/sjc/catalog/`, catalog review report.
**Exit criteria:** every catalog entry applies cleanly to the baseline and passes validity checks; planners have reviewed the SJC catalog.
**Risks:** transforms that silently break routes (mitigate: P5.4 checks + tests); catalog too large for search (mitigate: grouping into corridor packages).

### Phase 6 - Evaluation engine (before/after)

**Goals:** a deterministic, replicated evaluator that turns a scenario (baseline + package) into the brief's Phase 5 metrics with uncertainty. Built before the optimizer, because the optimizer calls it.

**Features**
- P6.1 Scenario runner: apply package, rebuild net (or patch at runtime via TraCI where possible), rerun demand assignment (re-route or DUE), N seeds, collect outputs (tripinfo, edgedata, queue, emissions, FCD as needed).
- P6.2 Metric library: VHT, VKT, mean and P95 travel time, delay and queue length, bus travel time and reliability, ped/cyclist delay/exposure, emissions (HBEFA/PHEMlight via SUMO), crash-risk proxies (SSM device: TTC/PET), emergency-response accessibility (shortest-time isochrones from stations/hospitals), equity by neighborhood/income group (join with census sectors), cost and benefit-cost ratio.
- P6.3 Uncertainty: confidence intervals across seeds, paired comparison vs. baseline, sensitivity to demand +/- X%.
- P6.4 Spillover/boundary analysis for the buffer zone (research question 5).
- P6.5 Results store: tidy tables (Parquet/CSV) per run + run manifest (P0.7).
- P6.6 Report generator: before/after tables, maps, charts (HTML/Markdown/PDF).

**Dependencies:** P4 (calibrated baseline), P5 (transforms).
**Deliverables:** `arteria/evaluate/`, baseline-vs-scenario report for a handful of manually chosen packages. **[ADR 0007: metric definitions and objective set]**
**Exit criteria:** re-running the same scenario + seeds reproduces identical results; hand-picked packages show plausible, explainable effects.
**Risks:** runtime per evaluation too high for optimization (feeds P7 surrogate design); metric definitions contested (fix in ADR).

### Phase 7 - Optimization (upper level)

**Goals:** search the combinatorial package space under constraints (brief Phase 4).

**Features**
- P7.1 Problem formulation: decision vector over catalog entries, constraints (budget, min transit service, emergency access, pedestrian continuity, equity thresholds), objectives (multi-objective). **[ADR 0008: optimization architecture]**
- P7.2 Optimizers: multi-objective evolutionary (NSGA-II via `pymoo`) as the default; Bayesian optimization (e.g. `optuna`/`BoTorch`) for small packages; random/greedy baselines for comparison.
- P7.3 Parallel evaluation backend: process pool locally, optional batch/cluster or cloud runners; caching of already-evaluated packages; checkpoint/resume.
- P7.4 Surrogate model: once enough samples exist, GNN or gradient-boosted surrogate predicting metrics from package + network features; active learning (surrogate pre-screens, SUMO confirms).
- P7.5 Optional RL track: dynamic lane allocation/reversible lanes (CLLA-style, `sumo-rl`) as a separate experiment, not required for the main deliverable.
- P7.6 Pareto front analysis and package ranking (with robustness across seeds/demand scenarios).
- P7.7 Experiment tracking (MLflow or plain run folders + manifests).

**Dependencies:** P6.
**Deliverables:** `arteria/optimize/`, Pareto fronts for SJC, ranked packages.
**Exit criteria:** optimizer beats random and greedy baselines on the agreed objectives within a fixed evaluation budget; top packages are confirmed by full replicated SUMO runs (not surrogate only).
**Risks:** compute cost; surrogate bias; overfitting to a single demand scenario (mitigate: robust objectives over demand variants).

### Phase 8 - Stakeholder communication layer

**Goals:** make results understandable to residents, planners and decision-makers without presenting game output as evidence (brief Phase 6, "Important caution").

**Features**
- P8.1 Web results viewer (static site: maps of before/after, package cards, metric tables, uncertainty) generated from P6.6.
- P8.2 `sumo-gui` recorded videos/screenshots of baseline vs. package.
- P8.3 Cities: Skylines visual twin of the pilot area (map import from OSM/heightmap, recreate selected packages) for workshops; clearly labelled "illustrative".
- P8.4 Workshop kit: slides, feedback forms, mapping of feedback to catalog changes.
- P8.5 Comparison study (research question 7): qualitative/quantitative differences between C:S behaviour and calibrated SUMO results.
- P8.6 3D/2.5D web traffic viewer: replay of SUMO `--fcd-output.geo` over open-data buildings and terrain (optional Google 3D basemap), with zoom/orbit, pause, replay, scrubbing and loop; whole city; labelled "illustrative" **[ADR 0015]**.
- P8.7 Before/after split view and per-edge delay-delta layer in the viewer.

**Dependencies:** P6 (results); P7 for final packages.
**Deliverables:** results site, videos, C:S save files and screenshots, workshop materials.
**Exit criteria:** at least one stakeholder session run with feedback captured.
**Risks:** C:S mods/versions change traffic behaviour [59][64]; audiences treating visuals as forecasts.

### Phase 9 - Policy report and thesis

**Goals:** final deliverables listed in the brief: policy report with implementation phases and monitoring indicators; thesis chapters (pt-BR) kept current via the `thesis-orchestrator` agent and its per-track agents.

**Features**
- P9.1 Policy report: recommended packages, phasing, cost, monitoring indicators, limitations.
- P9.2 Equity and safety assessment chapter.
- P9.3 Thesis integration: progress log and chapters under `docs/thesis/<track>/` updated after each relevant commit.
- P9.4 Reproducibility package: tagged release, environment lock, data manifest, instructions to reproduce key figures.

**Dependencies:** P6-P8.
**Deliverables:** report (PDF), thesis drafts, release `v1.0` of the SJC pilot.
**Exit criteria:** another person reproduces headline results from the release instructions.
**Risks:** results depend on non-public data (mitigate: publish derived/aggregated data and synthetic fallbacks).

### Phase 10 - Multi-city generalization

**Goals:** prove reusability by onboarding a second city with minimal code changes.

**Features**
- P10.1 City onboarding guide and `arteria new-city <name>` scaffolding command.
- P10.2 Open-data-only path (OSM + GTFS + public counts/travel times + synthetic demand) for cities without OD surveys.
- P10.3 Per-city plugin hooks (custom data loaders, local cost tables, local legal constraints) without forking shared code.
- P10.4 Cross-city regression tests (toy city + SJC fixtures) in the `nox` test suite (R1).
- P10.5 Optional MATSim demand step if a city needs activity-based demand (separate ADR per ADR 0001).

**Dependencies:** P0-P7 stable.
**Deliverables:** second city baseline (e.g. a nearby Vale do Paraíba city or a city with open data), onboarding guide.
**Exit criteria:** second city reaches a calibrated baseline and runs the optimizer with no changes to `arteria/` core beyond config/plugins.
**Risks:** hidden SJC-specific assumptions in shared code.

### Cross-cutting

- Versioning: 0.x milestones per phase (0.2 skeleton, 0.3 network, 0.4 calibrated baseline, 0.5 catalog, 0.6 evaluator, 0.7 optimizer, 0.8 communication, 1.0 SJC pilot release).
- Docs: ADRs for each [ADR] mark; CHANGELOG per milestone; napkin for open items only; README/README-eng kept in sync.
- Testing: unit tests on transforms and metrics with toy networks; golden-file tests for network builds; statistical tests for replicated results.

### Planned ADR index (reconciled)

| ADR | Topic | Phase |
|---|---|---|
| 0002 | City-agnostic project structure (incl. task runner = `nox`, single `arteria` CLI) | P0.1 |
| 0003 | City config and data schema | P0.2 |
| 0004 | Data storage and versioning (git vs. external, LFS policy) | P0.6 |
| 0005 | Calibration targets and acceptance thresholds | P4 |
| 0006 | Intervention catalog schema | P5.1 |
| 0007 | Metric definitions and objective set | P6 |
| 0008 | Optimization architecture | P7.1 |
| 0009 | Remote-session boundary: what a Claude app cloud session may read, run, commit and push vs. desktop-only work; toy-fixture outputs are never evidence; SUMO calls sit behind an adapter so the rest of `arteria/` tests without real data, no `sumo`/`netconvert` binary required remotely. Replaces the earlier "CI/CD, runner topology, self-hosted runner security" scope (no Actions runners, no hosted CI are planned) and absorbs the AI-agent scope/permissions question that was going to be its own ADR (same boundary, now that remote work is Claude sessions, so no separate number was needed). Kept as an ADR, not just a rule, because the adapter/fixture split shapes the package architecture | P0.1, P0.5, cross-cutting |
| 0010 | Non-public data handling: storage, retention, publishable derived data | P0.6, P1.2, P4.1 |
| 0015 | Visualization layer: `sumo-gui` 2D MVP, open-data web viewer (deck.gl), optional Google 3D, C:S as hobby track — proposed 2026-10-26, see `docs/visualization-plan.md` | P8.6, P8.7 |
| 0011 | Cities: Skylines edition, mod set, and "illustrative" labelling | P8.3 |
| 0012 | Repository visibility and licensing (public repo; Apache 2.0 code, CC BY 4.0 docs) — written and accepted 2026-10-25, resolving open questions 5 and 7 | P0.8 |
| 0013 | No real OD microdata; synthetic, count-calibrated demand only — written and accepted 2026-10-25, partially resolving open question 1 (OD microdata specifically) | P1.1, P3.1-P3.3, P4.3 |
| 0017 | Zoning and trip-generation data: TAZ delineation from the existing study-area polygons; IBGE Censo population for production, Geosanja zoning as an attraction proxy — proposed 2026-10-29 | P3.1, P3.2 |

## Remote features

*Reframed 2026-10-24. "Remote" means a Claude Code cloud session the owner starts from the Claude phone app, not GitHub Actions. The earlier design (hosted and self-hosted runners, Codespaces, issue-comment ChatOps, gated `workflow_dispatch` runs, Pages and `@claude` workflows) is withdrawn; surviving IDs keep their numbers, see "Retired IDs".*

Remote features are tasks the owner types into the Claude app and gets done end-to-end in one sitting. The session is a sandboxed cloud container with this repo cloned: it can read and write files, run Python, `pytest` and `nox`, install pinned packages from PyPI, commit, push a branch, and open or comment on a PR or issue. It has no GUI, no access to the owner's PC, `ARTERIA_DATA` or `ARTERIA_PRIVATE`, modest time-limited compute, and nothing survives the session except what is pushed. Heavy, GUI, licensed or private work waits for the next desktop session (Local features). **[ADR 0009]** records this boundary.

### What a remote session can and cannot do

| Can | Cannot |
|---|---|
| Read, write and refactor committed files; answer questions about them | See anything not committed: `ARTERIA_DATA`, `ARTERIA_PRIVATE`, the owner's PC |
| Run `ruff`, `mypy`, `pytest`, `nox` against committed toy fixtures | Run `sumo-gui`, `netedit`, Cities: Skylines or any GUI |
| Write and unit-test `arteria/network` and transform code against toy XML fixtures, with real SUMO calls stubbed behind an adapter (ADR 0009) | Install or run the real `sumo`/`netconvert` binary, or build/simulate real city networks: pinned OSM snapshots, demand and observations live outside git |
| Write YAML schemas and configs and validate them | Run calibration or optimizer batches (hours to days, L16-L18) |
| Draft ADRs, docs, CHANGELOG, napkin, roadmap and thesis-track updates | Produce numbers that back a recommendation: only desktop runs with a manifest (P0.7) count as results |
| Commit, push a branch, open/comment on a PR, file an issue | Keep state: the container is discarded after the session |

### Feature catalog

| ID | Task (what the owner types) | What the session does / delivers | Was (Actions framing) | Roadmap IDs |
|---|---|---|---|---|
| R1 | "Run the checks on `<branch>` and fix what fails." | `nox -s lint tests` (ruff, mypy, pytest on toy fixtures, SUMO calls stubbed via the adapter — no real `sumo` binary installed remotely); fixes, commits, pushes | CI on push/PR | P0.3, P0.4, P0.5, P10.4 |
| R3 | "Log a data request to Ipplan for signal plans." / "Add catalog candidate: bus lane on Av. X." / "Record workshop feedback: ..." | Adds or updates the entry in `cities/<city>/data-manifest.yaml` (status, contact, license), the catalog backlog or a GitHub issue; napkin line if it blocks work | Issue forms + labels | P1.1, P1.2, P5.6, P8.4 |
| R4 | "Add a patch making edge X one-way." / "Write the network validation checks." | `netconvert.cfg`, typemaps, `patches/*.xml`, `arteria/network` validation and diff code, tested on a hand-written toy net; the real build and visual check stay at the desk (L9-L11) | Hosted network rebuild | P2.2, P2.3, P2.5, P2.7 |
| R6 | "Queue a calibration run for sjc am-peak." / "Queue 10 seeds of package `bus-lanes-a`." | Napkin item with the exact `arteria`/`nox` command, inputs, expected outputs and what to commit back (aggregated report path); nothing runs remotely | ChatOps `/run` (R5) + run-request form | P4, P6.1, P7 (handoff to L15-L18) |
| R7 | "Review PR #12." / "Review the bus-lane transform diff." | Reads the diff, runs the related tests (P5.4 validity checks on toy nets), posts a review or summary, flags missing tests | Sticky PR metric diff | P5.2, P5.4, P6.2, P6.3 |
| R8 | "Implement GEH and travel-time RMSE with tests." / "Summarize the committed calibration report." | GoF metrics, detector-mapping logic and replication/confidence-interval helpers, tested on synthetic counts; reads an aggregated report committed from the desk and drafts its write-up | Gated calibration run | P4.2, P4.5, P4.6, P4.7 |
| R9 | "Wire NSGA-II over the catalog with a stub evaluator." | Problem formulation, `pymoo`/`optuna` wiring, package cache, checkpoint/resume and Pareto-analysis code, tested against a stub evaluator returning synthetic metrics | Gated optimizer batch | P7.1-P7.3, P7.6, P7.7 |
| R10 | "Health check: new SUMO release? broken links? manifest OK?" | Reads release notes, checks doc links, validates manifest structure; checksums of uncommitted files are verified only at the desk (L2) | Weekly scheduled workflow | P0.3, P0.6, P0.7 |
| R11 | "Build the results viewer from the sample results." | Static-site/report generator code and templates rendered from committed aggregated or sample data; publishing only from `results/published/` after owner review | Pages deploy | P6.6, P8.1 |
| R12 | "Docs pass: sync README/README-eng, check ADR numbering, curate the napkin." | Consistency edits across the README pair, CHANGELOG, ADR index, napkin and roadmap | Docs workflow | cross-cutting |
| R13 | "Draft ADR 0005 from the roadmap and the brief." | ADR in `docs/adr/` per its README format, `Status: Proposed`; the owner accepts | `@claude` Action (ADR part) | every **[ADR]** mark |
| R15 | "Prep release 0.2." | CHANGELOG version bump, release notes, reproduction instructions, lockfile refresh; the tag waits for the desk-side reproduction check (P9.4 exit criteria) | Tag-triggered release | P9.4 |
| R16 | "Onboard city `<name>`." | `cities/<name>/` from `cities/_template/` with stub `city.yaml` and data manifest, validated against the schema, on a branch/PR | Onboarding issue form | P10.1-P10.3 |
| R17 | "Draft the city config schema and validate `cities/sjc/city.yaml`." | Schemas (JSON Schema or pydantic) for `city.yaml`, data manifest, intervention catalog and scenarios, plus validator code and tests | new | P0.2, P0.6, P3.6, P5.1, P5.3 |
| R18 | "Create the `arteria/` skeleton with `arteria doctor`." / "Implement the turn-restriction transform with tests." | Package code (Typer CLI, modules per P0.1) and unit tests on toy fixtures; SUMO calls stay behind an adapter so everything else tests without real data | new | P0.1, P0.3, P0.4, P0.7, P5.2, P5.4, P6.2, P10.3 |
| R19 | "Update the thesis tracks for the last commit." | Runs `thesis-orchestrator` on the `Status: ativo` tracks under `docs/thesis/<track>/`, then commits as `docs(thesis)`; skipped for a purely administrative or pure dev-process/tooling commit (CLAUDE.md) | `@claude` Action (thesis part) | P9.3 |
| R20 | "What would break if I change X?" / "Explain how a package is applied." | Answers from the repo; commits nothing unless asked | new | any |
| R21 | "Draft the corridor scoring matrix." / "Outline the policy report." | Planning text from committed sources: scoring note, problem statements, workshop kit, policy-report and equity sections, with numbers marked TBD until desk results exist | new | P1.3, P1.5, P8.4, P9.1, P9.2 |
| R22 | "Write the FCD-to-trips converter and the viewer." | Converter (`--fcd-output.geo` XML -> trips JSON) and static viewer code, tested against a committed toy FCD fixture; no real SJC data, no Google key | new | P8.6, P8.7 |

**Retired IDs** (not reused): R2 Linux vs Windows SUMO parity (needs the Windows PC; the desk runs `nox -s smoke` there, L2); R5 ChatOps `/run` (merged into R6); R14 Codespaces devcontainer (the Claude session replaces it). No `.github/workflows/` files, issue forms, labels or devcontainer are planned.

**Limits to remember**
- Push before closing the app; the container does not persist.
- Packages come from PyPI through the session's proxy; pin everything in the lockfile so remote and desk environments match.
- Keep the remote suite toy-sized and fast (target under 5 min); anything bigger is a desk job.
- The chat is not a private channel: prompts and pasted text are stored by the Claude app, outside `ARTERIA_PRIVATE`.
- Numbers from toy fixtures or stub evaluators are test data, never findings for the thesis or the policy report.

### What waits for the desktop

| Item | Why not remote | Desk feature |
|---|---|---|
| Real-network builds and simulations (OSM snapshot, demand, baseline) | inputs live in `ARTERIA_DATA`, not git | L8, L9, L13, L15 |
| `netedit`, `sumo-gui`, media capture | GUI | L10, L14, L20 |
| Calibration and optimizer batches | hours to days, checkpointed on the PC | L16-L18 |
| OD microdata, unreleased municipal data, licensed data, credentials | privacy, data-sharing terms, license, security | L24 (`ARTERIA_PRIVATE`), OS credential store |
| Cities: Skylines, mods, save files | proprietary, GUI-only | L21-L23 |
| Raw per-vehicle outputs, large `.net.xml` files | size, re-identification risk | `ARTERIA_DATA`; publish aggregates via L25 |
| Hardware benchmarks and runtime estimates | must measure the real PC | P3/P4 benchmarks |

**Rules**
1. A remote session sees only committed files, and private data never enters the repo or the chat. As a safety net, `.gitignore` still covers `cities/*/private/`, `**/raw/`, `*.fcd.xml`, `outputs/`, `.env`.
2. Data manifest (P0.2, P0.6): each input has `license`, `visibility: public|restricted`, `sha256`. A pre-commit hook (run at the desk and by R1) fails if a `restricted` file's checksum appears in the git index.
3. Remote sessions work on a branch and push; the owner reviews and merges. Commit messages follow CLAUDE.md; after a code, docs or ADR commit, R19 runs the thesis update, except for a purely administrative or pure dev-process/tooling commit (CLAUDE.md) — those need no thesis update.
4. `gitleaks` in pre-commit; GitHub secret scanning and push protection on the repo.
5. Anything the table above blocks becomes an R6 napkin item for the next desk session.
6. The results site publishes only from `results/published/`, filled by an owner-reviewed PR checked against the manifest.

### Phone operating playbook

1. **Start:** in the Claude app, open a Claude Code session on the ArterIA repo and ask "Read the napkin and the roadmap; what is the next remote task?"
2. **One task per session:** type a prompt from the catalog (R1-R21); name the branch when continuing earlier work.
3. **Let it finish:** Claude edits, runs R1, commits and pushes; ask for a PR when the branch is ready.
4. **Review:** read the diff in the Claude app or GitHub Mobile; ask for R7 on anything non-trivial; merge from the phone.
5. **Docs and thesis:** after a substantive commit, ask for R12 and R19 in the same session.
6. **Blocked:** if the task needs SUMO on real data, a GUI, private data or a long run, ask for R6 and stop there.
7. **Before closing:** check that Claude's last reply says the branch was pushed.
8. **Never from the phone:** paste OD/municipal/licensed data or credentials into the chat, or cite toy-fixture numbers as results.

## Local features

*Detailed by the Local sub-planner; ADR numbers reconciled.*

This section covers work on the developer's desk machine: tool installation, local compute, GUI tools (netedit, sumo-gui, Cities: Skylines) and private data. The desk OS is WSL2 (Ubuntu), used as the sole primary environment rather than split with native Windows (ADR 0014) — GUI tools run inside WSL2 via WSLg, and the repo/`ARTERIA_DATA` live on the native Linux filesystem, not under `/mnt/c/...`. Each item is marked **Auto** (fully automatable), **Semi** (scripted with one human checkpoint) or **Manual** (documented procedure). IDs are `L<n>`.

### Entry-point conventions

- **One CLI, `arteria`** (Typer, installed from `pyproject.toml`). Every subcommand takes `--city <name>`, reads `cities/<city>/city.yaml`, writes a run manifest (P0.7) and is idempotent (skips a step when input checksums are unchanged).
- **`scripts/linux/*.sh`** for desk setup and OS-level helpers inside WSL2 (SUMO install, power/sleep inhibition, scheduled runs); no domain logic. `scripts/win/*.ps1` is limited to the one-off WSL2 bootstrap (L6), since the desk runs WSL2 only (ADR 0014).
- **`noxfile.py`** as the cross-platform task runner, so the same commands run on Windows, WSL2 and Linux: `nox -s lint tests smoke build-sjc calibrate-sjc` (recorded in ADR 0002; avoids make/just on Windows). Remote Claude sessions only ever run `lint tests` (R1); `smoke` (real SUMO binary) and everything past it stays desktop-only.
- **`ARTERIA_DATA`** points at the large-data root outside git; **`ARTERIA_PRIVATE`** at a plain local directory outside git for non-public data.

### Recommended local directory layout (outside git)

```
E:\arteria-data\                 (ARTERIA_DATA; excluded from Defender scan, not cloud-synced)
  raw\osm\<city>\<YYYY-MM-DD>\     .osm.pbf + .sha256 (Geofabrik clip or Overpass dump)
  raw\gtfs\<city>\<feed-date>\     GTFS zip + checksum
  raw\dem\<city>\                  DEM tiles for the C:S heightmap
  cache\                           netconvert/duarouter intermediates, keyed by input hash
  runs\<city>\<run-id>\            manifest.json, outputs (tripinfo, edgedata, FCD), logs
  optim\<city>\<study-id>\         optimizer DB (SQLite/Parquet), checkpoints, evaluated-package cache
  media\<city>\                    sumo-gui screenshots/videos, C:S screenshots
  cs\<city>\                       Cities: Skylines saves, map assets, mod-list snapshot
V:\                              (ARTERIA_PRIVATE; plain directory outside git)
  <city>\od-survey\  counts\  signal-plans\  crash\   + README-license.txt per source
```

The repo stores only manifests, checksums, patches, configs and small fixtures (P0.6). Paths resolve as `ARTERIA_DATA / <manifest-relative path>`; no absolute paths are committed.

### Environment and Windows tooling

| ID | Item | Mode | Roadmap | Entry point | Inputs -> Outputs |
|---|---|---|---|---|---|
| L1 | SUMO install and version pin | Auto | P0.3 | `scripts/win/setup-sumo.ps1 -Version <city.yaml>`; preferred: `eclipse-sumo` + `libsumo` + `traci` pip wheels pinned in the lockfile (same version on Windows, WSL2 and remote sessions); MSI/zip fallback for full sumo-gui | `sumo_version` -> binaries, `SUMO_HOME`, version reported by `arteria doctor` |
| L2 | Environment check | Auto | P0.3, P0.5 | `arteria doctor` | -> Python/SUMO/netconvert/osmium versions, `SUMO_HOME`, long paths, disk/RAM, `ARTERIA_DATA` writable, `ARTERIA_PRIVATE` present? |
| L3 | Python environment | Auto | P0.3 | `uv sync`, `nox -s dev` | `pyproject.toml`/`uv.lock` -> `.venv` |
| L4 | Long paths | Manual (one-time, admin) | P0.1 | *N/A under ADR 0014:* repo and `ARTERIA_DATA` live on WSL2 native `ext4`, which has no 260-character path limit; no script needed (see `docs/local/setup-and-daily-commands.md`) | - |
| L5 | Defender exclusions for speed | Manual (admin, user consent) | P4, P7 | *N/A under ADR 0014:* data and binaries live inside the WSL2 ext4 VHDX, which Defender does not scan file by file; no exclusions needed (see `docs/local/setup-and-daily-commands.md`) | - |
| L6 | WSL2 option | Semi | P0.3, P7.3 | `scripts/win/setup-wsl.ps1` + `scripts/linux/setup-sumo.sh` | -> Linux-parity env for long runs; copy data to WSL ext4 for I/O-heavy runs |
| L7 | Long-run power hygiene | Manual | P4, P7 | `scripts/linux/longrun-mode.sh` wrapping long jobs in `systemd-inhibit --what=sleep:idle` (or `caffeine`-style inhibit); the Windows host sleep/active-hours setting is documented as a manual step (WSL2 stops when the host sleeps) | -> machine stays awake overnight |

### Network and data pipelines

| ID | Item | Mode | Roadmap | Entry point | Inputs -> Outputs |
|---|---|---|---|---|---|
| L8 | OSM extraction | Auto | P2.1 | `arteria osm fetch --city sjc --candidate <id> [--pbf-path <file>] [--source-url <url>]` (implemented 2026-10-25: downloads/caches a Geofabrik regional PBF by default, or reuses a local `--pbf-path`; clips it via `osmium extract` to the named `study-areas.geojson` candidate's polygon; an Overpass-sourced small-area `.osm.xml` works too via `--pbf-path`) | candidate polygon (P1.4, `cities/<city>/study-areas.geojson`) -> `cities/<city>/network/raw/<city>-<candidate>.osm.pbf` + sha256 printed on success |
| L9 | netconvert build | Auto | P2.2, P2.3 | `arteria network build --city sjc --osm-pbf <file> [--type-files <files>] [--extra <opt>]...` (implemented 2026-10-25: standard SUMO OSM-import flags, runs P2.5 validation on the result automatically; patches from `cities/<city>/network/patches/manifest.yaml` are applied in a second pass; `--extra`/`--type-files` remain the escape hatch); one-command `arteria network rebuild --city sjc` (snapshot check, clip, build, validate, reference-hash check, provenance manifest in `network/builds/`, diff vs previous net) | PBF -> `cities/<city>/network/<city>.net.xml`, build log, validation error/warning counts |
| L10 | netedit junction fixes exported to patches | Semi | P2.4 | `arteria network edit --city sjc --junction <id>` opens netedit; `arteria network diff-to-patch` turns the before/after plain-XML diff into `patches/NNN-<slug>.*.xml`; human reviews and commits | built net -> patch file + `patches/README` entry (why, evidence) |
| L11 | Network validation and renders | Auto | P2.5, P2.7 | `arteria network validate --city sjc`, `arteria network diff --old <A> --new <B>` | net -> validation report, PNG renders |
| L12 | GTFS import | Semi (route matching checked) | P2.6, P3.4 | `arteria transit import --city sjc --gtfs <zip> --date <day>` (wraps `gtfs2pt.py`) | -> `pt-stops.add.xml`, `pt-vehicles.rou.xml`, unmatched-routes report |
| L13 | Demand generation | Auto | P3.1-P3.3, P3.6 | `arteria demand build --city sjc --window am-peak --method od2trips\|routesampler` | TAZ, OD (private), counts -> trips/routes, totals check |
| L14 | sumo-gui inspection | Manual | P3.6, P4 | `arteria sim gui --city sjc --scenario baseline` | -> visual check; notes to napkin/issues |

### Simulation, calibration and optimization compute

| ID | Item | Mode | Roadmap | Entry point | Inputs -> Outputs |
|---|---|---|---|---|---|
| L15 | Headless replicated runs | Auto | P3.6, P4.6, P6.1 | `arteria sim run --city sjc --scenario <s> --seeds 10 --workers N` (libsumo per process; TraCI on free ports when multi-client) | -> `runs/sjc/<run-id>/` |
| L16 | DUE / calibration | Auto (long) | P4.3-P4.5, P4.7 | `arteria calibrate demand --city sjc`, `arteria calibrate params --optimizer spsa\|optuna --resume` | observations, baseline -> calibrated routes/params, GEH/RMSE HTML report |
| L17 | Optimizer runs | Auto (very long, checkpointed) | P7.2, P7.3, P7.6, P7.7 | `arteria optimize run --city sjc --study <id> --algo nsga2 --budget 2000 --workers N --resume` | -> `optim/sjc/<study>/` (state, package-hash cache, Pareto front) |
| L18 | Scheduled overnight runs | Semi | P4, P7 | `scripts/linux/schedule-run.sh --command "..." --at 22:00` (systemd user timer, `cron`/`at` fallback; the job runs under `systemd-inhibit`) | -> scheduled timer; morning `arteria runs status` |
| L19 | *Retired:* self-hosted GitHub runner | - | - | Not planned: heavy work runs directly at the desk (L15-L18), queued from the phone via R6. ID kept so it is not reused; reopen only through a new ADR if remotely triggered compute is ever wanted | - |

Resource handling: workers default to physical cores - 1; per-worker RAM cap from `city.yaml`; refuse to start workers beyond 80% of free RAM; checkpoints every generation/K trials via atomic rename; `--resume` after sleep, reboot or Ctrl+C.

### Media and Cities: Skylines

| ID | Item | Mode | Roadmap | Entry point | Inputs -> Outputs |
|---|---|---|---|---|---|
| L20 | Screenshots/video capture | Auto (headless), Semi (curated views) | P8.2, P6.6 | `arteria media capture --city sjc --scenario <s> --views views.yaml` (sumo-gui settings file, `--start --quit-on-end`, TraCI `gui.screenshot`, `ffmpeg`) | -> PNG/MP4, side-by-side baseline/package video |
| L21 | C:S heightmap and map prep | Semi | P8.3 | `arteria cs prepare-map --city sjc` (DEM -> 1081x1081 16-bit PNG, OSM road export for importer mod) | -> `cs/sjc/heightmap.png`, `roads.osm`, README noting the ~17.28 km playable square |
| L22 | C:S build and package recreation | Manual | P8.3, P8.5 | Procedure in `docs/local/cities-skylines.md`: import map, fix roads, recreate packages with TM:PE, Move It and a pinned road-importer mod; one save per package; screenshots get an "illustrative" overlay **[ADR 0011]** | -> `cs/sjc/*.crp`, `mods.lock.txt` (Workshop IDs/versions) committed |
| L23 | C:S vs SUMO comparison | Semi | P8.5 | `arteria cs compare --city sjc --package <id>` (manually logged C:S observations vs SUMO metrics) | -> table for research question 7 |

### Visualization viewer

| ID | Item | Mode | Roadmap | Entry point | Inputs -> Outputs |
|---|---|---|---|---|---|
| L26 | Long `sumo-gui` 2D run and Google 3D coverage check | Manual | P8.2, P8.6 | `randomTrips.py -e 86400` then `sumo-gui`; try a Google 3D Tiles sandbox on the SJC viewport; key in `.env`/`ARTERIA_PRIVATE`, never git **[ADR 0015]** | -> go/no-go note on Google coverage and quota |
| L27 | Real FCD export and viewer run | Semi | P8.6 | `sumo --fcd-output.geo` on the real SJC network, convert (R22), serve locally | -> viewer replaying uncalibrated traffic over the whole city |
| L28 | Viewer video capture | Semi | P8.6, L20 | screen/headless capture from the open-data basemap; Google-basemap clips limited to 30 s and labelled "for promotional purposes only" | -> MP4 |
| L29 | Try `sumo-gui` 3D (OSG) | Manual | P8.6 | Windows "all extras" SUMO installer, 30-minute evaluation | -> note on whether it is worth keeping |

### Non-public municipal data

| ID | Item | Mode | Roadmap | Entry point |
|---|---|---|---|---|
| L24 | Private store checks | Manual (setup), Auto (checks) | P0.6, P1.2, P4.1 | plain directory outside git; `arteria data check-private` verifies the directory exists and that no private path is under the repo; pre-commit blocks files matching private-manifest checksums **[ADR 0010]** |
| L25 | Derived/public outputs | Auto | P9.1, P9.4 | `arteria data publish-derived --city sjc` (OD aggregated to zone totals, hourly counts, k-anonymity threshold) -> files safe to commit/release |

Data-sharing terms from the municipality override these defaults.

### Hardware and runtime estimates (to confirm by benchmarks in P3/P4)

| Workload | Assumption | Per-run | Batch |
|---|---|---|---|
| netconvert (corridor + buffer) | 10-30k edges | 1-5 min, < 2 GB RAM | n/a |
| Micro AM-peak run | 2 h, 50-150k vehicles | 3-15 min/core, 1-4 GB | 10 seeds on 8 workers: ~20 min |
| Mesoscopic run | same | 0.5-2 min | used inside the optimizer |
| duaIterate | 30-50 iterations | 2-10 h | overnight (L18) |
| NSGA-II | 2000 packages x 5 seeds = 10k runs | meso ~1 min | ~20 h on 8 workers; micro confirmation of top 20 afterwards |

Suggested minimum: 8 cores/16 threads, 32 GB RAM, 200 GB free SSD for `ARTERIA_DATA`. FCD/emissions outputs are GBs per run: enable them only for chosen runs and prune with `arteria runs gc --keep-tagged`.

### Local daily workflow

1. `arteria doctor`.
2. Read `.claude/napkin.md`, pick the item (runs queued from the phone via R6 first); `git pull`; `uv sync`.
3. `arteria runs status`; resume failed overnight jobs with `--resume`.
4. Make the change; `nox -s lint tests smoke` (toy network, < 2 min).
5. Network work: `arteria network build` + `validate`; netedit fixes only through L10; commit patches, never `.net.xml`.
6. Before long runs: L7, then schedule (L18) or launch with `--workers` and checkpoints.
7. Confirm `git status` shows no data files.
8. Commit aggregated results and reports that remote sessions should read (R8, R11); commit per the commit rules, invoke the `thesis-orchestrator` agent (skip for a purely administrative or pure dev-process/tooling commit, CLAUDE.md), move finished napkin items to `CHANGELOG.md`.

## Open questions

1. **Data access:** will the SJC municipality (Ipplan / Mobilidade Urbana / Urbam) and the transit operator share counts, signal plans and GTFS, and under what terms? **Partially resolved 2026-10-25 for OD survey microdata specifically:** the owner permanently declined to ever request, use or derive from real OD microdata, on privacy/re-identification grounds (ADR 0013) — demand generation (P3) is synthetic and count-calibrated regardless of availability, not contingent on this question for that one source. Counts, signal plans, crash data, emergency routes and GTFS remain separately `deferred` and still decide between the full and the open-data-only path for those sources (P1.2, P10.2, ADR 0010).
2. **Pilot area:** which corridor(s) win the P1.3 scoring, and how large a buffer is tractable for microsimulation versus mesoscopic? **Partially resolved 2026-10-25:** the owner chose all 4 candidates in `cities/sjc/candidate-corridors.md` (Av. Andrômeda↔DCTA, the Jardim Colinas roundabout/Ponte Estaiada, the centro/São Dimas/Vila Adyana one-way maze, and the Anel Viário), in priority order B > D > C > A. This is a qualitative owner call, not the data-backed P1.3 scoring (OD/counts stay deferred); no bounding polygon exists yet for any of the 4.
3. **Calibration thresholds:** accept the GEH < 5 on 85% of links convention, or looser thresholds given sparse data (ADR 0005)?
4. **Objectives:** which objectives are primary (person-delay, transit reliability, safety, emissions, equity), and who signs off on equity metrics and income-group data (ADR 0007)?
5. ~~**Repo visibility:** public or private GitHub repo?~~ **Resolved 2026-10-25:** public (ADR 0012). Does not change the per-source `visibility: public|restricted` data-manifest field (ADR 0003/0004), which still blocks committing any source an agency restricts.
6. **Compute:** is the current dev PC enough (8+ cores, 32 GB RAM), or is a university cluster/cloud budget available for P7 optimization batches?
7. ~~**Code license:** still TBD in the README.~~ **Resolved 2026-10-25:** Apache License 2.0 for code, CC BY 4.0 for docs/research writing/published derived data (ADR 0012).
8. **Cities: Skylines edition:** C:S 1 (mature mods: TM:PE, Move It, importers) or C:S II (less mod support)? Licensing for workshop use (ADR 0011).
9. **RL track:** is the dynamic lane-allocation RL experiment (P7.5) in thesis scope or deferred?
10. **Second city:** which city for P10 (a nearby Vale do Paraíba city, or one with strong open data)?
11. **Remote session limits:** what CPU, RAM and time a Claude app session gets in practice, and whether `nox -s lint tests` stays fast enough to run on every R1 (ADR 0009)?

**Decided:** hosted CI (GitHub Actions) is off the table — R1 (`nox -s lint tests`, run on demand in remote sessions and at the desk) and the desktop's `nox -s smoke` cover every check; no `.github/workflows/` file is planned (ADR 0009).
