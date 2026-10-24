# Napkin Runbook

## Curation Rules
- Re-prioritize on every read.
- Keep recurring, high-value notes only.
- Max 10 items per category.
- Each item includes date + "Do instead".
- Only open/unresolved items are kept here. The moment an item is done, remove it from this file — it belongs in `CHANGELOG.md` (user-facing) and/or `docs/adr/` (architectural record), not here.

## Execution & Validation (Highest Priority)

None yet.

## Roadmap & Status

See `README.md` for current status, `docs/roadmap.md` for the phased plan (P0-P10, remote R1-R21 = tasks for Claude app sessions, local L1-L25), and `docs/` for research material.

## Reference Documentation

None yet.

## Backlog Workflow

When adding new backlog items:
1. **Add napkin summary** — brief one-liner with date + impact + estimate (goes in "Backlog Features" below)
2. **Add detailed spec if needed** — for an architectural or irreversible decision, write an ADR in `docs/adr/`
3. **Update status** — reflect near-term priority changes in `README.md`

## Bug Fixes (Next Priority)

None open.

## Backlog Features

1. **[2026-10-24] Owner: actually send the SJC data requests** (blocks P3/P4, long lead time)
   Do instead: drafts are logged in `cities/sjc/data-requests.md` (Ipplan, SEMOB) and
   tracked in `cities/sjc/data-manifest.yaml` — a remote session can't send email, so
   fill in `[NOME]`/contact, verify the agency details noted in that file, send, then
   flip each item's `status` in the manifest and the tracker table.
2. **[2026-10-24] Decide repo visibility** (remote sessions push branches directly; drives results-site exposure)
   Do instead: decide before the first remote session pushes code or data manifests (roadmap open question 5).
3. **[2026-10-24] Pick the code license** (small)
   Do instead: decide before first public release; record in an ADR if non-trivial.
4. **[2026-10-24] Benchmark dev PC against 8-core / 32 GB guideline** (small)
   Do instead: check before committing to local calibration/optimizer run plans.
5. **[2026-10-24] Owner review of ADRs 0002-0004** (Status: Proposed, awaiting acceptance)
   Do instead: accept, reject, or request changes before P0 implementation starts against them.

## User Directives

1. **[2026-10-24] Keep responses concise; avoid trailing summaries**
   Do instead: State results directly and focus on relevant updates only.
