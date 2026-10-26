# Visualization layer plan (goal 2)

Status: proposal; recorded as ADR 0015 and roadmap P8.6/P8.7, R22, L26-L29. Written 2026-10-25 from an
Opus planning pass plus the owner's answers below. Claims marked **[unverified]**
were not confirmed.

Goal 2 is partly entertainment and partly stakeholder communication: a 3D or
2.5D view of the real city with animated SUMO traffic, plus before/after
intervention comparison. Numbers still come only from SUMO (goal 1); this layer
is illustrative and must say so on screen (research brief, Phase 6 caution).

## Owner's decisions

- Owns Cities: Skylines 1 (CS1) on Steam, Windows. No time to remodel a city by hand.
- Wants minimal custom code; accepts fidelity limits.
- Output **may be published** → licensing matters (see Google terms below).
- Extent: **whole city** (SJC first), not just one corridor.
- Replay of random/finished traffic is enough; no interactive control needed.
- CS1 is acceptable as a **separate hobby track**: imported terrain + plain
  roads, areas zoned by hand later in free time.
- Google Maps Platform billing account (API key) is acceptable.

## Decided path (owner, 2026-10-26)

1. **MVP: `sumo-gui` 2D with a long run.** Generate random trips with a large
   end time (`randomTrips.py -e <seconds>`, e.g. 86400 for a simulated day) and
   watch in `sumo-gui` (speed, pause, follow a vehicle). Endless variant: a small
   TraCI script that keeps inserting vehicles **[untested]**. Recipe to be added
   to `docs/local/sjc-quickstart.md` once verified on a real SJC network.
2. **Later: open-data web viewer (option B, 2.5D)** playing a recorded long run
   on a loop. Required controls: zoom/pan/orbit into interesting areas, pause,
   replay/restart, timeline scrubbing, loop. These map directly onto deck.gl's
   `TripsLayer` (current time is app-controlled) plus the map's own camera.
3. Google 3D (option A) stays optional for private viewing; CS1 stays a hobby track.

## Strategies considered

**A. Web viewer: deck.gl + Google Photorealistic 3D Tiles + SUMO playback.**
Photogrammetric 3D SJC in the browser, cars as moving trails or 3D models, free
orbit camera. Traffic: `sumo --fcd-output.geo` (lon/lat positions, off by
default) → small Python step → deck.gl `TripsLayer`; buildings via `Tile3DLayer`
(official Google 3D Tiles guide); CARTO documents a terrain extension that drapes
layers on the tiles. `sumolib` ships an FCD → kepler.gl JSON converter usable as
a reference. Before/after: two runs with the same seed, toggle or synchronized
split view, optional edge coloring by delay change. About 150 lines Python +
250 lines JS/HTML. Limits: cars are overlays (near-ground photogrammetry looks
melted); replay only. Runs in any browser (Windows or WSLg).
Google Map Tiles terms: overlaying own objects is allowed; logo and attribution
required; no pre-fetching, caching or offline use; promotional videos ≤ 30 s and
labelled "for promotional purposes only"; API key never committed. Coverage of SJC
**[unverified]**; free quota **[unverified]**.

**B. Same viewer, open data only: MapLibre + extruded OSM/Overture buildings +
terrain.** 2.5D block buildings with hillshade, same `TripsLayer` cars. Less
photoreal, but no API key, works offline, no recording limits, publishable under
ODbL. Overture serves buildings as PMTiles; height completeness for Brazil
**[unverified]** (expect default heights). Shares ~80% of A's code.

**C. Cities: Skylines 1.** Roads via the "OpenStreetMap Import" workshop mod
(ID 1957515502; 2024 comments report glitchy nodes and null-reference errors,
unconfirmed on the current patch). Terrain via the map editor's heightmap import
(terrain.party has been down at times; Skydark is an alternative). Blocker:
buildings and traffic only appear in zoned areas, so the import yields plain
roads until zoned by hand. No known mod feeds SUMO vehicles into the game; the
traffic shown would be the game's own, uncalibrated. Before/after = one save per
package, edited by hand (TM:PE, Move It).

