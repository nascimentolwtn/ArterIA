# ArterIA Roadmap

Status: Draft (planning only, no code yet). Date: 2026-10-24. Current version: 0.1 (planning).

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
- P0.5 CI skeleton (lint + unit tests + a tiny toy-network SUMO smoke test) - see Remote features.
- P0.6 Data policy: what is committed (configs, small fixtures, manifests, checksums) vs. kept out of git (raw OSM, OD microdata, large outputs); optional Git LFS or external storage (DVC/object storage). **[ADR 0004: data storage and versioning]**
- P0.7 Run provenance: every simulation/optimization run writes a manifest (git SHA, SUMO version, seed, config hash, input checksums).
- P0.8 License decision for code (TBD in README) and data attribution (ODbL for OSM).

**Dependencies:** none.
**Deliverables:** skeleton package, `cities/sjc/city.yaml` stub, `cities/_template/`, CI passing on a toy network, ADRs 0002-0004.
**Exit criteria:** `pytest` and a toy SUMO run pass locally and in CI; a contributor can create `cities/<new>/` from the template in under 30 minutes.
**Risks:** over-engineering before real data is seen (mitigate: keep schemas minimal, version them); SUMO version drift between local Windows and Linux CI (mitigate: pin version, test both).

### Phase 1 - Study-area selection (pilot SJC)

**Goals:** choose one or two pilot corridors/neighborhoods in SJC where data exists and interventions are plausible (brief Phase 1).

**Features**
- P1.1 Source inventory: PlanMob SJC diagnostic/prognostic, Master Plan (LC 612/2018), OD survey, FGV transit-tender studies, Linha Verde, GTFS (if available), counts, signal plans, crash data, emergency routes. Record availability, format, license and contact in the city data manifest.
- P1.2 Data requests to the municipality (Ipplan, Secretaria de Mobilidade Urbana, Urbam) and transit operator; track status.
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
- P2.1 OSM extraction: clip by polygon from Geofabrik/Overpass, pinned snapshot date and checksum.
- P2.2 `netconvert` pipeline with versioned options (typemaps, junction joining, ramp guessing, TLS guessing, sidewalks/bike lanes, public transport stops from OSM).
- P2.3 Network corrections as patch files (`.nod/.edg/.con/.tll` plain XML or `netconvert` patch inputs) applied on top of the generated net, so rebuilds from new OSM are reproducible.
- P2.4 Manual inspection and fixes in `netedit` for complex junctions, exported back into patch files.
- P2.5 Network validation checks: connectivity, dead ends, lane counts vs. field/aerial evidence, one-way status, turn restrictions, speed limits, TLS presence.
- P2.6 Public transport layer: GTFS import (`gtfs2pt.py`) or manual bus routes/stops/frequencies.
- P2.7 Network diff/report (edges, lanes, junctions changed between builds) and map renders.

**Dependencies:** P1.4 (polygon), P0.3.
**Deliverables:** `cities/sjc/network/` build script + patches, generated `.net.xml` (artifact, not necessarily committed), validation report.
**Exit criteria:** a one-command rebuild reproduces the same net from a pinned OSM snapshot; validation report has no blocking issues; key corridors verified against aerial imagery/field notes.
**Risks:** OSM quality gaps in Brazilian cities (lanes, turn restrictions missing); junction-joining artifacts; GTFS unavailable.

### Phase 3 - Demand and baseline scenario

**Goals:** a baseline demand for the chosen time window(s), consistent with available OD data and counts.

**Features**
- P3.1 Zoning: map OD survey zones to the study area and buffer; TAZ file (`.taz.xml`).
- P3.2 OD matrix preparation: from OD survey (expanded), or fallback trip generation (population/jobs) with gravity model; time-of-day profile.
- P3.3 Route/trip generation: `od2trips`, `duarouter`, or `routeSampler` (counts-driven) and `flowrouter`.
- P3.4 Transit demand and vehicles (buses from P2.6), optional pedestrians/bikes.
- P3.5 Traffic signal programs: field timings where available, else SUMO guessed programs flagged as uncalibrated.
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

