# ArterIA

AI-assisted decision support for street-network planning, designed to be reusable in any city. Streets are the city's arteries, and ArterIA helps test which changes actually improve them.

ArterIA does not "invent streets". It searches a constrained catalog of feasible interventions (one-way conversions, reversible lanes, bus lanes, lane reallocation, protected bike and pedestrian corridors, turn restrictions, a few new connectors) and evaluates each package against a calibrated baseline simulation.

## How it works

1. **Baseline:** build the study area from OpenStreetMap in SUMO, then calibrate with local traffic counts, travel times and origin-destination data.
2. **Candidates:** define interventions with cost, legal limits, safety, emergency access and equity notes.
3. **Optimization:** an upper-level optimizer (genetic algorithm, Bayesian optimization or RL, with GNN surrogates later) picks packages. SUMO acts as the lower level and returns the traffic response.
4. **Before/after:** compare vehicle-hours, 95th-percentile travel time, bus reliability, emissions, safety proxies and equity by neighborhood.
5. **Communication:** optional visual storytelling for stakeholders (for example with Cities: Skylines), not used as quantitative evidence.

## Using it in your city

Each city lives in its own folder under `cities/<city-name>/` with its own data, calibration and scenarios, while the optimizer and evaluation code stay shared. To add a city, you need an OSM extract of the study area, some traffic counts or travel times, and any available demand data.

## Pilots

- **São José dos Campos, SP, Brazil** (first pilot, in progress)

## Stack

SUMO (netedit, sumo-gui, TraCI), Python, OpenStreetMap, sumo-rl or custom optimizers.

## Status

Early stage, version 0.3 (network-build tooling: OSM fetch, `netconvert` build/validate, study-area polygons, the first intervention transforms). Next steps: run the real OSM-to-network pipeline for SJC at the desk and move to baseline calibration. See `CHANGELOG.md` for what's changed.

## Data and credits

Map data © OpenStreetMap contributors (ODbL). Each city's local sources are credited in its own folder.

## License

TBD
