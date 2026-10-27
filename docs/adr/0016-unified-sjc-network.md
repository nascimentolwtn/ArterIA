# 0016. One unified SJC network; candidate corridors are evaluation areas, not separate networks

Date: 2026-10-26
Status: Accepted

## Context

Candidates B, D, C and A each have a draft polygon (`cities/sjc/study-areas.geojson`).
Built separately with `osmium extract` + `netconvert` (SUMO 1.28, default flags),
they give:

| Net | Edges | Largest strongly connected component |
|-----|-------|--------------------------------------|
| B   | 2,074 | 85.1% |
| D   | 1,203 | 69.9% |
| C   |   919 | 86.9% |
| A   | 2,256 | 88.3% |
| Envelope of all four | 11,035 | 94.0% |

The polygons are not independent: B and C bounding boxes touch A (B was drawn to
connect to A's Anel Viario, owner decision 2026-10-25), and D is about 0.3 km
from A. Every corridor leans on A for through traffic. Clipping each one alone
cuts those flows at an arbitrary boundary.

## Decision

1. Build **one** SJC network, clipped to the rectangular envelope of all
   candidate polygons (`arteria osm fetch --city sjc --candidate all`, then
   `arteria network build --osm-pbf cities/sjc/network/raw/sjc-all.osm.pbf`).
   It writes `cities/sjc/network/sjc.net.xml`.
2. Candidates B, D, C and A stay as **named evaluation areas** (edge sets and
   later TAZs selected by polygon) inside that network. Interventions, metrics
   and before/after reports are scoped per area; demand, calibration and the
   baseline are done once.
3. Per-candidate extracts (`--candidate b|d|c|a`) remain available for quick
   visual checks, but are not a basis for results.

## Consequences

- Spillover between corridors (for example B or C interventions loading A) is
  measured instead of cut off, and the main routable component is larger.
- The envelope includes the gaps between corridors, so the net is about 11k
  edges (26 MB `.net.xml`), roughly 1.7x the sum of the four polygon nets. Runs
  are slower; if this hurts the optimizer loop, add a smaller corridor-only
  net later as a derived artifact. The unified net stays the source of truth.
- Hard to reverse mainly because the baseline, demand and calibration will be
  tied to this network's edge ids. Decide before Phase 3 (demand).
- The envelope is still a clipped extract: boundary dead ends and an unrouted
  tail (6% outside the main component) remain. Network validator adaptation to
  real networks is tracked separately in `.claude/napkin.md`.
- Polygons are drafts; if they move, rebuild and re-pin edge ids.

## Update 2026-10-27

Owner feedback extended the B (south through Jd. Satélite) and C (west/south-west
around Parque Vicentina Aranha) polygons. The envelope was rebuilt: 14,225 edges,
6,655 junctions, 93.1% of junctions in the main component, 0 validation errors
(the 11,035-edge figure above is the earlier, smaller envelope). Edge ids changed.
