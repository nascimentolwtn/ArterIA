# 0014. Desk environment: WSL2 (Ubuntu) as the sole primary OS, project on the native Linux filesystem

Date: 2026-10-26
Status: Accepted

## Context

`docs/roadmap.md` ("Local features", L1-L24) and ADR 0002's context line were
written around a Windows 11 desktop as the primary desk OS, with WSL2 called
out only as an optional "Linux-parity env for long runs" (L6). In practice
the owner is setting up the desk machine now and some of the tooling ArterIA
depends on at the desk — building SUMO from source, and generally any
`make`-based build — needs a real Linux filesystem to be fast: `make`,
`pip`/`git`, and SUMO's own build do large numbers of small file
operations, and on Windows 11 with WSL2 those cross the Windows/WSL 9P
network-filesystem boundary when the working tree sits under `/mnt/c/...`,
which is measurably slower (reports of 5-10x for `git status`/build-tool
file-stat-heavy workloads) than the same tree on WSL2's native `ext4`.

The alternative roadmap already considered — SUMO installed natively on
Windows, pointed at files living in WSL2 via `\\wsl.localhost\Ubuntu\...` —
has the same 9P cost in the other direction for any GUI tool browsing or
repeatedly re-reading many files, and means maintaining two separate SUMO
installs (version drift risk the roadmap's P0 risk list already flags:
"SUMO version drift between local Windows and Linux (WSL2)").

Windows 11 ships WSLg (Linux GUI app support inside WSL2) out of the box on
current builds, so `sumo-gui`/`netedit` can run directly inside WSL2 against
files on the native filesystem, with no cross-boundary access at all for the
normal workflow. Reaching into Windows only matters for the rare case of
opening a file in a Windows-only tool, which is low-frequency and not worth
optimizing for.

## Decision

- WSL2 (Ubuntu) is the desk machine's **sole primary OS** for ArterIA work —
  not a dual Windows-primary/WSL2-secondary setup. The roadmap's L6 framing
  ("WSL2 option... for long runs") is superseded: WSL2 is not an occasional
  escape hatch, it is where all desk work happens.
- The repo clone, `ARTERIA_DATA`, and (once mounted) `ARTERIA_PRIVATE` all
  live on WSL2's native Linux filesystem (e.g. `~/arteria-data`), never
  under `/mnt/c/...`. Nothing performance-sensitive (build, `git`, `pip`,
  `nox`) runs against a Windows-mounted path.
- SUMO (including `sumo-gui`/`netedit`) is installed inside WSL2, not
  natively on Windows. GUI tools run via WSLg; no `\\wsl.localhost\...` UNC
  path is part of the normal workflow. `pip install eclipse-sumo libsumo
  traci` (ADR 0001, L1) still gives the headless/TraCI path the same way on
  Windows, WSL2, or remote sessions — this decision only changes where the
  full GUI install lives.
- Windows is still the host OS (dual-booting isn't required), and is used
  for Windows-only tools when actually needed (e.g. a one-off open of a
  generated file in a GUI editor Linux doesn't have) via the WSL UNC path —
  that remains fine precisely because it's occasional, not a hot path.

## Consequences

- Easier: one real SUMO/build toolchain to install and keep current instead
  of two, which also removes the Windows/WSL2 version-drift risk the
  roadmap's P0 risk list called out; `make`/`git`/`pip`-heavy work (building
  SUMO from source, `nox` runs, large `git` operations) runs at native
  `ext4` speed with no 9P penalty; Windows-specific failure modes tied to
  the old long-path (L4) and Defender-exclusion (L5) items mostly stop
  applying once the working tree is off the Windows filesystem.
- Harder: several roadmap `L<n>` items were written as Windows-native
  PowerShell scripts under `scripts/win/*.ps1` assuming the Windows
  filesystem/registry (L4 long paths, L5 Defender exclusions, L7 power
  hygiene/Task Scheduler, L18 scheduled runs) or a Windows-only encryption
  note (L24, BitLocker). These need to be re-pointed at WSL2/Linux
  equivalents (`scripts/linux/...`, systemd timers or `cron` instead of
  Task Scheduler, `age`/VeraCrypt's Linux client instead of a
  Windows-BitLocker aside) or marked not applicable — tracked as a napkin
  follow-up rather than resolved in this ADR.
- Risk: depends on the installed Windows build actually having WSLg; if a
  future desk machine only has an older WSL2 without it, `sumo-gui`/
  `netedit` would need an X server (e.g. VcXsrv) as a fallback — worth a
  quick `wsl --version` check before relying on WSLg.
