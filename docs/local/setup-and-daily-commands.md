# Local setup and daily commands

Practical reference for working on ArterIA at the desk (WSL2/Ubuntu, per
ADR 0014 and `docs/roadmap.md`'s "Local features"). This file collects the commands that
already work today and the ones the roadmap defines but whose scripts don't
exist yet (marked **(planned)** — see the roadmap `L<n>` ID in parentheses for
the full spec). Remote Claude app sessions never run the SUMO/GUI steps here;
see `docs/roadmap.md` → "Remote features" for what they can do instead.

## One-time setup

1. **Python environment** (works today)
   ```bash
   pip install -e ".[dev]"
   ```
   Installs `arteria` editable plus `nox`, `ruff`, `mypy`, `pytest`. Needs
   Python >= 3.11 (`pyproject.toml`). A `uv sync` / `uv.lock` path is planned
   (L3) but not set up yet — plain `pip` works in the meantime.

2. **SUMO install** (planned — L1)
   No `scripts/win/setup-sumo.ps1` exists yet. Until it does, install SUMO
   manually:
   - Preferred: `pip install eclipse-sumo libsumo traci` (same version across
     Windows, WSL2 and remote sessions — pin the version in `pyproject.toml`
     once chosen, per ADR 0001).
   - For `sumo-gui`/`netedit` (GUI tools, not available via the pip wheels):
     download the SUMO MSI/zip from https://sumo.dlr.de/docs/Downloads.php and
     set `SUMO_HOME` to the install directory.

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
   export ARTERIA_DATA="$HOME/arteria-data"
   export ARTERIA_PRIVATE="/mnt/veracrypt1"   # only once the VeraCrypt volume exists (L24)
   ```
   Create `~/arteria-data/` (see the directory layout in `docs/roadmap.md`
   → "Recommended local directory layout", adapted to Linux paths).
   `ARTERIA_PRIVATE` isn't needed until restricted data (OD microdata,
   counts, signal plans) actually arrives.

6. **Pre-commit hooks** (works today)
   ```bash
   pip install pre-commit
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
nox -s smoke                   # skips cleanly without a `sumo` binary;
                                # real toy-network run still TODO (lands with Phase 2)
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

## Weekly / per-session routine

1. `arteria doctor` (mount `ARTERIA_PRIVATE` only if today's task needs it).
2. Read `.claude/napkin.md`, pick an item; `git pull`; `pip install -e ".[dev]"` if dependencies changed.
3. Make the change; `nox -s lint tests smoke`.
4. Network work (once Phase 2 starts): `arteria network build` + `validate`; junction fixes only through `netedit` (L10), exported to patches — never commit the generated `.net.xml` itself.
5. Before long runs (calibration/optimizer): disable sleep (L7), then launch with `--workers` or schedule overnight (L18).
6. Dismount `ARTERIA_PRIVATE`; confirm `git status` shows no data files staged.
7. Commit; invoke `thesis-orchestrator` per `CLAUDE.md` unless the commit is purely administrative/tooling; move finished `.claude/napkin.md` items into `CHANGELOG.md`.

## When does SJC become visible in SUMO?

As of 2026-10-25: **the code exists; running it at the desk is the only
step left.** `arteria osm fetch`, `arteria network build`, and
`arteria network validate` are implemented and unit-tested against toy
fixtures (remote sessions have no real `sumo`/`netconvert`/`osmium`
binary or network access, per ADR 0009, so none of the three has run
against real SJC data yet). `docs/local/sjc-quickstart.md` is the exact
desk sequence: geocode a study-area polygon for real (needs real network
to Nominatim), fetch + clip the real OSM extract, build and validate the
network, open it in `sumo-gui`/`netedit`, and see uncalibrated traffic
move on it via SUMO's bundled `randomTrips.py`. None of that is a
calibrated baseline or a validated corridor choice — see that file's
"What this is NOT" section.