**Dependencies:** P6 (results); P7 for final packages.
**Deliverables:** results site, videos, C:S save files and screenshots, workshop materials.
**Exit criteria:** at least one stakeholder session run with feedback captured.
**Risks:** C:S mods/versions change traffic behaviour [59][64]; audiences treating visuals as forecasts.

### Phase 9 - Policy report and thesis

**Goals:** final deliverables listed in the brief: policy report with implementation phases and monitoring indicators; thesis chapters (pt-BR) kept current via the `thesis-student` agent.

**Features**
- P9.1 Policy report: recommended packages, phasing, cost, monitoring indicators, limitations.
- P9.2 Equity and safety assessment chapter.
- P9.3 Thesis integration: progress log and chapters under `thesis/` updated after each relevant commit.
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
- P10.4 Cross-city regression tests (toy city + SJC fixtures) in CI.
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
| 0009 | CI/CD, runner topology, self-hosted runner security and remote-execution data boundary | P0.5, P7.3 |
| 0010 | AI agent automation in the repo (Claude Action / Claude Code on the web: scope, permissions, data access) | cross-cutting |
| 0011 | Non-public data handling: storage, encryption, retention, publishable derived data | P0.6, P1.2, P4.1 |
| 0012 | Cities: Skylines edition, mod set, and "illustrative" labelling | P8.3 |

## Remote features

*Detailed by the Remote / GitHub-on-the-go sub-planner; ADR numbers and private-data paths reconciled with the Local section.*

Remote features are the parts of ArterIA the owner can run from a phone through GitHub: issues, PRs, Actions, Codespaces and Claude. Anything heavy, licensed or private runs on the owner's Windows PC, which acts as a self-hosted runner, and only aggregated, publishable outputs come back to GitHub. Free-tier limits below are as known in late 2026 and should be re-checked before they shape a decision. **[ADR 0009]** covers this whole section.

### Runner tiers

| Tier | Runner label | Use for | Limits / cost |
|---|---|---|---|
| T1 hosted | `ubuntu-latest` | lint, tests, toy-net SUMO smoke, docs, reports from committed data | Public repo: free. Private repo: 2,000 min/month on Free (Windows minutes count 2x). 6 h per job. |
| T2 hosted, larger | `ubuntu-latest` + matrix | short baseline runs on open data (OSM + GTFS), few seeds | Same quota; keep each job under 60 min |
| T3 self-hosted | `[self-hosted, windows, arteria-heavy]` | calibration, optimizer batches, anything that reads private data (`ARTERIA_PRIVATE`) | No minute cost. Job limit up to 5 days. Only works while the PC is on. |
| T4 local only | none | `sumo-gui`/`netedit`, Cities: Skylines, raw OD microdata handling | Never triggered from GitHub |

Rule: a job that needs private data or takes more than about 4 h must target T3, and every T3 job is gated by a GitHub Environment with required reviewers.

### Feature catalog

