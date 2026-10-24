# 0004. Data storage and versioning

Date: 2026-10-24
Status: Accepted (2026-10-24: confirmed local-disk-only — no LFS, no external object store)

## Context

ArterIA's inputs and outputs span several orders of magnitude in size and sensitivity: a few KB of config, multi-GB OSM/network/simulation outputs, and non-public municipal data (OD surveys, signal plans, crash data) under data-sharing terms that forbid redistribution (`docs/roadmap.md` P0.6, P1.2, open question 5 on repo visibility). Remote Claude sessions (ADR 0009) only ever see what is committed, so whatever is kept out of git has to still be describable, checkable and reproducible from what *is* committed — otherwise a remote session (or a future contributor) cannot tell what a run depended on.

Git LFS and a self-hosted object store were both considered as ways to keep large files "in" the project without bloating the main git history. Both add operational cost (LFS storage quotas/billing, or standing up and securing a store) for data that, per P1.2/ADR 0010, is often not shareable anyway.

## Decision

- **Commit to git:** code, configs, `city.yaml`/data-manifest schemas (ADR 0003), small toy fixtures, network-correction patches (P2.3), checksums, and run manifests (P0.7). Nothing here depends on city-specific scale.
- **Never commit:** raw OSM snapshots, OD microdata, generated `.net.xml` network files, per-vehicle simulation outputs (tripinfo/FCD/emissions), optimizer checkpoints/caches, and media (screenshots/video). These live outside git entirely:
  - `ARTERIA_DATA` (local, outside git, excluded from AV scanning) — `raw/`, `cache/`, `runs/`, `optim/`, `media/`, `cs/`, per the directory layout in `docs/roadmap.md`.
  - `ARTERIA_PRIVATE` (a mounted encrypted volume — VeraCrypt or `age`, per ADR 0010) for non-public municipal data specifically.
- **No Git LFS and no external object store.** Large data stays off git and off any additional hosted storage; the manifest (ADR 0003) plus checksums is the only record that a given large file exists and what it is.
- **Safety net, not the only control:** `.gitignore` covers `cities/*/private/`, `**/raw/`, `*.fcd.xml`, `outputs/`, `.env`; a pre-commit hook (run at the desk and by remote sessions, R1) fails the commit if a `visibility: restricted` manifest entry's `sha256` is found in the git index.
- **Derived/public outputs** (aggregated, k-anonymized, per P9.1/L25) are the only form of real results data that may ever be committed or published, and only via an owner-reviewed PR into `results/published/`.

## Consequences

- Easier: the repository stays small enough to be fully readable by a remote session and safe to make public (feeds open question 5); reproducibility rests on manifests and checksums rather than on git tracking multi-GB binaries; no LFS billing/quota or object-store security surface to maintain.
- Harder: every large or sensitive artifact needs a manifest entry and a checksum to be reproducible at all — there is no "just commit it" fallback; restoring a specific historical run requires the `ARTERIA_DATA`/`ARTERIA_PRIVATE` tree (or its backup) in addition to the git history, since git alone no longer has the data.
- Risk: a contributor accidentally commits a large or restricted file before the pre-commit hook catches it, or runs it from a fork where the hook isn't installed — mitigate with GitHub secret scanning/push protection (`gitleaks` already planned) and by treating the pre-commit hook as a safety net, not the only control, per the rule above.
