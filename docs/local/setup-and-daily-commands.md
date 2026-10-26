# Local setup and daily commands

Practical reference for working on ArterIA at the desk (WSL2/Ubuntu, per
ADR 0014 and `docs/roadmap.md`'s "Local features"). This file collects the commands that
already work today and the ones the roadmap defines but whose scripts don't
exist yet (marked **(planned)** — see the roadmap `L<n>` ID in parentheses for
the full spec). Remote Claude app sessions never run the SUMO/GUI steps here;
see `docs/roadmap.md` → "Remote features" for what they can do instead.

## Quick setup (WSL2)

Copy-pasteable version of the "One-time setup" section below, for a fresh
WSL2 Ubuntu machine. Clone inside WSL's own filesystem (here `~/git/ArterIA`) —
never under `/mnt/c/...` (ADR 0014). Every new shell needs
`source .venv/bin/activate` from the repo root before `arteria`/`nox`/`pytest`
work.

```bash
git clone https://github.com/nascimentolwtn/ArterIA.git ~/git/ArterIA && cd ~/git/ArterIA

# Python env: pip lives in a project venv (.venv/ is gitignored); Ubuntu 24.04's
# system Python is PEP 668 "externally managed", so bare `pip install` is refused.
sudo apt install -y python3-venv python3-pip   # no-op if already present
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# SUMO: the eclipse-sumo wheel ships sumo, sumo-gui, netedit and netconvert
# (verified 1.28.0 on this WSL2 box); the GUIs run through WSLg (ADR 0014) —
# no Windows install, no \\wsl.localhost\...
pip install eclipse-sumo libsumo traci

# osmium CLI (arteria osm fetch) is not in any wheel:
sudo apt install -y osmium-tool

# optional: system SUMO (apt) instead of / besides the wheel
# sudo apt install -y sumo sumo-tools sumo-doc

# SUMO_HOME for the pip wheel (SUMO tools like randomTrips.py live there):
echo 'export SUMO_HOME="$(~/git/ArterIA/.venv/bin/python -c "import sumo; print(sumo.SUMO_HOME)")"' >> ~/.bashrc
# (with apt SUMO instead: export SUMO_HOME=/usr/share/sumo)

# WSLg check: this should open a SUMO window on the Windows desktop
# sumo-gui --window-size 400,300

# ARTERIA_DATA
echo 'export ARTERIA_DATA="$HOME/git/ArterIA/data"' >> ~/.bashrc
source ~/.bashrc
mkdir -p "$ARTERIA_DATA"

# pre-commit hooks
pip install pre-commit
pre-commit install

# sanity check
arteria doctor
```

`ARTERIA_PRIVATE` isn't part of this — it's only needed once restricted data
(OD microdata, counts, signal plans) actually arrives; see step 5 below.

## One-time setup

1. **Python environment** (works today)
   ```bash
   sudo apt install -y python3-venv python3-pip
   python3 -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"
   ```
   Always inside the venv: Ubuntu 24.04 marks system Python as externally
   managed (PEP 668), and one venv per checkout also avoids the shared
   editable-install race noted in `.claude/napkin.md`. Installs `arteria` editable plus `nox`, `ruff`, `mypy`, `pytest`. Needs
   Python >= 3.11 (`pyproject.toml`). A `uv sync` / `uv.lock` path is planned
   (L3) but not set up yet — plain `pip` works in the meantime.

2. **SUMO install** (planned — L1)
   No `scripts/linux/setup-sumo.sh` exists yet. Until it does, install SUMO
   manually, inside WSL2 (never a native Windows install — ADR 0014):
   - Headless/TraCI: `pip install eclipse-sumo libsumo traci` (venv active; same version
     as remote sessions — pin it in `pyproject.toml` once chosen, per
     ADR 0001).
   - `sumo-gui`/`netedit` come in the same `eclipse-sumo` wheel (checked on
     this machine: 1.28.0, WSLg 1.0.79). They run inside WSL2 via WSLg with
     no extra config on current Windows builds. The apt packages
     (`sudo apt install sumo sumo-tools sumo-doc`) are optional.
   - `osmium` CLI: `sudo apt install osmium-tool` (needed by `arteria osm fetch`). If you need a newer
     version than Ubuntu's repos carry, build from source instead (see
     https://sumo.dlr.de/docs/Downloads.php's Linux/source instructions) —
     either way, if `arteria doctor` can't find `SUMO_HOME` afterward, set
     it explicitly (typically `export SUMO_HOME=/usr/share/sumo` in
     `~/.bashrc`).

3. **Long paths** — not applicable under WSL2 (ADR 0014). Windows'
   `MAX_PATH`/registry long-path setting only matters for a working tree on
   the Windows filesystem; with the repo on WSL2's native `ext4` there's no
   path-length limit to raise. (If you ever do clone onto `/mnt/c/...`
   instead, per ADR 0014 don't — but if you must, the old recipe is
   `git config --global core.longpaths true` plus `LongPathsEnabled=1` in
   the registry.)

4. **Defender exclusions** — not applicable under WSL2 (ADR 0014). Windows
   Defender's real-time scanner doesn't walk WSL2's `ext4` VHD the way it
   does a native NTFS path, so there's nothing to exclude once `ARTERIA_DATA`
   lives inside WSL2.

5. **Environment variables**
   ```bash
   # in ~/.bashrc (or ~/.profile)
   export ARTERIA_DATA="$HOME/git/ArterIA/data"   # gitignored /data/ inside the repo
   export ARTERIA_PRIVATE="$HOME/arteria-private"   # plain directory outside git; only once restricted data exists
   ```
   Create `data/` in the repo (gitignored) (see the directory layout in `docs/roadmap.md`
   → "Recommended local directory layout", adapted to Linux paths).
   `ARTERIA_PRIVATE` isn't needed until restricted data (OD microdata,
   counts, signal plans) actually arrives.

