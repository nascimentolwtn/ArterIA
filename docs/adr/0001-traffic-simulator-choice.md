# 0001. Traffic simulator choice

Date: 2026-10-24
Status: Accepted

## Context

ArterIA needs a calibrated baseline traffic model to evaluate before/after impacts of candidate street-network interventions (one-way conversions, lane reallocation, bus lanes, new connectors, etc.) under traffic-assignment constraints, per the project's recommended method (see `docs/research-brief-sjc.md`, Phase 2 and Phase 4).

Candidate simulators considered:

- **SUMO** (Simulation of Urban MObility) — open-source, microscopic/mesoscopic, strong OSM import (`netconvert`), TraCI API for runtime control and RL/optimization loops, active community, used in most of the academic AI-traffic-optimization literature surveyed in the research brief (CLLA, DRL signal control, RL lane allocation).
- **MATSim** — open-source, agent-based, strong for city-scale demand modeling and policy scenarios, but heavier setup for corridor-level microscopic detail (lane geometry, turn restrictions).
- **AIMSUN** and **PTV Vissim** — commercial, strong calibration tooling and industry acceptance, but licensing cost is a barrier for an open, reusable, city-agnostic project.
- **TransModeler** — commercial, similar licensing barrier.

Project constraints that matter here: the project must stay free/open-source to be reusable across cities (see README "Using it in your city"), must support an API for an upper-level optimizer to query traffic response to candidate interventions (TraCI/Python), and must be able to build a network directly from OpenStreetMap for any pilot city, starting with São José dos Campos.

## Decision

Use **SUMO** as the baseline traffic simulator and lower-level traffic-assignment engine for all pilot cities.

- Networks are built from OpenStreetMap extracts via `netconvert`/`netedit`.
- Runtime interaction (feeding candidate interventions, reading back travel times, queues, emissions proxies) goes through **TraCI**.
- MATSim is not ruled out long-term for city-scale demand generation (trip/OD estimation) if corridor-level OD data proves insufficient, but it is not the traffic-assignment engine.
- Commercial simulators (AIMSUN, Vissim, TransModeler) are out of scope: licensing cost conflicts with the project's goal of being freely reusable by any city.

## Consequences

- Easier: free and open city onboarding (no license cost), direct OSM-based network builds, straightforward integration with Python-based optimizers (genetic algorithms, Bayesian optimization, RL) via TraCI, alignment with the bulk of reviewed academic work (easier to reuse/replicate published methods).
- Harder: SUMO's calibration tooling is less mature than commercial alternatives — demand calibration (matching link volumes, turning movements, transit loads) will need custom scripting rather than built-in calibration wizards.
- Risk: if a pilot city's demand modeling needs outgrow corridor-level OD estimates (e.g. requires full activity-based synthetic populations), a MATSim demand-generation step feeding into SUMO assignment may be added later as a separate ADR, not a replacement of this one.
