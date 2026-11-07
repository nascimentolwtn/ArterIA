# Cities: Skylines 1 — manual build procedure (roadmap L21-L23, ADR 0011)

Illustrative hobby track — never SUMO evidence (research brief Phase 6, ADR
0015, ADR 0011). Most steps are a Windows GUI action at the desk, but **not
all of them**: step 2's OSM road-data prep can be run from a Claude session
too (Overpass is a public, scripted-access-friendly API — no browser, no
bot-check circumvention), writing straight into the Windows game folder via
WSL2's `/mnt/c` bridge. Steps are written city-agnostic; SJC's own numbers
(corridors B and D, the first corridor actually taken end-to-end to a
playable city) are given as a worked example after step 6.

**File naming:** version road-data files sequentially (`SJC_01.osm`,
`SJC_02.osm`, ...) instead of overwriting the one you're actively testing —
each import attempt is cheap to redo but expensive to re-diagnose blind.
Keep one "current" file (e.g. `map.osm`/`map`, matching whatever default the
importer's Path field shows) for the import you're about to try next, and
rename anything you want to keep as a numbered version before overwriting it.

## 0. Prep (scripted)

Run, from the repo, with `ARTERIA_DATA` set:

```
arteria cs prepare-map --city sjc --corridor A       # or B / C / D
arteria cs fetch-heightmap --city sjc --corridor A \
  --out "/mnt/c/Users/<you>/AppData/Local/Colossal Order/Cities_Skylines/Addons/MapEditor/Heightmaps/sjc-<corridor>/heightmap.png"
```

The first writes `$ARTERIA_DATA/cs/sjc/<corridor>/map-prep.md` with the
tile's center, bbox, and an Overpass-ready bbox string. The second builds
the actual heightmap PNG from real SRTM elevation data
(`api.opentopodata.org`) and can write straight into the Windows `Heightmaps`
folder via WSL2's `/mnt/c` — no terrain.party/Heightmapper browser step
needed. It also pre-applies the 180° rotation (see step 1), so the file it
writes is ready to import as-is. Takes about a minute (60x60 real samples,
throttled).

## 1. Terrain — heightmap

If step 0's `fetch-heightmap` ran, the file is already in place, already
rotated — skip straight to step 2 after importing it (Content Manager ->
Editors -> Map Editor -> New -> **Import terrain**, pick the image). Spot-
check the imported relief against what you'd expect for the area (the
scaling convention it uses is commonly documented, not independently
verified by that tool) before building on it.

**Known gotcha — Import does nothing:** a conflicting mod can silently
block the Map Editor's terrain-import click handler (not root-caused to a
specific mod; disabling *all* mods and restarting the game fixed it once).
Disable mods, restart, import, then re-enable mods you still want.

**Manual fallback**, if `fetch-heightmap` isn't usable or its terrain looks
wrong: go to terrain.party, or **CS Heightmap** if that errors (reported
broken by one source behind ADR 0011, unconfirmed from the desk machine).
Navigate to the note's center coordinate, pick the ~18 km tile size,
download the PNG, import it, and **rotate it 180°** by hand (the importer
defaults to sun-north-at-noon).

## 2. Roads

The original Cimtographer Workshop listing is unmaintained; **subscribe to
the maintained fork, Workshop ID 1485051886** ("Cimtographer - rebuild for
1.10.x") instead.

### 2a. Why the live fetch and raw OSM data are both likely to fail on a real corridor

Cimtographer's (the fork's) **"Load from overpass-api.de"** button and
**"Load OSM From File"** both threw a `System.NullReferenceException` at
`Mapper.OSM.OSMInterface.init` on real, dense SJC road data this session —
reproducibly, from both the live fetch and a static file with the same
data. This is **not** the importer being fundamentally broken: a trivial
hand-built 1-way test file loaded fine, proving the crash is data-dependent.
Bisecting by way count (same filtering, shrinking bbox) found:

- **Works:** 500 ways, 2,000 ways, 7,378 ways (a real, geographically
  contiguous 9x9 km crop of SJC corridor B).
- **Crashes:** 12,173 ways (the same corridor, "real roads only" filtered —
  footway/path/cycleway/etc. already dropped) and 19,295 ways (unfiltered).
- Exact breakpoint between 7,378 and 12,173 not found — treat **~7,000-8,000
  ways as a practical safe ceiling** for this fork/game patch until proven
  otherwise elsewhere.

