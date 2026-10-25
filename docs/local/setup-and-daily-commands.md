# Local setup and daily commands

Practical reference for working on ArterIA at the desk (Windows 11, per
`docs/roadmap.md`'s "Local features"). This file collects the commands that
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

3. **Long paths** (planned — L4, one-time, admin)
   `scripts/win/enable-longpaths.ps1` doesn't exist yet. Manually:
   ```powershell
   git config --global core.longpaths true
   # then enable LongPathsEnabled=1 in the registry (Local Group Policy or regedit), reboot
   ```

4. **Defender exclusions** (planned — L5, optional, admin)
   Exclude `ARTERIA_DATA` and the `sumo.exe`/`netconvert.exe` paths from
   real-time scanning for speed. Script not written yet; do it by hand in
   Windows Security settings if runs feel slow. Never exclude the repo or
   Downloads folder.

5. **Environment variables**
   ```powershell
   setx ARTERIA_DATA   "E:\arteria-data"
   setx ARTERIA_PRIVATE "V:\"     # only once the VeraCrypt volume exists (L24)
   ```
   Create `E:\arteria-data\` (see the directory layout in `docs/roadmap.md`
   → "Recommended local directory layout"). `ARTERIA_PRIVATE` isn't needed
   until restricted data (OD microdata, counts, signal plans) actually
   arrives.

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
```

## Daily commands (planned, no script yet — roadmap ID in parentheses)

These are specified in `docs/roadmap.md` but their entry points don't exist
in the repo yet. Build them when their phase starts (see "When does SJC
become visible in SUMO?" below for the current blocker).

```bash
arteria osm fetch --city sjc --source geofabrik --date YYYY-MM-DD   # (L8, P2.1)
arteria network build --city sjc                                    # (L9, P2.2/P2.3)
arteria network validate --city sjc                                 # (L11, P2.5)
arteria network edit --city sjc --junction <id>                     # (L10, P2.4, opens netedit)
arteria sim gui --city sjc --scenario baseline                      # (L14, P3.6)
arteria demand build --city sjc --window am-peak                    # (L13, P3.1-P3.3)
arteria sim run --city sjc --scenario baseline --seeds 10           # (L15, P3.6/P4.6)
arteria calibrate demand --city sjc                                 # (L16, P4.3-P4.5)
arteria optimize run --city sjc --study <id> --algo nsga2            # (L17, P7)
```

## Weekly / per-session routine

1. `arteria doctor` (mount `ARTERIA_PRIVATE` only if today's task needs it).
2. Read `.claude/napkin.md`, pick an item; `git pull`; `pip install -e ".[dev]"` if dependencies changed.
3. Make the change; `nox -s lint tests smoke`.
4. Network work (once Phase 2 starts): `arteria network build` + `validate`; junction fixes only through `netedit` (L10), exported to patches — never commit the generated `.net.xml` itself.
5. Before long runs (calibration/optimizer): disable sleep (L7), then launch with `--workers` or schedule overnight (L18).
6. Dismount `ARTERIA_PRIVATE`; confirm `git status` shows no data files staged.
7. Commit; invoke `thesis-orchestrator` per `CLAUDE.md` unless the commit is purely administrative/tooling; move finished `.claude/napkin.md` items into `CHANGELOG.md`.

## When does SJC become visible in SUMO?

Short answer: **not yet, and it's not a remote-session task** — it needs two
things to happen first, both desktop-only.

1. **Phase 1 (study-area selection) hasn't run.** `cities/sjc/city.yaml` still
   has placeholder bounding polygon and time windows — there's no corridor
   chosen yet (roadmap P1.3/P1.4). That's a scoring/decision step, not code;
   it can happen in a remote session (R21 can draft the scoring matrix) but
   needs your input on which corridor(s) to evaluate.
2. **The OSM extraction and `netconvert` build (L8/L9, Phase 2) require the
   real `sumo`/`netconvert`/`osmium` binaries and GUI tools**, which remote
   Claude sessions deliberately don't have (ADR 0009) — this is desktop work.

Once a corridor polygon exists, the realistic desktop sequence is:
`arteria osm fetch` (download + clip OSM) → `arteria network build`
(`netconvert`) → `arteria network validate` → open it in `sumo-gui`/`netedit`
to actually look at it. None of those four commands exist in the repo yet —
only their spec in `docs/roadmap.md`. So the real dependency chain is:
**pick the SJC pilot corridor → write `arteria osm fetch`/`network build`
(a remote session can write and unit-test this code against toy fixtures
today, per R4) → run it at the desk with real SUMO installed.** There's no
date attached to this yet in the roadmap; it's gated on your corridor
decision, not on remaining code volume.
