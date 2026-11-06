# 0008. Optimization architecture

Date: 2026-11-06
Status: Proposed

## Context

`CLAUDE.md`'s architecture direction calls for a two-level design: an
upper-level optimizer selects intervention packages (subsets of
`arteria/interventions/catalog.py`'s `InterventionCatalog.entries`); SUMO
acts as the lower level, scoring each package's traffic response. Phase 7
of `docs/roadmap.md` (P7.1-P7.7) is that upper level: decide what a
"package" is as a search-space object, pick a search algorithm, cache
repeated evaluations, and extract a Pareto front a planner can compare
options from.

Two things shape the decision more than the algorithm choice itself:

- **No real evaluator exists yet.** The lower level (P6.1, running SUMO
  per package) is desk-only future work — this remote session is scoped
  by ADR 0009 to toy fixtures and synthetic data, never a real SUMO
  binary. Whatever gets built now has to work against a stub evaluator
  today and swap to a real one later without a rewrite.
- **Cost vs. benefit is genuinely multi-objective.** A planner wants to
  see the trade-off curve between money spent and traffic/safety/equity
  benefit, not one scalarized number — collapsing to a single objective
  now would bake in a weighting nobody has decided on yet.

Algorithms considered for the search backend:

- **NSGA-II** (genetic, population-based, multi-objective) — mature,
  well-supported in `pymoo`, needs no gradient or surrogate model, and
  naturally returns a Pareto front instead of one scalarized optimum.
  Costly in evaluations-per-candidate-found relative to surrogate-based
  methods, but that cost is free while the evaluator is a stub.
- **Bayesian optimization** (`optuna`/BoTorch, surrogate-based) —
  dramatically more sample-efficient, which matters once each evaluation
  means a real SUMO run (P6.1), but needs either a scalarized objective
  or a more involved multi-objective acquisition function, and a
  surrogate model to fit — more machinery to stand up correctly than
  NSGA-II for a first cut.
- **Random/greedy baselines** — not real contenders, but needed later to
  show NSGA-II is actually earning its complexity over "just try things."

## Decision

- **`PackageProblem` (`arteria/optimize/problem.py`) separates the search
  space from the search algorithm.** A package is a boolean vector, one
  bit per catalog entry, decoded in catalog order; `PackageProblem`
  answers only "is this selection feasible" (no violated
  `mutual_exclusions`, fits an optional `budget_brl`) and "which entries
  does it contain." It does not know NSGA-II, pymoo, or any other backend
  exists — a Bayesian-optimization backend can be built against the same
  class without touching it.
- **NSGA-II (`pymoo`) is the first search backend, not the only one.**
  `arteria/optimize/nsga2.py`'s `run_nsga2()` wraps `PackageProblem` in a
  pymoo `Problem` (binary sampling, two-point crossover, bit-flip
  mutation) and returns the non-dominated front as `ParetoPackage`
  objects (entry ids, raw metrics, a crowding-distance diversity rank).
  Chosen over Bayesian optimization *for this first pass* because it
  needs no surrogate model and returns a real front for free; the
  sample-inefficiency that would matter against a real SUMO evaluator
  does not matter yet against a free synthetic one.
- **The evaluator is an injected `Callable[[Sequence[CatalogEntry]],
  dict[str, float]]`, not a hardcoded SUMO call.** `evaluate_package_stub`
  (`problem.py`) is the only evaluator wired in today: deterministic,
  derived only from catalog metadata (`cost_estimate_brl`, `complexity`),
  never a traffic-impact estimate — explicitly not evidence, per ADR
  0009. The real SUMO-backed evaluator (P6.1) is a drop-in replacement
  matching the same `Evaluator` signature; nothing in `nsga2.py` assumes
  which one is in use.
- **`PackageCache` (`arteria/optimize/cache.py`) memoizes by the sorted
  tuple of included entry ids, not the raw bit vector or generation
  index**, and persists to JSON. This is what "resume" means here
  (`run_nsga2(..., checkpoint_path=..., resume=True)`): a resumed run
  re-runs the GA from scratch but never re-evaluates a package an earlier
  run already scored. It deliberately does not checkpoint pymoo's own
  `Algorithm`/population state — a narrower scope than the roadmap line
  (P7.6) literally reads, chosen because cache-based resume is what
  actually matters once evaluation is expensive (a real SUMO run), while
  resuming the GA's exact population is not needed to get that benefit.
- **Parallel/distributed evaluation (the other half of P7.3) and
  experiment tracking beyond the cache's own JSON (P7.7) are out of
  scope for this pass.** `nsga2.py` evaluates each generation in-process,
  serially — fine while the evaluator is a cheap stub. Optuna/BoTorch
  backends and random/greedy baselines (to demonstrate NSGA-II earns its
  complexity) are likewise not built yet; `PackageProblem`'s
  backend-agnostic design is what makes adding them later a new module,
  not a rewrite of this one.

## Consequences

- Easier: P7.6 (Pareto front analysis) has real, if synthetic, fronts to
  analyze immediately, without waiting on P6.1. Swapping in the real
  SUMO-backed evaluator later is a one-line change at each `run_nsga2()`
  call site (pass a different `Evaluator`), not a redesign — the
  `PackageProblem`/`Evaluator`/`PackageCache` seams are exactly where
  that swap happens. A Bayesian-optimization backend can be added as a
  sibling to `nsga2.py` against the same `PackageProblem`, for a
  sample-efficiency comparison once real evaluations are expensive
  enough to justify it.
- Harder: the binary decision vector's size is the catalog's entry
  count, so a much larger real catalog (hundreds of candidate
  interventions for a full city) may strain `pymoo`'s default
  operators or need a smarter encoding/crossover — not addressed here,
  since the toy catalog this module is tested against is small by
  construction (ADR 0009). Nothing here enforces that a package's
  included entries are all mutually *compatible* beyond
  `mutual_exclusions` and budget — a planner-reviewed package can still
  be nonsensical in ways P5.4's `validity.py` or P5.6's catalog review
  would need to catch, since `PackageProblem` doesn't call either.
- Risk/trade-off: NSGA-II's main weakness — needing far more evaluations
  than a surrogate-based method to find a comparable front — is invisible
  today because the evaluator is free. Once P6.1 wires in a real,
  expensive SUMO-backed evaluator, this trade-off becomes real money
  (compute time, or wall-clock before a planner sees results), and
  whether optuna/BoTorch should become the *primary* backend rather than
  a baseline comparison should be revisited then, with real per-evaluation
  cost numbers in hand — not guessed now.
