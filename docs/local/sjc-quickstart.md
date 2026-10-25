# SJC quickstart: from zero to a moving picture in SUMO

A step-by-step runbook for the first time you take ArterIA's SJC pilot from
"only code exists" to "I can see a real São José dos Campos street network
with vehicles moving on it in `sumo-gui`." Everything here runs at the desk
(Windows 11, WSL2, or Linux with SUMO installed) — none of it works from a
remote Claude app session (ADR 0009: no `sumo`/`netconvert`/`osmium` binary,
no network to Nominatim or Geofabrik there).

**What this gets you:** a real network render and vehicles visibly moving.
**What this is NOT:** a calibrated baseline, a validated corridor choice, or
anything citable as a research result. The demand in step 5 is random
traffic for a visual sanity check only — see the "What this is not" section
at the bottom before showing this to anyone as if it were evidence.

## 0. One-time setup (if not already done)

```bash
pip install -e ".[dev,geo]"   # geo extra: geopy/shapely/pyproj, needed for step 1
arteria doctor                 # confirms sumo/netconvert/osmium are on PATH and SUMO_HOME is set
```

If `doctor` reports `sumo`/`netconvert`/`osmium` as "not found on PATH", install
SUMO first (`docs/local/setup-and-daily-commands.md` → "SUMO install") and
`osmium-tool` (`apt install osmium-tool` on Linux/WSL2, or see
https://osmcode.org/osmium-tool/ for Windows) before continuing.

## 1. Draft the study-area polygon (real Nominatim geocoding)

```bash
arteria studyarea build --city sjc --user-agent "arteria-sjc/0.2 (your-real-email@example.com)"
```

This writes `cities/sjc/study-areas.geojson` with one polygon per candidate
corridor in `cities/sjc/study-areas.yaml`. **Use your real email in
`--user-agent`** — Nominatim's usage policy blocks generic placeholders.

Treat the output as a draft: open `cities/sjc/study-areas.geojson` in QGIS
or https://geojson.io and eyeball it against satellite imagery before
trusting it for anything beyond this quickstart. If a polygon looks wrong
(landmark geocoded to the wrong place, buffer too tight/loose), fix the
landmark query or `buffer_m` in `study-areas.yaml` and re-run.

## 2. Pick a candidate and fetch the OSM extract

The owner's priority order (2026-10-25) is **B > D > C > A**
(`cities/sjc/candidate-corridors.md`). Start with candidate `b`
(Av. Andrômeda <-> DCTA / Jardim Satélite):

```bash
arteria osm fetch --city sjc --candidate b
```

First run downloads Geofabrik's `sudeste-latest.osm.pbf` (all of
Southeast Brazil — several hundred MB; this is a one-time cache, reused
on later runs) to `cities/sjc/network/raw/`, then clips it to candidate
B's polygon via `osmium extract`, writing
`cities/sjc/network/raw/sjc-b.osm.pbf`. If your connection is slow, fetch a
smaller pre-clipped `.osm.pbf` yourself (e.g. a city-level extract from
Geofabrik or an Overpass API export of the same polygon) and pass it with
`--pbf-path <your-file>` to skip the regional download entirely.

Don't have a stable connection at all right now? Overpass Turbo
(https://overpass-turbo.eu) can export a small bounding-box extract as
`.osm.xml` in seconds, directly in the browser — osmium/netconvert accept
that too (swap `.osm.pbf` for `.osm.xml` in the next step).

## 3. Build the network

```bash
arteria network build --city sjc --osm-pbf cities/sjc/network/raw/sjc-b.osm.pbf
```

Writes `cities/sjc/network/sjc.net.xml` and prints how many validation
errors/warnings it found (reusing `arteria/network/validate.py`, roadmap
P2.5). The flags this wraps are the standard SUMO-documented OSM-import
recipe (geometry cleanup, roundabout/ramp guessing, junction joining, TLS
guessing) — they were written and unit-tested against toy fixtures
remotely (ADR 0009), **not run against the real binary yet**, so if
`netconvert` rejects a flag on your installed version, check
`netconvert --help` and pass a fix via `--extra "--your-flag"`
rather than editing `arteria/network/build.py`.

If it reports validation errors:

```bash
arteria network validate --city sjc
```

...prints the full list (severity, check, message) so you know exactly
what's wrong before opening it in a GUI.

## 4. Look at it

```bash
netedit cities/sjc/network/sjc.net.xml
```

or, to see it without editing:

```bash
sumo-gui -n cities/sjc/network/sjc.net.xml
```

This is the point where you should actually recognize the street layout —
compare it against Google Maps/satellite imagery for the same area. If
junctions look wrong (missing turn lanes, a roundabout rendered as a tangle,
a joined junction that shouldn't be), that's real OSM-quality or
netconvert-tuning work for later (roadmap P2.4, `netedit` fixes exported to
patches) — not something to fix by hand-editing the generated `.net.xml`
(never commit that file either; only patches and configs are versioned,
per P0.6/ADR 0004).

## 5. See some traffic move (quick visual only, not calibrated demand)

SUMO ships a quick random-trip generator that needs no OD data — good
enough to confirm vehicles actually route through the network you just
built, nothing more:

```bash
python "%SUMO_HOME%\tools\randomTrips.py" -n cities/sjc/network/sjc.net.xml -r cities/sjc/network/sjc-random.rou.xml -e 3600 -p 2
sumo-gui -n cities/sjc/network/sjc.net.xml -r cities/sjc/network/sjc-random.rou.xml
```

(On Linux/WSL2: `python "$SUMO_HOME/tools/randomTrips.py" ...` — same
arguments.) `-e 3600` simulates one hour, `-p 2` emits a new vehicle every
~2 seconds on average. Press play in `sumo-gui` and you should see vehicles
moving through the real SJC street layout.

## What this is NOT

- **Not a calibrated baseline.** `randomTrips.py` traffic has no relation to
  real SJC demand, OD survey data, or counts — it exists only to prove the
  network is routable. Phase 3/4 (demand generation, calibration against
  real counts — `cities/sjc/data-manifest.yaml` still has the OD survey as
  `deferred`) is unstarted work, not something this quickstart shortcuts.
- **Not a validated corridor choice.** Candidate B's priority comes from the
  owner's qualitative call (`bf725e9`, 2026-10-25), not the data-backed
  P1.3 scoring matrix, which is still open.
- **Not evidence for anything.** Nothing produced by this runbook belongs in
  a thesis chapter, a policy report, or any comparison between packages —
  see `docs/roadmap.md`'s remote/desktop split and the "Numbers from toy
  fixtures or stub evaluators are test data, never findings" rule.

## If something in steps 2-3 doesn't work as written

`arteria osm fetch`/`arteria network build` were written and unit-tested
against toy fixtures in a remote session that has no real `sumo`/
`netconvert`/`osmium` binary (ADR 0009) — this quickstart is the first time
they run against the real tools and real SJC data. If a flag or file
format doesn't match what your installed SUMO version expects, that's
expected friction, not a sign the whole approach is wrong: fix the
specific flag (via `--extra`/`--type-files` or, if the underlying wrapper
itself needs a code change, edit `arteria/network/build.py`/`osm_fetch.py`
directly — you have the real binary now, something no remote session has
had yet) and note what changed in `.claude/napkin.md` or a quick commit so
the next remote session doesn't re-introduce the same assumption.