**D. `sumo-gui` 3D (OSG).** The pip wheel has no OSG. The Windows "all extras"
installer includes it, or build from source in WSL. Crude 3D network, no
buildings, live TraCI. 30-minute try only.

**E. Unity/Unreal + Cesium + TraCI, or CARLA.** Existing bridges: BME
SUMO-Unity3D-connection, Sumonity, SUMO-Unity-VR-traffic-simulation; CARLA has an
OSM map pipeline and SUMO co-sim. Best "game" feel, but weeks of work and heavy
installs; CARLA struggles at city scale.

**F. Minor.** Google Earth Pro KML `gx:Track` (unsuitable beyond a few hundred
vehicles **[unverified]**); Blender + blosm (OSM buildings only; Google tiles
can't be stored); `sumo3Dviz` batch video renderer (arXiv 2604.19194,
**[unverified]** details); `sumo-web3d` is archived, skip.

| | Real-looking SJC | SUMO traffic | Before/after | Custom code | No manual modelling | Terms risk | First visual |
|---|---|---|---|---|---|---|---|
| A deck.gl + Google 3D | High | Replay | Toggle / split | ~400 lines | Yes | Medium | ~1 evening |
| B deck.gl + OSM/Overture | Medium (2.5D) | Replay | Toggle / split | +~50 on A | Yes | None (ODbL) | ~1 evening |
| C CS1 + mods | Medium after zoning | No | Manual saves | 0 (C# mod for SUMO cars) | **No** | Low | Days |
| D sumo-gui OSG | Low | Live | Two runs | 0 | Yes | None | ~1 h |
| E Unity/Unreal/CARLA | High | Live | Two worlds | High | Partly | Medium | Weeks |
| F Earth/Blender | Medium | Export | Two files | ~200 lines | Yes | Medium | 1–2 days |

## Recommendation (adjusted for "may be published" and "whole city")

- **Build one viewer with a basemap switch, A and B sharing code.** Because the
  output may be published, make **B (open data) the default for anything public or
  recorded beyond 30 s**, and use **A (Google 3D) for private/personal viewing and
  short labelled clips**. Re-read Google's policy before any public embed.
- **CS1 as a parallel hobby track**, decoupled from the SUMO pipeline: terrain +
  OSM roads imported once, zoned in free time.
- **Whole-city scale** stresses both SUMO and the browser: plan to subsample
  vehicles or aggregate trajectories for display, and to load the FCD in chunks.
  Decide the trade-off once real SJC FCD output exists.

## Phases

- **V0 (~1 h, optional):** check Google 3D coverage of SJC in a sandbox; try
  Windows `sumo-gui` 3D (extras build).
- **V1:** `--fcd-output.geo` on the quickstart `randomTrips` run → converter →
  static HTML served locally (`python -m http.server`). First moving cars.
- **V2:** before/after toggle + split view; edge delta coloring from per-edge
  output; permanent "illustrative, uncalibrated" banner.
- **V3:** 3D car models, camera presets, video capture (B for clips > 30 s).
- **V4 (optional):** live TraCI over a websocket (not needed per owner).
- **Hobby track:** CS1 terrain + roads import; zoning by hand.

## Suggested roadmap items (not yet added to `docs/roadmap.md`)

- P8.6 "3D web traffic viewer (FCD playback over 3D city)"; P8.7 "Before/after
  split view + edge-delta layer".
- Remote-possible (ADR 0009): R22 write the FCD-to-trips converter and viewer
  against a committed toy FCD fixture.
- Desk-only: L26 Google 3D coverage check + API key setup (key in `.env` or
  `ARTERIA_PRIVATE`, never git); L27 real FCD export + viewer run; L28 viewer
  video capture (extends L20; Google footage ≤ 30 s); L29 try `sumo-gui` 3D on the
  Windows extras build.
- Rescope L21–L23 (CS1) to optional and note the OSM Import mod's unreliability.
- ADR warranted (renderer choice, Google terms, "illustrative" labelling): written as ADR 0015 (0011 stays reserved
  for the C:S edition/mod-set decision).

## Open

- Billing/quota details for the Google key **[unverified]**.
- Whether Google has 3D coverage for SJC **[unverified]**.
- Overture building-height completeness for Brazil **[unverified]**.
