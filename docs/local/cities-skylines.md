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
center, bbox, and an Overpass/Cimtographer-ready bbox string. Open that file
and keep it next to the game.

## 1. Terrain — heightmap

1. Go to terrain.party (fallback: Skydark, or a raw SRTM/DEM tile hand-cropped
   to the bbox in `map-prep.md` — both unverified for SJC coverage, confirm
   on the day). Navigate to the note's center coordinate, pick the ~18 km
   tile size, download.
2. Extract the zip into `%localappdata%\Colossal Order\Cities_Skylines\Addons\MapEditor\Heightmaps`
   (create `MapEditor\Heightmaps` if missing).
3. Content Manager -> Editors -> Map Editor -> New -> **Import terrain**,
   pick the image.
4. **Rotate the imported heightmap 180°** before building on it — the
   importer defaults to sun-north-at-noon.
5. If Import does nothing: disable mods and retry (known conflict), then
   re-enable.

## 2. Roads — Cimtographer (primary)

1. Subscribe to Cimtographer (formerly Cities-Skylines-Mapper) on the
   Workshop.
2. In the Map Editor, open Cimtographer, paste the Overpass bbox string from
   `map-prep.md` (`south,west,north,east`), "Load From overpass-api.de."
3. Adjust tolerance/curve-simplification settings if the segment count is
   near the 32,767 hard limit, then "Make Roads."
4. Fix broken/spiky nodes by hand (`netedit`'s in-game counterpart / default
   road tools).

**Fallback — OSM Import (Workshop ID 1957515502):** if Cimtographer fails to
fetch or the segment cap can't be worked around, export a local `.osm` file
for the same bbox and import it with this mod instead. Expect more manual
cleanup afterward (per the 2024 community reports this ADR's research was
based on).

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

- terrain.party's current coverage and reliability for SJC.
- Whether Cimtographer's Overpass fetch still works unmodified on the
  current game patch (CS1 has been updated many times since the sources
  behind ADR 0011 were written).
- OSM Import (1957515502)'s current glitch/null-reference reports — check
  the Workshop page's recent comments before relying on the fallback.
