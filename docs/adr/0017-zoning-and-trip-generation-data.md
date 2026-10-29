# 0017. Zoning and trip-generation data for the gravity-model baseline

Date: 2026-10-29
Status: Proposed

## Context

ADR 0013 already decided, in principle, that SJC's baseline demand (roadmap
P3) is built as a synthetic, count-calibrated scenario via a gravity-model
fallback (population/jobs, time-of-day profile) rather than a real OD
survey, with `routeSampler` doing the counts-driven calibration afterward.
That ADR named the *pipeline* but not the *data*: it does not say what
stands in for "population" and "jobs" for SJC.

Checking `cities/sjc/data-manifest.yaml` for Phase 3 confirms the gap: the
manifest has street geometry (`osm-network-extract`), zoning/Master Plan
*map* layers (`geosanja-plano-diretor-zoneamento`), and street-face
geometry (`ibge-faces-logradouros`) — nothing demographic (population by
area) or economic (jobs, establishments). `traffic-counts` and
`signal-timing-plans` are also still `deferred` (restricted, pending
agency contact the owner has not authorized), so there is no real jobs
dataset reachable without contacting an agency, consistent with the
project's standing no-contact-yet policy (roadmap P1.2).

Separately, P3.1 (zoning) needs a TAZ (traffic analysis zone) delineation.
The project already has four aerial-verified study-area polygons
(`cities/sjc/study-areas.geojson`, candidates a/b/c/d, CHANGELOG [1.1]) and
a unified network envelope larger than their union (ADR 0016). Inventing a
new zone layer from scratch would duplicate geometry the project has
already vetted.

## Decision

- **TAZ delineation**: one TAZ per enabled study-area candidate
  (`a`, `b`, `c`, `d`), built directly from `cities/sjc/study-areas.geojson`,
  plus one `external` TAZ for every network edge outside all four
  polygons (through traffic and the rest of the unified envelope). No new
  zone geometry is drawn; the TAZ layer reuses the same polygons already
  used for corridor drafting (`cities/sjc/corridors/`) and aerial
  verification.
- **Production weight (population)**: IBGE Censo 2022 population by census
  tract ("setores censitários"), a public, self-service download — same
  agency and no-contact precedent already used for
  `ibge-faces-logradouros`. Recorded as a new `data-manifest.yaml` entry,
  `ibge-censo-populacao-setores`, `status: deferred` until the real file is
  fetched and hashed (not done in the commit that proposes this ADR).
- **Attraction weight (jobs proxy)**: no public jobs/employment dataset is
  reachable without contacting an agency (RAIS/CAGED-style data is not
  self-service). Instead, the already-downloaded
  `geosanja-plano-diretor-zoneamento` land-use/zoning classification
  (commercial/institutional/mixed-use vs. purely residential) stands in as
  a density-weighted proxy for attraction. This is explicitly a proxy, not
  a jobs count.
- This ADR only decides *which data* backs P3.2's gravity model; it does
  not change ADR 0013's pipeline (gravity model → `routeSampler` against
  whatever counts exist → GEH/RMSE validation) or its scope limits.

## Consequences

- Easier: P3.1 (TAZ zoning) can be implemented and run for real immediately,
  independent of this ADR's acceptance, since TAZ geometry only depends on
  already-accepted study-area polygons. P3.2's real implementation (fetch
  the IBGE census file, join it to TAZs, build the OD matrix) has a named
  data source to build against instead of stalling on "which data."
- Harder: the attraction side is a land-use proxy, not real employment
  counts, so trip attraction in commercial/institutional TAZs is only as
  good as the Master Plan zoning classification — it will not capture
  within-zone variation (e.g. one large employer vs. many small shops) and
  cannot support a jobs-based equity or economic-impact claim. This sits
  inside ADR 0013's existing scope-limits list (no neighborhood-level
  equity claims from this demand model without real census data); this ADR
  does not widen or narrow that list.
- Risk: if IBGE's Censo 2022 setor-level population file is not cleanly
  downloadable for SJC the way `ibge-faces-logradouros` was, P3.2 has no
  immediate population source either and the gravity model would need a
  coarser fallback (e.g. municipality-level population split by TAZ area) —
  flagged in the napkin, not resolved here.
