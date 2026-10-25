# 0012. Repository visibility and licensing

Date: 2026-10-25
Status: Accepted

## Context

`docs/roadmap.md`'s open questions left two things unresolved: #5 (public or
private GitHub repo — with remote sessions pushing branches directly, a
public repo publishes every pushed branch at once) and #7 (code license,
needed before the first release, P0.8). Neither blocked work so far, but
both needed an answer before more code and city data accumulate.

The owner decided: ArterIA, including this pilot study, is meant to be
public — a public GitHub repo, with licenses that make reuse of the code and
of the research writing straightforward.

This is a separate axis from the per-source `visibility: public|restricted`
field in `data-manifest.yaml` (ADR 0003) and the pre-commit safety net that
enforces it (`arteria/data_safety.py`, ADR 0004). That field tracks whether
a specific *externally sourced* dataset (e.g. OD survey microdata, signal
timing plans, crash data — several SJC manifest entries carry
`visibility: restricted` today, per the agency's own licensing terms) may be
redistributed, which the data provider decides, not ArterIA. Making the repo
and its own code/docs public does not and cannot override a third party's
redistribution terms on data it supplies: a restricted-visibility source, if
ever received, still may never be committed, exactly as before this ADR.
That field and hook are unchanged by this decision.

## Decision

- The GitHub repository is public.
- Code (`arteria/`, its CLI, tests, and tooling) is licensed under the
  **Apache License 2.0** (`LICENSE` at the repo root).
- Documentation, the research brief, ADRs, the roadmap, the thesis tracks,
  and any derived/aggregated data published under `results/published/` are
  licensed under **CC BY 4.0** (`LICENSE-DOCS.md`).
- `README.md`/`README-eng.md`'s license section now states both, instead of
  "A definir"/"TBD".
- This resolves roadmap open questions #5 and #7.
- The data-manifest `visibility: public|restricted` field and the
  `arteria/data_safety.py` pre-commit hook (ADR 0003/0004) are unchanged:
  they keep protecting against ever committing a restricted-visibility
  source into this now-public repo, independent of ArterIA's own license.

## Consequences

- Easier: remote sessions can commit, push, and open PRs/issues without
  ambiguity about public exposure; reuse of the code (Apache 2.0, with its
  explicit patent grant) and of the writing (CC BY 4.0, attribution-only) is
  unambiguous for anyone who finds the repo.
- Harder: Apache 2.0 is effectively a one-way choice — relicensing later
  needs every contributor's consent, which gets harder as more people touch
  the code.
- Risk: a public repo plus open licenses make the unchanged
  `arteria/data_safety.py` pre-commit hook the only technical barrier
  against ever publishing a restricted-visibility source (several SJC
  manifest entries are marked `restricted` today, all still `deferred`).
  If any of those sources is ever actually received, re-verify the hook
  runs in every environment that could commit it (desk and remote, per R1),
  not just locally.