**Even an import that succeeds can still leave you stuck.** Cities:
Skylines 1 has a hardcoded cap of roughly **32,768 total network segments
and 32,768 total nodes per city** (the game's `NetManager`), shared by
*every* draggable network type — roads, pedestrian paths, water pipes,
power lines, quays, canals. No mod lifts this; multiple independent player
reports confirm it's treated as impassable. The 7,378-way import above
reported roughly 17,000 objects on load — close enough to the cap that,
once editing began, the game refused to let the user add *any* new network
object: not an outside-connection road, not a plain street, not an
airstrip, not a water pipe (the error reads **"Cannot create any more
objects of this type!"**). Deleting existing roads did not reliably free
slots back up in the same session (matches community reports that the
counter can stay "locked" until a save → quit to desktop → reload cycle);
redoing the import at a smaller scope was more reliable in practice than
chasing that cycle.

### 2b. Road-data prep that avoids both problems (can run in a Claude session)

Fetch only the bbox you actually need (never the full ~18 km importable
tile) and drop non-vehicle highway classes before import, instead of
importing everything and fighting the cap afterward:

```bash
# 1. Fetch once per city/area from the public Overpass API (south,west,north,east)
curl -s "https://overpass-api.de/api/interpreter" --data-urlencode \
  "data=[out:xml][timeout:90][bbox:$SOUTH,$WEST,$NORTH,$EAST]; way[highway]; (._;>;); out body;" \
  -o raw.osm

# 2. Filter by road class + a tighter sub-bbox, write a fresh .osm
python3 - "$WEST" "$SOUTH" "$EAST" "$NORTH" out.osm <<'PY'
import xml.etree.ElementTree as ET, sys
KEEP_HIGHWAY = {"residential", "service", "tertiary", "secondary", "primary",
                 "unclassified", "primary_link", "secondary_link", "tertiary_link",
                 "motorway", "motorway_link", "trunk", "trunk_link", "living_street"}
WEST, SOUTH, EAST, NORTH = map(float, sys.argv[1:5])
tree = ET.parse("raw.osm"); root = tree.getroot()
nodes, in_bbox, ways = {}, {}, []
for el in root:
    if el.tag == "node":
        nodes[el.get("id")] = el
        lat, lon = float(el.get("lat")), float(el.get("lon"))
        in_bbox[el.get("id")] = SOUTH <= lat <= NORTH and WEST <= lon <= EAST
    elif el.tag == "way":
        ways.append(el)
kept, needed = [], set()
for w in ways:
    hw = next((t.get("v") for t in w.findall("tag") if t.get("k") == "highway"), None)
    if hw not in KEEP_HIGHWAY:
        continue
    refs = [nd.get("ref") for nd in w.findall("nd")]
    if any(in_bbox.get(r, False) for r in refs):
        kept.append(w); needed.update(refs)
new_root = ET.Element("osm", version="0.6", generator="arteria-filter")
ET.SubElement(new_root, "bounds", minlat=str(SOUTH), minlon=str(WEST), maxlat=str(NORTH), maxlon=str(EAST))
for nid in needed:
    if nid in nodes:
        new_root.append(ET.Element("node", id=nid, lat=nodes[nid].get("lat"), lon=nodes[nid].get("lon")))
for w in kept:
    new_root.append(w)
ET.ElementTree(new_root).write(sys.argv[5], encoding="UTF-8", xml_declaration=True)
print(f"kept ways: {len(kept)}  kept nodes: {len(needed)}")
PY
```

Aim for a result comfortably under the ~7,000-8,000-way practical ceiling —
and well under it if you also want headroom afterward for junction fixes,
an outside connection, and water pipes (see 3b/3c below). Write the output
straight to the Windows path the importer's Path field shows (e.g.
`/mnt/c/Users/<you>/OneDrive/Documents/map.osm`), versioned per the naming
rule above.

### 2c. Load into Cimtographer

1. **"Load OSM From File"**, pointing at the filtered file from 2b (safer
   than the live Overpass fetch, since it lets you control the bbox/filter
   before the importer ever sees the data).
2. Leave **Curve Tolerance** at its default first try. Raising it
   simplifies OSM points into fewer, straighter segments (more headroom
   under the segment cap) but risks flattening complex geometry — a
   roundabout or crossing viaducts, for instance — into an unrecognizable
   blob. Prefer shrinking the bbox or dropping more road classes (2b) over
   raising this, and only raise it as a last resort, checking the result
   visually.
3. **Bounding Box field** (only used by the live-fetch buttons, not needed
   if loading from file): inferred format `south,west,north,east`, matching
   Overpass QL's own `[bbox:...]` convention — inferred from behavior, not
   confirmed from the mod's source.

**Fallback — an OSM Import mod:** if the Cimtographer fork still fails, try
the "OpenStreetMap Import Mod" by grilly86 (confirm its current Workshop id
when you search) or the older OSM Import (Workshop ID 1957515502). Expect
more manual cleanup afterward either way.

**Alternative — Image Overlay + manual trace:** if auto-import keeps
producing messy junctions no matter the settings, skip straight to section 3
and hand-draw the network using the overlay as a guide. Slower, but avoids
importer-specific bugs entirely.

## 3. Reference imagery, junctions, water, outside connections

### 3a. Overlay / Overlay 2

Subscribe to Overlay (or Overlay 2). Drop a satellite/map image of the same
bbox as `overlay.png` in the mod's folder; it renders translucently over the
Map Editor so roads/zoning can be hand-corrected against real imagery.

### 3b. Junction cleanup — expected, not a sign of a bad import

OSM ways commonly don't share the exact same node at a real intersection
(a real-world data-entry quirk, not an import or filtering bug), so some
disconnected road ends after import are normal, independent of how the
bbox/filtering was done. Fix by either: dragging a loose end onto the
nearby node it should join with **Move It** (shows a snap indicator), or
drawing a short bridging segment with the base road tool between the two
ends. Don't chase every gap across the whole map — prioritize the corridor
you actually care about.

### 3c. Water

Map Editor's Water tool: lower the terrain into a channel/basin at the
area's lowest point (check the heightmap's own elevation range), then place
a **Water Source** inside that carved, actual water — not on dry land. A
Water Source placed on unmodified terrain does not count toward the "water"
requirement checklist even though it looks placed; this is the most common
reason that checklist item stays unmet. The water doesn't need to trace a
real river's exact path (illustrative only, ADR 0015) — any plausible
basin/stream works.

