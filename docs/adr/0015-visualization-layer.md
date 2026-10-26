# 0015. Visualization layer: sumo-gui 2D first, open-data web viewer second, Google 3D optional

Date: 2026-10-26
Status: Proposed

## Context

Goal 2 of the project (entertainment plus stakeholder communication) needs a
3D or 2.5D view of the real city with animated SUMO traffic, before/after
comparison, and long-running playback. The owner has no time to remodel a city
by hand, accepts fidelity limits, wants minimal custom code, may publish the
result, and wants the whole city rather than one corridor. Cities: Skylines 1
cannot meet this on its own: imported OSM roads stay empty until zoned by hand,
and no known mod feeds SUMO vehicles into the game. The pip `eclipse-sumo`
wheel has no OSG, so `sumo-gui` has no 3D view. Google Photorealistic 3D Tiles
forbid caching and limit promotional video to 30 seconds. Full comparison:
`docs/visualization-plan.md`.

## Decision

1. **MVP:** `sumo-gui` 2D with a long random-trips run (`randomTrips.py -e`).
2. **Main 2.5D viewer:** a static web viewer (deck.gl `TripsLayer`) replaying
   SUMO `--fcd-output.geo` output over open data (MapLibre, extruded OSM/Overture
   buildings, terrain), with zoom/pan/orbit, pause, replay, scrubbing and loop.
   Open data is the default for anything public or recorded.
3. **Google 3D Tiles** is an optional basemap for private viewing and short
   labelled clips only; the API key never enters git.
4. **Cities: Skylines 1** is a separate hobby track (terrain + OSM roads, zoning
   by hand); it is not part of the evidence or viewer pipeline. ADR 0011 stays
   reserved for its edition/mod-set/labelling decision.
5. Every visual shows an "illustrative, uncalibrated" label; quantitative claims
   come only from SUMO results (research brief, Phase 6).

## Consequences

- No hand modelling and little custom code (about 400 lines), and one viewer
  serves both goals.
- Cars are overlays on extruded buildings, so fidelity is below a game or
  photogrammetry view, and whole-city display may need vehicle subsampling or
  chunked loading.
- Playback is replay only; live TraCI control is deferred.
- Open risks: Google 3D coverage of SJC, Google quota/billing, and Overture
  building-height completeness in Brazil are unverified.