6. **Pre-commit hooks** (works today)
   ```bash
   pip install pre-commit      # venv active
   pre-commit install
   ```
   Runs `ruff` + the `arteria.data_safety` restricted-checksum check
   (`.pre-commit-config.yaml`) on every commit.

## Daily commands (today)

```bash
arteria doctor                 # Python/SUMO/netconvert/osmium versions, SUMO_HOME,
                                # ARTERIA_DATA/ARTERIA_PRIVATE present + writable
nox -s lint                    # ruff check . && mypy arteria
nox -s tests                   # pytest (toy fixtures only)
nox -s lint tests              # both — same as a remote Claude session's R1
nox -s smoke                   # skips cleanly without `sumo`/`netconvert`; otherwise builds
                                # tests/fixtures/smoke/ with netconvert, runs sumo, checks trips
arteria city new <name>        # scaffold cities/<name>/ from cities/_template/
arteria studyarea build --city sjc --user-agent "<yours>"
                                # (P1.4) geocodes cities/sjc/study-areas.yaml via
                                # Nominatim, writes study-areas.geojson. DESK-ONLY:
                                # needs real network to nominatim.openstreetmap.org,
                                # blocked remotely (ADR 0009). First run:
                                # pip install -e ".[dev,geo]"  (new `geo` extra)
                                # --user-agent must identify you, per Nominatim's
                                # usage policy — not a placeholder. Treat the
                                # output as a draft; check it against satellite
                                # imagery/OSM before any real P2.1 extraction.
                                # Add --include-future for the disabled Vista
                                # Verde extension candidate.
arteria osm fetch --city sjc --candidate b [--pbf-path <file>]
                                # (L8, P2.1) downloads/caches Geofabrik's sudeste
                                # extract (or reuses --pbf-path), clips it to the
                                # named study-area candidate's polygon via
                                # `osmium extract`. DESK-ONLY: needs network +
                                # the real `osmium` binary, neither available
                                # remotely (ADR 0009). Written and unit-tested
                                # against toy fixtures only — see
                                # docs/local/sjc-quickstart.md step 2.
arteria network build --city sjc --osm-pbf <file> [--type-files ...] [--extra ...]
                                # (L9, P2.2/P2.3) wraps `netconvert` with the
                                # standard SUMO OSM-import flags, then runs the
                                # existing P2.5 validation on the result and
                                # prints the error/warning counts. DESK-ONLY:
                                # needs the real `netconvert` binary, not
                                # available remotely. See
                                # docs/local/sjc-quickstart.md step 3 — the
                                # flag set hasn't been run against a real
                                # binary yet, so confirm it against
                                # `netconvert --help` before trusting it blind.
arteria network validate --city sjc [--net <file>]
                                # (L11, P2.5) prints the full validation report
                                # (reuses arteria/network/validate.py, already
                                # tested on toy fixtures) for a `.net.xml` you
                                # already built.
```

## Daily commands (planned, no script yet — roadmap ID in parentheses)

These are specified in `docs/roadmap.md` but their entry points don't exist
in the repo yet.