| ID | Feature | Trigger | Runner | Secrets | Artifacts / retention | Roadmap IDs |
|---|---|---|---|---|---|---|
| R1 | CI: ruff, mypy, pytest, toy SUMO smoke (SUMO version pinned) | `push`, `pull_request` | T1 | none | JUnit + coverage, 7 d | P0.3, P0.4, P0.5 |
| R2 | Cross-platform check (Linux vs Windows SUMO) | `pull_request` to main, weekly | T1 + T3 Windows | none | logs, 7 d | P0.5 risk, P10.4 |
| R3 | Issue forms + labels | issue opened | n/a | none | n/a | P1.2, P5.6, P8.4 |
| R4 | Network rebuild from pinned OSM snapshot + validation and diff report | `workflow_dispatch`, PR touching `cities/*/network/**` | T1 | none | `.net.xml` + report, 14 d; job summary with the diff table | P2.1-P2.3, P2.5, P2.7 |
| R5 | ChatOps `/run scenario <name> seeds=<n>` | `issue_comment`, only if `author_association == OWNER` | T1 if open data, else T3 | `GITHUB_TOKEN` | metrics Parquet + manifest, 30 d | P3.6, P6.1, P6.5 |
| R6 | Run-request issue form (city, scenario, seeds, tier) | `issues: opened/labeled` with `run-request` | T1/T3 | same | same; bot comments a metric table on the issue | P6.1, P6.6 |
| R7 | PR metric diff: baseline vs package table as a sticky PR comment | `pull_request` touching `catalog/` or `arteria/interventions/` | T1 (toy + small SJC fixture) | none | 14 d | P5.2, P5.4, P6.2, P6.3 |
| R8 | Calibration run (gated) | `workflow_dispatch` / `/calibrate` | T3, environment `heavy-compute` (owner approval) | private data paths via runner-local env, never repo secrets | GoF report (aggregated only), 90 d; raw outputs stay on PC | P4.3-P4.7 |
| R9 | Optimizer batch with checkpoint/resume (gated) | `workflow_dispatch` (budget, seed, algorithm) | T3, `heavy-compute` | as R8 | Pareto CSV + summary, 90 d; checkpoints local | P7.2, P7.3, P7.6, P7.7 |
| R10 | Scheduled health: SUMO/dependency release check, link check, data-manifest checksum verify | `schedule` (weekly) | T1 | none | summary only | P0.6, P0.7 |
| R11 | Results site (GitHub Pages) from approved aggregated results | push to `results/published/**`, `workflow_dispatch` | T1 | built-in Pages token | Pages site | P6.6, P8.1 |
| R12 | Docs automation: CHANGELOG/README sync check, ADR numbering check, thesis build (pt-BR Markdown to PDF) | PR touching `docs/`, `thesis/`, `README*` | T1 | none | thesis PDF, 30 d | P9.3, cross-cutting |
| R13 | Claude GitHub integration (`anthropics/claude-code-action`): `@claude` for small code/doc edits, ADR drafts, CHANGELOG entries, thesis-student updates **[ADR 0010]** | `issue_comment` / `pull_request_review_comment` mentioning `@claude`, owner only | T1 | `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` | PR opened by the bot | P0.x, P9.3, docs |
| R14 | Codespaces devcontainer (Python + pinned SUMO, headless; optional noVNC for a quick `sumo-gui` look) | manual from phone/browser | Codespaces 2-core | none (public data only) | n/a | P0.3, P2.4 (light), P10.1 |
| R15 | Release / reproducibility package: tag builds environment lock, data manifest, figure-reproduction check | push tag `v*` | T1 | none | release assets | P9.4 |
| R16 | New-city scaffold via "Onboard city" issue form, opening a PR with `cities/<new>/` from the template | issue form + label | T1 | none | PR | P10.1, P10.2 |

**Limits to remember**
- Artifacts and packages share 500 MB on the Free plan for private repos. Set `retention-days` on every upload; never upload full FCD output or `.net.xml` files over about 50 MB.
- Git LFS free quotas are small (roughly 1 GB storage/bandwidth, to verify). Avoid LFS for outputs; use external storage per ADR 0004.
- Codespaces: about 120 core-hours/month and 15 GB storage free on personal accounts. Idle timeout 30 min, auto-delete after 7 days.
- `issue_comment` and `schedule` workflows run from the default branch; test ChatOps changes with `workflow_dispatch` first.
- `repository_dispatch` needs a PAT, so it is not phone-friendly; use it only from local scripts.
- Claude Code on the web and the Claude Action run in cloud sandboxes: same rule as T1, public or committed data only.

### What must stay out of the cloud