### 3d. Outside connections

At least one road must reach the actual outer edge of the full (25-tile)
terrain square to register as an outside connection — the dashed line
shown in-game marks the inner 9-tile *playable* boundary, not the tile
edge a connection needs to touch (commonly documented, not independently
re-verified by this session).

If **"Cannot create any more objects of this type!"** appears when placing
*any* new network object — not just an outside connection — this is almost
certainly the segment/node cap from 2a, not a bug specific to whatever you
were placing. Deleting roads and retrying in the same session is not
reliable; starting a fresh map with a smaller/filtered import (2b) was.

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

## Worked example — SJC corridors B and D (first playable city, 2026-11-03)

All bboxes `west, south, east, north` (decimal degrees):

| Area | Bbox | Result |
|---|---|---|
| Corridor B, full importable tile (18x18 km) | `-45.975781, -23.300537, -45.799834, -23.137751` | 19,295 ways unfiltered — crashes the importer outright. |
| Corridor B, 9x9 km crop (ceiling test) | `-45.931810, -23.259841, -45.843806, -23.178447` | 7,378 ways / 30,129 nodes after highway-class filtering — imports fine, but reported ~17k objects: close enough to the segment cap that editing later hit "Cannot create any more objects of this type!" on *everything*. |
| Corridors B + D combined, final (playable) | `-45.925442, -23.244254, -45.866762, -23.189994` | 4,537 ways / 17,130 nodes — imported cleanly, left real headroom for junction fixes, the outside connection, and water. This is the one actually played. |
| Corridor D alone (Jardim Colinas roundabout / Ponte Estaiada), for reference | `-45.912024, -23.225655, -45.900346, -23.200066` | Not imported standalone; folded into the combined crop above since the owner wanted to play with fixing this specific interchange. |

