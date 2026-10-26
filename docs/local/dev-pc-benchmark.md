# Dev PC benchmark vs. the 8-core / 32 GB guideline

Measured 2026-10-26 inside WSL2 (Ubuntu, kernel 6.18 microsoft-standard-WSL2) on the desk PC. The guideline is the "Suggested minimum" under the compute-budget table in `docs/roadmap.md` (8 cores/16 threads, 32 GB RAM, 200 GB free SSD for `ARTERIA_DATA`) and open question 6 there ("is the current dev PC enough?").

## Measurements

| Item | Guideline | Measured | Verdict |
|---|---|---|---|
| CPU | 8 cores / 16 threads | Intel Core i5-11400F @ 2.60 GHz, 6 cores / 12 threads, AVX2/AVX-512, VT-x (12 logical CPUs visible in WSL2, no CPU cap in `.wslconfig`) | Below: 75% of cores |
| RAM visible to WSL2 | 32 GB | 9.7 GiB (`MemTotal` 10,185,512 kB), 3 GiB swap; `C:\Users\lw_na\.wslconfig` sets `memory=10GB` | Far below: about 30% |
| Disk | 200 GB free SSD | 1007 GB ext4 virtual disk (`/dev/sdd`), 831 GB free | Meets |
| Disk write | n/a | 179 MB/s sequential (`dd` 1 GiB with `fdatasync`) | Adequate |
| WSL2 networking | n/a | `networkingMode=mirrored` | n/a |
| SUMO | installed | `sumo`/`netconvert` not on `PATH` in this session (the session that took these measurements was a worktree agent; the 2026-10-26 desk run did use SUMO, so check with `arteria doctor`) | SUMO benchmark not run |
| Python | 3.12 | 3.12.3 | OK |

Quick CPU check (pure-Python integer loop, 20M iterations per task, `multiprocessing.Pool`): 1.12 s for one task; 2.44 s for 6 tasks in parallel; 2.68 s for 12 tasks in parallel. Perfect scaling would stay near 1.1 s. The 12-task result implies roughly 5x throughput over serial across 12 threads, and 6 tasks give about 2.8x, so the machine scales to about 5-6 effective workers on this synthetic test (SMT threads, Windows host load and pool start-up all contribute; single noisy run, not a rigorous benchmark).

Not measured: host physical RAM (not readable from WSL2 without PowerShell; the `.wslconfig` cap is the binding limit anyway), SUMO step rates (no SUMO binary in the measuring session), thermals under sustained load.

## Go / no-go for run plans

The roadmap workload table assumes 8 workers, 1-4 GB per micro run and about 2 GB for `netconvert`.

- **Network builds (`netconvert`, candidates B/D/C/A): GO.** Under 2 GB RAM and 1-5 minutes; candidate B already built here.
- **Single micro AM-peak runs and `sumo-gui` viewing: GO.** One run needs 1-4 GB.
- **Seed batches (10 seeds): GO with 4 workers, not 8.** 4 workers x up to 4 GB fits in 10 GB with headroom for Windows-side memory pressure; expect about 2x the "10 seeds on 8 workers: ~20 min" figure, so roughly 40 minutes or more.
- **Calibration (`duaIterate`, 30-50 iterations, 2-10 h): GO overnight, 4 workers**, with sleep disabled (L7) and one candidate at a time.
- **NSGA-II optimizer (10k meso runs, about 20 h on 8 workers): conditional / NO-GO as planned.** Expect about 35-45 h on 4-5 workers on this machine. Use a smaller first campaign (for example 500 packages x 3 seeds), or a cloud/university node, and keep micro confirmation to the top few packages. Meso runs are lighter on RAM, so 6 workers may be possible after measuring.
- **FCD/emissions outputs:** keep disabled except for chosen runs; disk is fine, RAM is not the constraint there.

## Actions

1. Raise `memory=` in `.wslconfig` if the host has spare RAM (needs host RAM check; then `wsl --shutdown`). 16 GB would allow 6 workers for batches; 32 GB is only reachable with a hardware upgrade.
2. Re-run a real SUMO benchmark at the desk once the optimizer exists: time a candidate-B micro run and a meso run at 1, 4 and 6 workers, and record peak RSS per run; replace the estimates above.
3. Roadmap open question 6 stays open for the P7 optimizer (cloud/cluster decision); it is answered "yes" for P2-P4 work.