| Item | Why | Where it lives |
|---|---|---|
| OD survey microdata, unreleased municipal datasets (counts, signal plans, crash records) | privacy, data-sharing terms | encrypted private store outside the repo (`ARTERIA_PRIVATE`, see L24) |
| Licensed data (commercial probe/travel times, restricted cost tables, paid imagery) | license forbids redistribution | same |
| Credentials (municipal portals, API keys with ToS limits) | security | OS credential store / runner-local `.env`, never in Actions secrets unless the job is T1-safe |
| Cities: Skylines, mods, save files | proprietary, GUI-only | local only; publish screenshots/videos labelled "illustrative" |
| `netedit`/`sumo-gui` editing sessions | GUI work | local; results go back as patch files (P2.3, P2.4) |
| Long calibration/optimization runs (> 4 h) | 6 h hosted job limit, minute quota | T3 runner |
| Raw per-vehicle outputs (FCD, tripinfo) from private-demand scenarios | re-identification risk, very large | local; publish aggregates only |

**Enforcement**
1. Private data never lives inside the repo. As a safety net, `.gitignore` still covers `cities/*/private/`, `**/raw/`, `*.fcd.xml`, `outputs/`, `.env`.
2. Data manifest (P0.2, P0.6): each input has `license`, `visibility: public|restricted`, `sha256`. R10 and a pre-commit hook fail if a `restricted` file's checksum appears in the git index.
3. Runner routing: any step reading `restricted` inputs must use `runs-on: [self-hosted, arteria-heavy]` and `environment: heavy-compute`; `scripts/check_workflows.py` in CI rejects workflows that break this.
4. Self-hosted runner hardening: non-admin Windows service account with access only to the work folder and the private store; never run T3 on `pull_request` from forks; T3 triggers are `workflow_dispatch` and owner-only ChatOps.
5. GitHub secret scanning + push protection, Dependabot alerts, `gitleaks` in pre-commit.
6. Upload allowlist: T3 artifacts may contain only files under `results/aggregated/`.
7. The results site publishes only from `results/published/`, filled by a human-reviewed PR checked against the manifest.

### Proposed workflow files

| File | Purpose |
|---|---|
| `.github/workflows/ci.yml` | Lint, type-check, tests and toy SUMO smoke on push/PR (R1) |
| `.github/workflows/cross-platform.yml` | Weekly Linux vs Windows SUMO parity check (R2) |
| `.github/workflows/network-build.yml` | Rebuild a city net from its pinned OSM snapshot, validate and diff (R4) |
| `.github/workflows/chatops.yml` | Parse owner `/run`, `/calibrate`, `/optimize` comments and dispatch to the right tier (R5) |
| `.github/workflows/run-request.yml` | Handle the run-request issue form and comment results back (R6) |
| `.github/workflows/pr-metrics.yml` | Sticky PR comment with baseline vs package metrics (R7) |
| `.github/workflows/heavy-run.yml` | Gated T3 calibration/optimizer runs with checkpoints (R8, R9) |
| `.github/workflows/scheduled-health.yml` | Weekly SUMO/dependency check, link check, manifest verify (R10) |
| `.github/workflows/pages.yml` | Build and deploy the results site from `results/published/` (R11) |
| `.github/workflows/docs.yml` | CHANGELOG/README sync, ADR numbering, thesis PDF build (R12) |
| `.github/workflows/claude.yml` | `@claude` integration, owner-triggered only (R13) |
| `.github/workflows/release.yml` | Tag builds the reproducibility package (R15) |

Also planned: `.github/ISSUE_TEMPLATE/{run-scenario,data-request,catalog-candidate,onboard-city,bug}.yml`, `.github/labels.yml` (`run-request`, `tier:hosted`, `tier:heavy`, `data-request`, `catalog`, `adr-needed`, `thesis`), `.devcontainer/devcontainer.json` (R14), `CODEOWNERS`.

### Phone operating playbook

