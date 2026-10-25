# 0009. Remote-session boundary: what a Claude app cloud session may do

Date: 2026-10-24
Status: Accepted (filed 2026-10-25, after the fact — code and `docs/roadmap.md` had already been citing this decision as settled since 2026-10-24; see "Context" below)

## Context

ArterIA's "remote" work is a Claude Code cloud session the owner starts from
the phone app against this repo, alongside "local" work at the desk (Windows
11, real SUMO install, GUI tools, private data). An earlier design built this
boundary around GitHub Actions: hosted/self-hosted runners, Codespaces,
issue-comment ChatOps, gated `workflow_dispatch` runs, Pages deploys and
`@claude` workflows. That design is withdrawn — no `.github/workflows/` file
is planned.

Without a written boundary, code already has to make case-by-case judgment
calls about what a remote session can assume: whether a real `sumo`/
`netconvert` binary or `sumolib` is available, whether toy-fixture test
output may ever be cited as a real finding, and whether hosted CI is still
expected to exist. `docs/roadmap.md` and several modules
(`arteria/network/validate.py`, `arteria/interventions/turn_restriction.py`,
`arteria/calibration/goodness_of_fit.py`) already cited "ADR 0009" as the
answer to these questions before this file existed — the decision was acted
on without being recorded, which is exactly the gap `docs/adr/README.md`
asks ADRs to close for a hard-to-reverse choice. This ADR records the
decision as it has been implemented since 2026-10-24, rather than proposing
something new.

## Decision

- A remote session is a sandboxed cloud container with this repo cloned. It
  can read and write committed files, run Python/`pytest`/`nox`, install
  pinned packages from PyPI, commit, push a branch, and open or comment on a
  PR/issue.
- A remote session **never** has: the real `sumo`/`netconvert`/`osmium`
  binaries, `sumo-gui`/`netedit` or any other GUI, Cities: Skylines, the
  owner's PC, or anything not committed to git (`ARTERIA_DATA`,
  `ARTERIA_PRIVATE`).
- Real SUMO calls sit behind an adapter so the rest of `arteria/` can be
  written and tested without real data or a real binary: modules like
  `network/validate.py` parse the plain-XML `.net.xml` shape directly with
  the stdlib and are exercised only against hand-written toy fixtures in
  `tests/fixtures/`.
- Toy-fixture or stub-evaluator output is test data, never a finding:
  nothing produced only from toy fixtures may back a recommendation in the
  thesis or the policy report. Only desktop runs with a run-provenance
  manifest (P0.7) count as results.
- Hosted CI/CD is off the table. `nox -s lint tests` (ruff, mypy, pytest
  against toy fixtures) is the check a remote session and the desk both run
  on demand (roadmap R1); `nox -s smoke` (a real toy-network SUMO run) stays
  desktop-only. No `.github/workflows/` file is planned.
- This same boundary also answers the AI-agent scope/permissions question
  that was going to be its own ADR — it did not get a separate number,
  because it's the same line: what a remote session may read, run, commit
  and push vs. what waits for the desk.

## Consequences

- Easier: `arteria/` modules can be designed, written and unit-tested from
  the phone against toy fixtures without waiting for real SUMO access or
  real city data; no CI runner topology, secrets, or self-hosted-runner
  security surface to maintain.
- Harder: every module that will eventually touch real SUMO output needs an
  explicit adapter seam from the start, or the toy-fixture tests end up
  testing the wrong thing once real data arrives; a contributor reading only
  the code (not the roadmap) could mistake toy-fixture test passes for
  validated behavior if this ADR isn't kept in view.
- Risk: the boundary drifts silently if a future module reaches for a real
  SUMO call without going through the adapter — mitigate by treating "no
  `sumo`/`netconvert`/`sumolib` import outside the adapter layer" as a review
  check, not just a convention.
