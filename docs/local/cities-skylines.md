# Cities: Skylines 1 — manual build procedure (roadmap L21-L23, ADR 0011)

Desk-only, Windows, GUI. Illustrative hobby track — never SUMO evidence
(research brief Phase 6, ADR 0015, ADR 0011). Do this at the desk, not in a
Claude session: every step below is a Windows GUI action.

## 0. Prep (scripted)

Run, from the repo, with `ARTERIA_DATA` set:

```
arteria cs prepare-map --city sjc --corridor A   # or B / C / D
```

This writes `$ARTERIA_DATA/cs/sjc/<corridor>/map-prep.md` with the tile's
center, bbox, and an Overpass-ready bbox string (usable by the Cimtographer
fork or an OSM Import mod). Open that file and keep it next to the game.

## 1. Terrain — heightmap

This is the only step with an actual **file** to download and place; the
road step below (Cimtographer) fetches live and needs no local file.

1. Go to terrain.party. If it errors or won't load (reported broken by one
   source behind ADR 0011, unconfirmed from the desk machine), use
   **CS Heightmap** instead (external web tool, exports a scaled 16-bit
   greyscale PNG). Either way, navigate/search to the note's center
   coordinate (`center_lon, center_lat` in `map-prep.md`), pick the ~18 km
   tile size, download the PNG (terrain.party ships it in a zip; CS
   Heightmap gives the PNG directly).
2. Put that PNG into `%localappdata%\Colossal Order\Cities_Skylines\Addons\MapEditor\Heightmaps`
   (create `MapEditor\Heightmaps` if missing).
3. Content Manager -> Editors -> Map Editor -> New -> **Import terrain**,
   pick the image.
4. **Rotate the imported heightmap 180°** before building on it — the
   importer defaults to sun-north-at-noon.
5. If Import does nothing: disable mods and retry (known conflict), then
   re-enable.

## 2. Roads — Cimtographer (primary; no file needed, fetches live)

The original Cimtographer Workshop listing is unmaintained; **subscribe to
the maintained fork, Workshop ID 1485051886** ("Cimtographer - rebuild for
1.10.x") instead — the original page links to it.

1. In the Map Editor, open Cimtographer (the fork), paste the Overpass bbox
   string from `map-prep.md` (`south,west,north,east`) into its coordinate
   field, "Load From overpass-api.de."
2. Adjust tolerance/curve-simplification settings if the segment count is
   near the 32,767 hard limit, then "Make Roads."
3. Fix broken/spiky nodes by hand (`netedit`'s in-game counterpart / default
   road tools). If the result is too messy to fix node-by-node, switch to
   the Image Overlay approach below instead of fighting the importer.

**Fallback — an OSM Import mod:** if the Cimtographer fork fails to fetch or
the segment cap can't be worked around, try the "OpenStreetMap Import Mod"
by grilly86 (reported to be a revamped, scaling-fixed successor with
auto-naming — confirm its current Workshop id when you search for it) or
the older OSM Import (Workshop ID 1957515502, imports from a local `.osm`
file). Expect more manual cleanup afterward either way.

**Alternative — Image Overlay + manual trace:** several map-making creators
reportedly prefer this over any auto-import, since auto-generated OSM roads
commonly come out messy with traffic-bug-prone junctions: skip straight to
section 3 below, drop the satellite/map overlay, and hand-draw the road
network with the game's own tools using the overlay as a guide. Slower, but
avoids importer-specific bugs entirely.

## 3. Reference imagery — Overlay / Overlay 2

Subscribe to Overlay (or Overlay 2). Drop a satellite/map image of the same
bbox as `overlay.png` in the mod's folder; it renders translucently over the
Map Editor so roads/zoning can be hand-corrected against real imagery. Swap
the file and toggle the overlay to reload without restarting the editor.

## 4. Save, zone, package edits

1. Save the map.
2. Zone/plant by hand in free time — no scripted help here.
3. For each intervention package under evaluation (ADR 0006 catalog), make
   one save: TM:PE for lane/turn/priority changes, Move It for geometry
   tweaks. Record what changed in the save's filename or a short note next
   to it.
4. Pin every Workshop mod's id and version actually used into
   `$ARTERIA_DATA/cs/sjc/mods.lock.txt` (one line per mod) so a save can be
   reproduced later.

## 5. Capture and label

Every screenshot or video gets an "illustrative, uncalibrated — not SUMO
evidence" caption or on-screen overlay before it leaves this folder (ADR
0011 consequence, research brief Phase 6). Google 3D/web-viewer clip limits
(ADR 0015) do not apply here — this is a separate track — but the labelling
rule does.

## 6. Comparison (roadmap P8.5/L23)

Log CS1's own observed traffic behaviour against the matching SUMO baseline
in a simple table (`arteria cs compare`, not yet implemented). This is a
qualitative side-by-side for research question 7, never a validation of
either tool against the other.

## Open / unverified

- terrain.party's current coverage and reliability for SJC; CS Heightmap's
  coverage/reliability as the alternative.
- Whether the Cimtographer fork's (1485051886) Overpass fetch works cleanly
  on the current game patch and gives usable road geometry for a dense SJC
  corridor, or whether hand-tracing over Image Overlay ends up being the
  real path.
- OSM Import (1957515502) and the grilly86 "OpenStreetMap Import Mod"'s
  current glitch/null-reference reports and exact Workshop id — check the
  Workshop page's recent comments before relying on either fallback.