1. **Triage:** in GitHub Mobile, filter Issues by `is:open label:run-request,data-request` and re-prioritize with labels.
2. **Small change:** comment `@claude <instruction>` (e.g. "draft ADR 0005 skeleton"); review the PR in the Files view.
3. **Quick run:** open the "Run scenario" form with `tier:hosted`; read the metric table the bot comments back.
4. **Heavy run:** confirm the PC runner is "Idle" (Settings > Actions > Runners), comment `/calibrate sjc am-peak` or `/optimize sjc budget=200`, approve the `heavy-compute` deployment from the notification.
5. **Monitor:** read the job summary in the Actions tab; failure notifications link to the log.
6. **Review a package PR:** read the sticky metric-diff comment, approve or request changes.
7. **Publish:** merge the PR moving aggregated results into `results/published/`; Pages redeploys.
8. **Docs and thesis:** after a merged code/ADR PR, comment `@claude run thesis-student update` and merge the `docs(thesis)` PR.
9. **Light coding:** use a Codespace in the mobile browser for small edits only; stop it when done.
10. **Never from the phone:** anything in the "out of the cloud" table; note it in the napkin for the next desk session.

## Local features

*Detailed by the Local sub-planner; ADR numbers reconciled.*

This section covers work on the developer's Windows 11 machine: tool installation, local compute, GUI tools (netedit, sumo-gui, Cities: Skylines) and private data. Each item is marked **Auto** (fully automatable), **Semi** (scripted with one human checkpoint) or **Manual** (documented procedure). IDs are `L<n>`.

### Entry-point conventions

- **One CLI, `arteria`** (Typer, installed from `pyproject.toml`). Every subcommand takes `--city <name>`, reads `cities/<city>/city.yaml`, writes a run manifest (P0.7) and is idempotent (skips a step when input checksums are unchanged).
- **`scripts/win/*.ps1`** only for Windows-specific setup that needs the OS (registry, Defender, Task Scheduler, runner service); no domain logic.
- **`noxfile.py`** as the cross-platform task runner, so the same commands run on Windows, WSL2 and Linux CI: `nox -s lint tests smoke build-sjc calibrate-sjc` (recorded in ADR 0002; avoids make/just on Windows).
- **`ARTERIA_DATA`** points at the large-data root outside git; **`ARTERIA_PRIVATE`** at the mounted encrypted volume.

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
V:\                              (ARTERIA_PRIVATE; VeraCrypt volume, mounted only while needed)
  <city>\od-survey\  counts\  signal-plans\  crash\   + README-license.txt per source
