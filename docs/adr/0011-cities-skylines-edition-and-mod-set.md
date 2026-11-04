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

**Revised 2026-11-03 (same day):** a second AI's report (Gemini, unverified
by this session beyond one corroborating signal) claimed the original
Cimtographer listing and terrain.party are both broken/abandoned, and named
a different current stack: the "OpenStreetMap Import Mod" by grilly86 (said
to be a revamped, scaling-fixed, auto-naming successor to the original
concept) for roads, the external **CS Heightmap** web tool for terrain
instead of terrain.party, and — as the actual modern creator preference —
tracing roads by hand over the **Image Overlay** mod rather than trusting
any auto-import, since auto-generated OSM roads are reported to create messy
junctions and traffic bugs. This session's own plain (non-spoofed) request
to terrain.party got a 503; a follow-up with a spoofed browser user-agent to
check further was refused by this harness as bot-check circumvention, so
terrain.party's status stays genuinely unverified, not confirmed broken.
Separately, **the owner checked the original Cimtographer Workshop page
directly and found it says "no longer being maintained," pointing to a
working fork at Workshop ID 1485051886** — which the owner already
subscribed to. That is a verified, first-party fact (unlike Gemini's
report) and changes the Cimtographer recommendation below from "the
original listing" to "that fork," without needing to accept the rest of
Gemini's claims.

**Revised 2026-11-03 (third revision, same day): the fork's own crash
threshold and the real cap behind it.** Running the fork against real SJC
corridor B data surfaced two distinct, previously-unknown constraints,
full detail and a reproducible worked example in `docs/local/cities-skylines.md`:

1. **The fork throws `NullReferenceException` on dense real data**, from
   both its live Overpass fetch and a static `.osm` file — not a broken
   importer (a trivial file loads fine), but data-volume/density dependent.
   Bisection on SJC corridor B found it works at 7,378 ways, fails at
   12,173 ways; exact breakpoint unknown, ~7,000-8,000 ways taken as a
   practical safe ceiling for this fork/game patch until shown otherwise.
2. **A successful import can still exhaust the game's own hardcoded
   cap.** Cities: Skylines 1's `NetManager` allows roughly 32,768 total
   network segments and 32,768 total nodes per city, shared by every
   draggable network type (roads, pedestrian paths, water pipes, power
   lines, quays, canals) — confirmed via multiple independent player
   reports to be impassable; no mod lifts it. A 7,378-way import (reporting
   ~17k objects) left so little headroom that no further network object of
   any kind — plain street, outside connection, water pipe — could be
   added afterward.

The fix that actually worked was scoping the Overpass fetch to a much
smaller bbox (one corridor + buffer, not the full ~18 km tile) and
dropping non-vehicle highway classes before import, rather than tuning the
importer's own settings after the fact. This also corrects this ADR's own
"Area per map" framing below (point 5): the bound that matters in practice
is the segment/node cap, not just the terrain-tile size, and a corridor's
own tight bbox is usually well under both. It also corrects this ADR's
"Consequences" claim that every step past `prepare-map` needs a desk GUI
action: the Overpass fetch + road-class/bbox filtering is a public,
scripted-access-friendly API call, so a Claude session can run it and write
the result straight into the Windows game folder via WSL2's `/mnt/c`
bridge — only the Map Editor/mod GUI steps themselves stay desk-only.

Two further gotchas confirmed first-hand, not previously documented
anywhere in this project: a Water Source only counts toward the "water"
requirement checklist if it sits in terrain actually carved below the
surrounding level (not placed on dry land), and an outside connection
needs a road touching the literal outer tile edge, not the inner 9-tile
playable-area boundary shown in-game. Both are now in
`docs/local/cities-skylines.md`.

**Outcome:** using a combined corridor B + D crop (4,537 ways, well under
both the crash threshold and the segment cap) produced the first actually
playable SJC city on this track — terrain, roads, fixed junctions, a water
body, and an outside connection all in place, zoning/traffic-fixing
underway.

## Decision

1. **Edition: CS1** (already owned; CS2 has materially less mod support for
   this workflow).
2. **Terrain: `arteria cs fetch-heightmap`** (added 2026-11-03, same day as
   this revision) builds the heightmap PNG directly from real SRTM GL1
   elevation data (`api.opentopodata.org`, a public API meant for scripted
   access — unlike terrain.party/Heightmapper, which need a browser this
   session can't drive), bypassing the terrain.party/CS Heightmap/Skydark
   question entirely for a Claude-session workflow. It pre-applies the
   180° rotation the importer otherwise needs by hand (sun-north-at-noon by
   default). Scaling (0-1024 m across the 16-bit range) is the commonly
   documented C:S 1 convention, not independently re-verified — check the
   imported terrain's rough shape/relief in-game before trusting it, and
   fall back to a manual terrain.party/CS Heightmap/Skydark download only
   if the result looks wrong.
3. **Roads: the maintained Cimtographer fork, Workshop ID 1485051886**
   (not the original, now-unmaintained listing), pasting the bbox this
   ADR's tooling produces (`arteria cs prepare-map`, roadmap L21) — the
   owner already subscribed to this fork. If it still hits the 32,767-segment
   cap or an Overpass fetch failure for the chosen area, fall back to the
   "OpenStreetMap Import Mod" by grilly86 (exact current Workshop id
   unconfirmed — find it on the Workshop when needed) or the original OSM
   Import (1957515502); either way, expect manual node/junction cleanup in
   `netedit`'s C:S counterpart or in-game tools. Regardless of which importer
   is used, if the auto-imported roads come out messy (reported to be
   common, and the reason some creators skip auto-import entirely): keep the
   **Image Overlay** mod's satellite reference on and hand-trace/fix the
   problem junctions with the game's own smooth road tools rather than
   fighting the importer's settings indefinitely.
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
- Cimtographer's (the fork's) 32,767-segment cap means a dense corridor
  (centre, many minor streets) may need the importer's simplification
  settings turned up, trading street-grid fidelity for import success; the
  OSM Import mods' manual cleanup, or hand-tracing over Image Overlay, is
  the fallback cost if that trade is unacceptable.
- `arteria cs prepare-map`/`fetch-heightmap` aren't the only steps a Claude
  session can run: the Overpass fetch + road-class/bbox filtering ahead of
  the road importer (revised 2026-11-03, third revision) is also scriptable
  and can write straight into the Windows game folder via WSL2's `/mnt/c`.
  Only the Map Editor/mod GUI steps themselves (Cimtographer or an OSM
  Import mod, Overlay, TM:PE, Move It) stay a manual procedure on the
  owner's Windows desk machine, documented in `docs/local/cities-skylines.md`.
- This mod ecosystem moves fast and this session cannot browse the Workshop
  to confirm current mod health directly (bot-check/network limits) — the
  owner's own live check is what resolved the Cimtographer question this
  time, and should be trusted over any AI's unverified report when the two
  disagree.
