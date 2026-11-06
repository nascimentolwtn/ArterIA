"""Random and greedy baseline optimizers (roadmap P7.2, ADR 0008).

`nsga2.py` is a real optimizer; nothing yet shows whether NSGA-II is
actually earning its complexity over something far simpler. These two
baselines exist to answer that, against the same `PackageProblem` and
`Evaluator` seam NSGA-II uses, so a caller can compare fronts directly:

- `random_search_baseline` draws `n_samples` random feasible selections
  and keeps the non-dominated ones -- "what do you get for free by just
  trying things."
- `greedy_baseline` walks the catalog cheapest-entry-first, keeping each
  entry only if the package stays feasible, and keeps every
  non-dominated package seen along that one path -- "what does the
  simplest reasonable heuristic get you."

Both use `evaluate_package_stub` by default, the same synthetic,
catalog-metadata-only evaluator `nsga2.py` defaults to (ADR 0009: no real
SUMO run backs it). Both accept any `Evaluator`, so swapping in the real
evaluator later (P6.1) needs no change here either.
"""

from __future__ import annotations

import random
from collections.abc import Sequence

from arteria.interventions.catalog import CatalogEntry
from arteria.optimize.cache import PackageCache
from arteria.optimize.nsga2 import Evaluator, OptimizationResult, ParetoPackage
from arteria.optimize.problem import PackageProblem, evaluate_package_stub


def _cached(evaluator: Evaluator, cache: PackageCache) -> Evaluator:
    def wrapped(entries: Sequence[CatalogEntry]) -> dict[str, float]:
        entry_ids = frozenset(entry.id for entry in entries)
        cached_metrics = cache.get(entry_ids)
        if cached_metrics is not None:
            return cached_metrics
        metrics = evaluator(entries)
        cache.put(entry_ids, metrics)
        return metrics

    return wrapped


def _dominates(a: dict[str, float], b: dict[str, float]) -> bool:
    """Whether package `a` dominates `b` (minimize cost_brl, maximize estimated_benefit)."""
    at_least_as_good = (
        a["cost_brl"] <= b["cost_brl"] and a["estimated_benefit"] >= b["estimated_benefit"]
    )
    strictly_better = (
        a["cost_brl"] < b["cost_brl"] or a["estimated_benefit"] > b["estimated_benefit"]
    )
    return at_least_as_good and strictly_better


def _pareto_front(
    packages: dict[frozenset[str], dict[str, float]],
) -> list[ParetoPackage]:
    """The non-dominated subset of `packages`, deduplicated by entry-id set."""
    items = list(packages.items())
    front = [
        ParetoPackage(entry_ids=sorted(entry_ids), metrics=metrics)
        for entry_ids, metrics in items
        if not any(
            _dominates(other_metrics, metrics)
            for _, other_metrics in items
            if other_metrics is not metrics
        )
    ]

    def _sort_key(package: ParetoPackage) -> tuple[float, float]:
        return (package.metrics["cost_brl"], -package.metrics["estimated_benefit"])

    return sorted(front, key=_sort_key)


def random_search_baseline(
    problem: PackageProblem,
    evaluator: Evaluator = evaluate_package_stub,
    *,
    n_samples: int = 50,
    seed: int | None = 42,
    max_attempts_per_sample: int = 100,
) -> OptimizationResult:
    """Sample `n_samples` random feasible packages and return their Pareto front.

    Each sample draws a fresh random boolean vector, resampling up to
    `max_attempts_per_sample` times if it is infeasible (violates a
    mutual exclusion or the budget); a sample that never turns up
    feasible in that many attempts is skipped. Deterministic for a given
    `seed`.
    """
    rng = random.Random(seed)
    cache = PackageCache()
    cached_evaluator = _cached(evaluator, cache)

    packages: dict[frozenset[str], dict[str, float]] = {}
    for _ in range(n_samples):
        for _attempt in range(max_attempts_per_sample):
            selection = [rng.random() < 0.5 for _ in range(problem.n_entries)]
            if problem.is_feasible(selection):
                entries = problem.selected_entries(selection)
                entry_ids = frozenset(entry.id for entry in entries)
                packages[entry_ids] = cached_evaluator(entries)
                break

    return OptimizationResult(pareto_front=_pareto_front(packages), cache=cache)


def greedy_baseline(
    problem: PackageProblem,
    evaluator: Evaluator = evaluate_package_stub,
) -> OptimizationResult:
    """Walk the catalog cheapest-entry-first, keeping what stays feasible.

    Starting from the empty package, each catalog entry (sorted by
    ascending `cost_estimate_brl`, missing estimates treated as cheapest)
    is tentatively added; it is kept if the resulting selection is still
    feasible, dropped otherwise. The result is the non-dominated subset
    of every package seen along that single path, including the empty
    one -- not just the final package, since an earlier, cheaper point on
    the path may dominate it on one objective.
    """
    cache = PackageCache()
    cached_evaluator = _cached(evaluator, cache)

    ordered_indices = sorted(
        range(problem.n_entries),
        key=lambda i: problem.catalog.entries[i].cost_estimate_brl or 0.0,
    )

    selection = [False] * problem.n_entries
    packages: dict[frozenset[str], dict[str, float]] = {
        frozenset(): cached_evaluator(problem.selected_entries(selection))
    }
    for i in ordered_indices:
        candidate = list(selection)
        candidate[i] = True
        if problem.is_feasible(candidate):
            selection = candidate
            entries = problem.selected_entries(selection)
            entry_ids = frozenset(entry.id for entry in entries)
            packages[entry_ids] = cached_evaluator(entries)

    return OptimizationResult(pareto_front=_pareto_front(packages), cache=cache)
