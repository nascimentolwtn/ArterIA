# 0013. No real OD microdata; synthetic, count-calibrated demand only

Date: 2026-10-25
Status: Accepted

## Context

`cities/sjc/data-manifest.yaml`'s `od-survey-microdata` entry had been
sitting as `visibility: restricted`, `status: deferred` since the project's
first data inventory (P1.1): restricted because "data-sharing terms"
would likely limit redistribution, deferred because the owner chose not to
contact any SJC agency yet (P1.2). The roadmap's risk mitigation and ADR
0002's multi-city note already treated an open-data-only demand path
(OSM + GTFS + public counts + synthetic demand, P10.2) as first-class, not
a fallback — but only as a contingency for *if* the OD survey were never
released, not as a standing choice independent of availability.

The owner explored, with another AI session outside this repo, exactly why
OD *microdata* (household/trip-level, as opposed to the published
aggregated `od-survey-atlas`) tends to carry redistribution restrictions.
The conclusion reached there, and adopted here: the main reason is not
primarily commercial value, but privacy — home/work/school location,
income and household composition, and precise daily trip timing can be
inferred or re-identified from zone + socioeconomic + timing combinations
even without names, on top of survey-consent limits and the agency's own
contractual confidentiality. That reframes this from a data-availability
question (will Ipplan release it, under what terms) to a scope decision
this project can make unilaterally: never touch real OD microdata at all,
regardless of whether it ever becomes available.

## Decision

- ArterIA will never request, receive, retain, publish, or derive data
  from (including by randomizing or anonymizing a real copy of) OD survey
  microdata, for SJC or any future city onboarded under this layout. This
  is a permanent policy choice, not contingent on what Ipplan would or
  would not release.
- `cities/sjc/data-manifest.yaml`'s `od-survey-microdata` entry moves to
  `status: declined` — a new `ManifestStatus` value (`arteria/config.py`),
  distinct from `deferred`: `deferred` still expects a possible future
  request once the owner lifts it, `declined` does not. `cities/sjc/data-requests.md`
  drops the OD-microdata ask from Draft 1 (Ipplan) accordingly;
  `od-survey-atlas` (the aggregated, public version) is unaffected and
  stays on that draft.
- Demand generation (roadmap P3) builds a synthetic, privacy-preserving,
  count-calibrated scenario instead, using tools already named in the
  roadmap rather than new ones:
  1. Network build for the selected study area (P2), as already planned.
  2. With no real OD survey (now permanent for SJC, not just deferred),
     trip generation falls back to the gravity-model path already named in
     P3.2 (population/jobs, time-of-day profile), not a real OD matrix.
  3. **`routeSampler`** (already named in P3.3/P4.3) is the primary
     counts-driven demand/calibration tool, matching simulated flows to
     whatever aggregate counts/screenline/peak-hour data are actually
     available (per ADR 0003's `time_windows`, including the qualitative
     peak-hour basis accepted for corridors A/D, ADR 0003's addendum).
     `od2trips`/`duarouter`/`flowrouter` (P3.3) and `cadyts`-style or
     `duaIterate` iterative adjustment (P4.3) fill out the same pipeline.
  4. `randomTrips.py` keeps its existing, narrower role (per
     `docs/local/sjc-quickstart.md` and the napkin's existing caution): a
     routability sanity check during draft network validation (P2), never
     the source of demand for a real scenario or a cited finding. This ADR
     does not promote it to a demand-generation tool.
  5. SUMO's runtime `<calibrator>` elements may supplement `routeSampler`
     for dynamic flow-matching during a run, within P4.3's existing scope
     — an implementation detail, not a new roadmap item.
  6. Validation (P4) checks the calibrated scenario against independent
     held-out observed data (counts, speeds, queues, travel times) using
     the existing GEH/RMSE acceptance criteria
     (`arteria/calibration/goodness_of_fit.py`), unchanged by this ADR.
- **Terminology:** any report, chapter, or figure describing this scenario
  calls it a "synthetic traffic scenario calibrated to observed flows",
  "count-calibrated demand scenario", or "representative peak-hour
  scenario" — never "the real traffic of São José dos Campos" or
  equivalent language implying it reconstructs actual individual trips.
- **Scope limits, acknowledged up front rather than discovered later:**
  this demand model is adequate for interventions whose evaluation turns
  on corridor-level demand loading — one-way conversions, reversible
  lanes, lane reallocation, turn restrictions, signal retiming, bus-lane
  pilots, local intersection redesigns (i.e. most of the P5.2 catalog). It
  is not adequate, without real OD structure, for: new connectors'
  network-wide benefit claims, large land-use changes, transit-oriented
  development, equity analysis by neighborhood, emergency-evacuation
  modeling, or long-distance commuting behavior. In particular, any future
  equity objective (roadmap open question #4, ADR 0007, not yet written)
  that wants to score interventions by neighborhood-level benefit
  distribution needs a different data basis (e.g. IBGE census aggregates)
  to survive this limitation — it cannot lean on this synthetic demand for
  that claim.

## Consequences

- Easier: every future session has one demand-generation path instead of
  two (real-OD vs. fallback) to maintain or reason about; no LGPD,
  informed-consent, or re-identification exposure for the whole pilot,
  since no household/trip-level microdata is ever handled or stored;
  `cities/sjc/data-requests.md`'s Draft 1 is shorter and never asks for
  something the project won't use even if offered.
- Harder: the pilot cannot support claims that depend on real
  trip-purpose/desire-line structure — a reviewer asking "where do these
  trips actually come from" gets "a calibrated gravity-model/routeSampler
  fit to counts," not a survey-backed answer. The scope-limits list above
  has to be respected by every later phase (P5 catalog review, P6 metrics,
  P7 optimizer framing), not just restated once here.
- Risk: a future session must not quietly treat `od-survey-atlas`
  (aggregated, public, still `deferred` pending contact) as equivalent to
  microdata, nor reopen the OD-microdata question under a different
  manifest id without a fresh ADR — the `declined` status exists precisely
  so this doesn't need re-deciding every time demand generation comes up.