```

The repo stores only manifests, checksums, patches, configs and small fixtures (P0.6). Paths resolve as `ARTERIA_DATA / <manifest-relative path>`; no absolute paths are committed.

### Environment and Windows tooling

| ID | Item | Mode | Roadmap | Entry point | Inputs -> Outputs |
|---|---|---|---|---|---|
| L1 | SUMO install and version pin | Auto | P0.3 | `scripts/win/setup-sumo.ps1 -Version <city.yaml>`; preferred: `eclipse-sumo` + `libsumo` + `traci` pip wheels pinned in the lockfile (same version on Windows and Linux CI); MSI/zip fallback for full sumo-gui | `sumo_version` -> binaries, `SUMO_HOME`, version reported by `arteria doctor` |
| L2 | Environment check | Auto | P0.3, P0.5 | `arteria doctor` | -> Python/SUMO/netconvert/osmium versions, `SUMO_HOME`, long paths, disk/RAM, `ARTERIA_DATA` writable, private volume mounted? |
| L3 | Python environment | Auto | P0.3 | `uv sync`, `nox -s dev` | `pyproject.toml`/`uv.lock` -> `.venv` |
| L4 | Long paths | Manual (one-time, admin) | P0.1 | `scripts/win/enable-longpaths.ps1` (`LongPathsEnabled=1`, `git config core.longpaths true`) | -> registry/git config |
| L5 | Defender exclusions for speed | Manual (admin, user consent) | P4, P7 | `scripts/win/defender-exclusions.ps1` (exclude `ARTERIA_DATA` and `sumo.exe`/`netconvert.exe`; never the repo or Downloads) | -> Defender prefs, documented rollback |
| L6 | WSL2 option | Semi | P0.3, P7.3 | `scripts/win/setup-wsl.ps1` + `scripts/linux/setup-sumo.sh` | -> Linux-parity env for long runs; copy data to WSL ext4 for I/O-heavy runs |
| L7 | Long-run power hygiene | Manual | P4, P7 | `scripts/win/longrun-mode.ps1` (`powercfg` no sleep on AC, Windows Update active hours) | -> machine stays awake overnight |

### Network and data pipelines

| ID | Item | Mode | Roadmap | Entry point | Inputs -> Outputs |
|---|---|---|---|---|---|
| L8 | OSM extraction | Auto | P2.1 | `arteria osm fetch --city sjc --source geofabrik\|overpass --date YYYY-MM-DD` (Geofabrik `sudeste` PBF + `osmium extract -p polygon.geojson`; Overpass only for small areas) | polygon (P1.4) -> `raw/osm/sjc/<date>/area.osm.pbf` + sha256 in manifest |
| L9 | netconvert build | Auto | P2.2, P2.3 | `arteria network build --city sjc [--osm-date]` | PBF, `netconvert.cfg`, typemaps, `patches/*.xml` -> `sjc.net.xml`, build log, golden hash |
| L10 | netedit junction fixes exported to patches | Semi | P2.4 | `arteria network edit --city sjc --junction <id>` opens netedit; `arteria network diff-to-patch` turns the before/after plain-XML diff into `patches/NNN-<slug>.*.xml`; human reviews and commits | built net -> patch file + `patches/README` entry (why, evidence) |
| L11 | Network validation and renders | Auto | P2.5, P2.7 | `arteria network validate --city sjc`, `arteria network diff --from <A> --to <B>` | net -> validation report, PNG renders |
| L12 | GTFS import | Semi (route matching checked) | P2.6, P3.4 | `arteria transit import --city sjc --gtfs <zip> --date <day>` (wraps `gtfs2pt.py`) | -> `pt-stops.add.xml`, `pt-vehicles.rou.xml`, unmatched-routes report |
| L13 | Demand generation | Auto | P3.1-P3.3, P3.6 | `arteria demand build --city sjc --window am-peak --method od2trips\|routesampler` | TAZ, OD (private), counts -> trips/routes, totals check |
| L14 | sumo-gui inspection | Manual | P3.6, P4 | `arteria sim gui --city sjc --scenario baseline` | -> visual check; notes to napkin/issues |

### Simulation, calibration and optimization compute

| ID | Item | Mode | Roadmap | Entry point | Inputs -> Outputs |
|---|---|---|---|---|---|
| L15 | Headless replicated runs | Auto | P3.6, P4.6, P6.1 | `arteria sim run --city sjc --scenario <s> --seeds 10 --workers N` (libsumo per process; TraCI on free ports when multi-client) | -> `runs/sjc/<run-id>/` |
| L16 | DUE / calibration | Auto (long) | P4.3-P4.5, P4.7 | `arteria calibrate demand --city sjc`, `arteria calibrate params --optimizer spsa\|optuna --resume` | observations, baseline -> calibrated routes/params, GEH/RMSE HTML report |
| L17 | Optimizer runs | Auto (very long, checkpointed) | P7.2, P7.3, P7.6, P7.7 | `arteria optimize run --city sjc --study <id> --algo nsga2 --budget 2000 --workers N --resume` | -> `optim/sjc/<study>/` (state, package-hash cache, Pareto front) |
| L18 | Scheduled overnight runs | Semi | P4, P7 | `scripts/win/schedule-run.ps1 -Command "..." -At 22:00` (Task Scheduler) | -> scheduled task; morning `arteria runs status` |
| L19 | Self-hosted GitHub runner (optional) | Semi | P0.5, P7.3, P10.4 | `scripts/win/setup-runner.ps1` (service, label `arteria-heavy`, `workflow_dispatch`/owner ChatOps only, never fork PRs) **[ADR 0009]** | -> T3 tier of Remote features |

Resource handling: workers default to physical cores - 1; per-worker RAM cap from `city.yaml`; refuse to start workers beyond 80% of free RAM; checkpoints every generation/K trials via atomic rename; `--resume` after sleep, reboot or Ctrl+C.

### Media and Cities: Skylines

| ID | Item | Mode | Roadmap | Entry point | Inputs -> Outputs |
|---|---|---|---|---|---|
| L20 | Screenshots/video capture | Auto (headless), Semi (curated views) | P8.2, P6.6 | `arteria media capture --city sjc --scenario <s> --views views.yaml` (sumo-gui settings file, `--start --quit-on-end`, TraCI `gui.screenshot`, `ffmpeg`) | -> PNG/MP4, side-by-side baseline/package video |
| L21 | C:S heightmap and map prep | Semi | P8.3 | `arteria cs prepare-map --city sjc` (DEM -> 1081x1081 16-bit PNG, OSM road export for importer mod) | -> `cs/sjc/heightmap.png`, `roads.osm`, README noting the ~17.28 km playable square |
| L22 | C:S build and package recreation | Manual | P8.3, P8.5 | Procedure in `docs/local/cities-skylines.md`: import map, fix roads, recreate packages with TM:PE, Move It and a pinned road-importer mod; one save per package; screenshots get an "illustrative" overlay **[ADR 0012]** | -> `cs/sjc/*.crp`, `mods.lock.txt` (Workshop IDs/versions) committed |
| L23 | C:S vs SUMO comparison | Semi | P8.5 | `arteria cs compare --city sjc --package <id>` (manually logged C:S observations vs SUMO metrics) | -> table for research question 7 |

### Non-public municipal data

| ID | Item | Mode | Roadmap | Entry point |
|---|---|---|---|---|
| L24 | Encrypted private store | Manual (setup), Auto (checks) | P0.6, P1.2, P4.1 | VeraCrypt container or `age`-encrypted files (Windows 11 Home lacks BitLocker management); `arteria data check-private` verifies mount and that no private path is under the repo; pre-commit blocks files matching private-manifest checksums **[ADR 0011]** |
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

1. `arteria doctor` (mount the private volume only if today's task needs it).
2. Read `.claude/napkin.md`, pick the item; `git pull`; `uv sync`.
3. `arteria runs status`; resume failed overnight jobs with `--resume`.
4. Make the change; `nox -s lint tests smoke` (toy network, < 2 min).
5. Network work: `arteria network build` + `validate`; netedit fixes only through L10; commit patches, never `.net.xml`.
6. Before long runs: L7, then schedule (L18) or launch with `--workers` and checkpoints.
7. Dismount the private volume; confirm `git status` shows no data files.
8. Commit per the commit rules, invoke the `thesis-student` agent, move finished napkin items to `CHANGELOG.md`.

## Open questions

1. **Data access:** will the SJC municipality (Ipplan / Mobilidade Urbana / Urbam) and the transit operator share OD survey microdata, counts, signal plans and GTFS, and under what terms? This decides between the full and the open-data-only path (P1.2, P10.2, ADR 0011).
2. **Pilot area:** which corridor(s) win the P1.3 scoring, and how large a buffer is tractable for microsimulation versus mesoscopic?
3. **Calibration thresholds:** accept the GEH < 5 on 85% of links convention, or looser thresholds given sparse data (ADR 0005)?
4. **Objectives:** which objectives are primary (person-delay, transit reliability, safety, emissions, equity), and who signs off on equity metrics and income-group data (ADR 0007)?
5. **Repo visibility:** public or private GitHub repo? This changes Actions minutes, artifact storage, fork-PR risk on the self-hosted runner and results-site exposure (ADR 0009).
6. **Compute:** is the current dev PC enough (8+ cores, 32 GB RAM), or is a university cluster/cloud budget available for P7 optimization batches?
7. **Code license:** still TBD in the README; needed before the first release (P0.8).
8. **Cities: Skylines edition:** C:S 1 (mature mods: TM:PE, Move It, importers) or C:S II (less mod support)? Licensing for workshop use (ADR 0012).
9. **RL track:** is the dynamic lane-allocation RL experiment (P7.5) in thesis scope or deferred?
10. **Second city:** which city for P10 (a nearby Vale do Paraíba city, or one with strong open data)?
11. **AI agents in CI:** API key or subscription OAuth token for the Claude Action, and what data it may touch (ADR 0010)?
