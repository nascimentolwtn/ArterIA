# 0011. Cities: Skylines edition, mod set, and "illustrative" labelling

Date: 2026-11-03
Status: Proposed

## Context

ADR 0015 decided C:S 1 (CS1) stays a hobby track, decoupled from the SUMO
evidence pipeline, scoped down to "terrain + plain roads imported, zoned by
hand later." That ADR reserved this number for the edition/mod-set/labelling
decision itself, since the mod research hadn't been done yet. It has now:
the owner's CS1 workflow research (terrain.party heightmaps, OSM import mods,
Overlay reference imagery) confirms the mod-driven approach and adds two
details ADR 0015 didn't have — a concrete road-import mod comparison, and
CS1's hard terrain-tile size limit.

CS1's importable terrain tile tops out at about 18 km square (a terrain.party
export at that size is "roughly 1:1 scale with the game"). The whole SJC net
(`cities/sjc/network/sjc.net.xml`, `origBoundary`) is about 38 x 28 km. So
"whole city" (ADR 0015's scope decision for the *web viewer* track) does not
transfer to CS1: only one corridor-sized crop fits per CS1 map, regardless of
mods — the "81 tiles" mod unlocks more of the *existing* terrain square's
outer tiles, it does not enlarge the terrain itself.

Road-import options compared:
- **Cimtographer** (formerly Cities-Skylines-Mapper): paste terrain.party
  coordinates, fetch from `overpass-api.de`, "Make Roads." The long-running
  community default; hard limit of 32,767 road segments, plus
  tolerance/curve settings to simplify dense OSM data below that cap.
- **OSM Import** (Workshop ID 1957515502): imports from a local `.osm` file;
  newer, reported to need more manual cleanup afterward.
- **Overlay / Overlay 2**: not a road importer — displays a satellite/map
  image as a translucent in-editor reference layer, swappable while the
  editor runs. Useful alongside either importer for hand corrections.

## Decision

1. **Edition: CS1** (already owned; CS2 has materially less mod support for
   this workflow).
2. **Terrain:** heightmap import via the built-in Map Editor, sourced from
   terrain.party (fallback: Skydark or a raw SRTM/DEM tile if terrain.party
   lacks SJC coverage or is down — both unverified, check at use time).
   Rotate the imported heightmap 180° before use: the importer defaults to
   sun-north-at-noon, which is wrong for most reference footage/expectations.
3. **Roads: Cimtographer primary**, pasting the bbox this ADR's tooling
   produces (`arteria cs prepare-map`, roadmap L21). Fall back to OSM Import
   (1957515502) only if Cimtographer's segment cap or Overpass fetch fails
   for the chosen area; either way, expect manual node/junction cleanup in
   `netedit`'s C:S counterpart or in-game tools.
4. **Reference imagery: Overlay/Overlay 2** for satellite context while
   hand-placing zoning, buildings, or fixing roads.
5. **Area per map: one corridor + buffer, never the whole city** — pick the
   corridor via `arteria cs prepare-map --city sjc --corridor <A|B|C|D>`
   (default 18 km tile; the tool warns if the corridor's own extent doesn't
   fit or if a larger `--size-km` is requested).
6. **Package edits:** TM:PE and Move It (already implied by roadmap L22), one
   save per intervention package, Workshop mod IDs/versions pinned in
   `mods.lock.txt` (roadmap L22 deliverable) so a save can be reproduced.
7. **Labelling:** every CS1 screenshot or video carries an "illustrative,
   uncalibrated — not SUMO evidence" caption or on-screen overlay, per the
   research brief's Phase 6 caution and ADR 0015 consequence 5. No CS1
   observation is ever reported as if it were a SUMO metric; CS1-vs-SUMO
   comparison (roadmap P8.5/L23) is explicitly a qualitative side-by-side,
   not a validation of either tool against the other.

## Consequences

- No mod does both roads and SUMO traffic: CS1's own traffic stays
  uncalibrated and is never substituted for SUMO output (ADR 0015 already
  established this; restated here since it is easy to forget once a CS1
  scene looks convincing).
- Corridor-scoped maps mean a separate CS1 save per corridor if more than
  one is ever built, not a single whole-city save — more files to track in
  `mods.lock.txt`/`cs/<city>/`, but each stays small enough to actually play.
- Cimtographer's 32,767-segment cap means a dense corridor (centre, many
  minor streets) may need the importer's simplification settings turned up,
  trading street-grid fidelity for import success; OSM Import's manual
  cleanup is the fallback cost if that trade is unacceptable.
- `arteria cs prepare-map` is the only scripted step in this whole track —
  everything downstream (Map Editor, Cimtographer, Overlay, TM:PE, Move It)
  is a manual GUI procedure on the owner's Windows desk machine, documented
  in `docs/local/cities-skylines.md`, not something a Claude session can run
  or verify directly.