Same heightmap (built once for corridor B's full 18x18 km tile) covered the
smaller combined B+D crop too, since both are centered on nearly the same
point — no need to re-fetch terrain when narrowing the road-data bbox
afterward, as long as the new area stays inside the original tile.

## Worked example — Orlando, FL theme-park/resort corridors (2026-11-06)

**Hobby-track reproduction only** (ADR 0011/0015) — Orlando was never onboarded
as an ArterIA city (no `cities/orlando/`); the landmarks below were geocoded
ad hoc (Nominatim) and fed straight into `compute_map_prep`/`build_heightmap`
without a `corridors.geojson`, since step 2's scripted prep only needs a
bbox, not the production pipeline.

These named areas (Disney/Universal/SeaWorld parks, their hotels, two
outlet malls) are landmark footprints spread far wider than one corridor,
confirming the backlog note's expectation: four separate crops, grouped by
which landmarks sit within a few km of each other, rather than one map.

**Orlando's resort/parking-lot road density is markedly higher than SJC's**
per corridor-equivalent area — the 18 km tile centred on Universal alone hit
**39,873 ways** after the same highway-class filtering that kept SJC's full
18x18 km tile to 19,295, and even dropping `highway=service` (parking-lot
access roads, a much larger share of the graph here than in SJC) only cut
it to 15,298 — still crash-tier. Every crop below needed to shrink much
further than SJC's corridors did before landing safely under the
~7,000-8,000-way ceiling.

| Area | Road-crop bbox (west, south, east, north) | Result |
|---|---|---|
| Universal Orlando (Universal Studios, Islands of Adventure, Hard Rock Hotel, Orlando International Premium Outlets — all within ~2 km of each other) | `-81.481785, 28.456476, -81.440908, 28.492651` (4 km) | 3,288 ways / 14,887 nodes. |
| Disney parks + Pop Century Resort (Magic Kingdom, EPCOT, Hollywood Studios, Animal Kingdom, Disney's Pop Century Resort) | `-81.608029, 28.348955, -81.526343, 28.421304` (8 km) | 4,500 ways / 28,721 nodes. |
| SeaWorld + Orlando Vineland Premium Outlets (~4 km apart) | `-81.507922, 28.371759, -81.446649, 28.426022` (6 km) | 4,148 ways / 18,964 nodes. |
| Celebration Suites (Kissimmee), standalone — ~6.6 km south of the Disney cluster, clipped out of every Disney tile up to 9 km | `-81.529805, 28.317631, -81.499189, 28.344763` (3 km) | 916 ways / 5,755 nodes. |

Heightmap tiles (18 km, centred on each cluster's own centroid): built one
each for `disney`, `universal`, `seaworld_vineland`. **`celebration`'s own
road crop sits entirely inside `disney`'s 18 km tile**, so it reuses
`disney`'s heightmap rather than fetching a fourth one — same reasoning as
SJC's corridor B/D reuse. All four written to
`data/cs/orlando/<cluster>/{map.osm,heightmap.png,map-prep.md}` and mirrored
into the Windows game folders (`AppData/.../Heightmaps/orlando-<cluster>/`,
`OneDrive/Documents/ORLANDO_<CLUSTER>_01.osm`).

Not yet done: the GUI import/play steps (1-6 above) for any of the four —
this session only ran the scripted step-0 prep, same division of labour as
SJC's first pass.

### `orlando-minimized` — a fifth, composite map (2026-11-06)

A fifth variant, built after the owner started playing one of the four real
crops: a single map collaging all 4 Orlando clusters together instead of
four separate maps. **Not a real-geography crop** — each cluster's own
road geometry is translated as a rigid block (no rotation/resizing) to a
new position chosen to (a) keep the 4 clusters' real relative compass
directions and (b) fit all 4 inside one 18 km tile without their crop
bounding boxes overlapping. All 4 translations are small (under ~3 km),
since the real clusters already sit within about 19 km of each other.

Combining the 4 clusters' already-filtered crops as-is would have summed to
12,852 ways — over the practical ceiling (section 2a) and in SJC's own
confirmed-crashing range (12,173). Dropping `highway=service` (parking-lot/
resort access roads — a much larger share of the graph in these
theme-park/resort areas than in SJC) from each cluster first brought the
total to **4,140 ways / 24,737 nodes**, close to SJC's own final combined
B+D crop (4,537 ways). Full placement table, translation deltas, and the
master centre point (whose real SRTM terrain was used for this map's
heightmap, since the composite itself has no single real location) are in
`data/cs/orlando/minimized/map-prep.md`.

No connector roads were added between the 4 relocated clusters — there's a
checked (programmatic, no bounding-box overlap) gap of at least ~1-2 km
between any two, left for the owner to hand-draw if wanted, same as any
other junction-cleanup (3b).

## Open / unverified

- Exact way-count breakpoint between 7,378 (works) and 12,173 (crashes) for
  the Cimtographer fork — not found, only bounded.
- Whether the ~32,768 NetManager segment/node cap figure is exact for the
  current game patch, or just the commonly-cited order of magnitude.
- The outside-connection "must touch the literal tile edge, not the 9-tile
  playable boundary" claim — commonly documented, not independently
  re-verified in this session beyond it being consistent with what was
  observed.
- terrain.party's current coverage/reliability for SJC; CS Heightmap's
  coverage/reliability as the alternative.
- OSM Import (1957515502) and the grilly86 "OpenStreetMap Import Mod"'s
  current glitch/null-reference reports and exact Workshop id — check the
  Workshop page's recent comments before relying on either fallback.