```bash
arteria network edit --city sjc --junction <id>                     # (L10, P2.4, opens netedit)
arteria sim gui --city sjc --scenario baseline                      # (L14, P3.6)
arteria demand build --city sjc --window am-peak                    # (L13, P3.1-P3.3)
arteria sim run --city sjc --scenario baseline --seeds 10           # (L15, P3.6/P4.6)
arteria calibrate demand --city sjc                                 # (L16, P4.3-P4.5)
arteria optimize run --city sjc --study <id> --algo nsga2            # (L17, P7)
```

A quick visual check of the network and some (uncalibrated) traffic moving
on it doesn't need any of those yet — see `docs/local/sjc-quickstart.md`,
which uses SUMO's own bundled `randomTrips.py` instead.

## Viewing the SJC simulation again

Closing the `sumo-gui` window ends that run; nothing is lost, because the
network and routes are plain files in `cities/sjc/network/` (gitignored,
regenerable). From the repo root, with the venv active
(`source .venv/bin/activate`) and `SUMO_HOME` set (new shell, or
`source ~/.bashrc`; check with `echo $SUMO_HOME` — if empty, `randomTrips.py`
fails with "can't open file '/tools/randomTrips.py'", and a one-off fix is
`export SUMO_HOME="$(python -c 'import sumo; print(sumo.SUMO_HOME)')"`):

```bash
# replay the same traffic (same routes, same vehicles) — press Play, or add --start
sumo-gui -n cities/sjc/network/sjc.net.xml -r cities/sjc/network/sjc-random.rou.xml --start --delay 200

# just look at the street network, no vehicles
sumo-gui -n cities/sjc/network/sjc.net.xml

# open it for editing instead (junction fixes go through netedit, never by hand)
netedit cities/sjc/network/sjc.net.xml

# fresh random traffic (different vehicles every run unless you pass --seed)
python "$SUMO_HOME/tools/randomTrips.py" -n cities/sjc/network/sjc.net.xml \
  -r cities/sjc/network/sjc-random.rou.xml -o cities/sjc/network/sjc-random.trips.xml \
  -e 3600 -p 2 --validate --seed 42
```

In `sumo-gui`: Play/Step buttons and the **Delay (ms)** box at the top control
speed (raise it to slow down); scroll zooms, drag pans; right-click a vehicle
or edge for info. The run ends at the route file's end time (`-e 3600` = one
simulated hour), after which the GUI sits idle — close it and relaunch to
replay. Open it from a WSL2 terminal; the window appears on the Windows desktop
via WSLg. If `sumo-gui` says it can't find the network or routes, one of them
is missing: rebuild with `arteria network build --city sjc --osm-pbf
cities/sjc/network/raw/sjc-b.osm.pbf` and rerun `randomTrips.py` as above
(`arteria osm fetch --city sjc --candidate b` first if `raw/` is gone). This is
uncalibrated random traffic — a routability check only.

## Weekly / per-session routine

1. `arteria doctor`.
2. Read `.claude/napkin.md`, pick an item; `git pull`; `pip install -e ".[dev]"` if dependencies changed (venv active: `source .venv/bin/activate`).
3. Make the change; `nox -s lint tests smoke`.
4. Network work (once Phase 2 starts): `arteria network build` + `validate`; junction fixes only through `netedit` (L10), exported to patches — never commit the generated `.net.xml` itself.
5. Before long runs (calibration/optimizer): disable sleep (L7), then launch with `--workers` or schedule overnight (L18).
6. Confirm `git status` shows no data files staged.
7. Commit; invoke `thesis-orchestrator` per `CLAUDE.md` unless the commit is purely administrative/tooling; move finished `.claude/napkin.md` items into `CHANGELOG.md`.

## When does SJC become visible in SUMO?

As of 2026-10-26: **it already is, for candidate B.** The full chain ran for
real at the desk: `arteria studyarea build` (Nominatim), `arteria osm fetch
--candidate b` (Geofabrik + `osmium extract`), `arteria network build`
(`osmium cat` to OSM XML, then `netconvert`) and `sumo-gui` with SUMO's bundled
`randomTrips.py` traffic. Candidates D, C and A have study-area polygons but no
network yet, and `arteria network validate` still reports mostly false positives
on real networks (see `.claude/napkin.md`). `docs/local/sjc-quickstart.md` is the
exact sequence. None of it is a calibrated baseline or a validated corridor
choice — see that file's "What this is NOT" section.
