"""NSGA-II wiring over the catalog, plus Pareto-front and resume support
(roadmap R9: P7.2 optimizer wiring, P7.6 Pareto analysis, P7.7 experiment
tracking).

`run_nsga2` runs pymoo's NSGA-II over a `PackageProblem`'s binary
decision vector (one bit per catalog entry), using whatever evaluator is
passed in — by default `problem.evaluate_package_stub`, the synthetic
placeholder this remote session is scoped to (ADR 0009; no SUMO here).
Wiring a different evaluator (the real SUMO-backed one, P6.1) or a
different optimizer backend (Bayesian optimization/`optuna`, P7.2) is a
drop-in future change, not something this module needs to anticipate.

**Resume scope, narrower than the roadmap line (P7.6) literally reads:**
pymoo's own `Algorithm`/checkpoint object is not wired up here. "Resume"
means the `PackageCache` is persisted to `checkpoint_path` and reloaded
on the next call with `resume=True`, so a resumed run re-runs the GA from
scratch but never re-evaluates a package an earlier run already scored —
every repeat proposal of a previously-seen package is a cache hit. That
is a real, correct instance of P7.3/P7.6 resume-without-re-evaluation,
but it does not resume the GA's own population/generation state; a
future pass can checkpoint pymoo's algorithm object directly if that
finer-grained resume is ever needed. Parallel/distributed evaluation
(P7.3's process-pool/cluster half) is likewise out of scope — the stub
evaluator is cheap enough that this module evaluates a generation
in-process, serially.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from pydantic import BaseModel
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import BinaryRandomSampling
from pymoo.optimize import minimize

from arteria.interventions.catalog import CatalogEntry
from arteria.optimize.cache import PackageCache
from arteria.optimize.problem import PackageProblem, evaluate_package_stub

#: Objective values assigned to an infeasible candidate. Large enough that
#: no feasible toy- or real-catalog package could plausibly cost more, and
#: a benefit of 0 is the worst case any feasible package can score (an
#: empty package also scores 0, but it is always feasible, so this never
#: ties with a *better* feasible point — only with that one equally-bad one).
_INFEASIBLE_COST_BRL = 1e12
_INFEASIBLE_BENEFIT = 0.0

Evaluator = Callable[[Sequence[CatalogEntry]], dict[str, float]]


class ParetoPackage(BaseModel):
    """One non-dominated package from a completed NSGA-II run.

    `entry_ids` is the sorted list of included catalog entry ids.
    `rank` orders front members by crowding distance (most to least
    isolated in objective space) when pymoo's result exposes it;
    `None` if it doesn't. All front members share pymoo's domination
    rank of 0 by construction (they are the non-dominated front), so
    `rank` here is a diversity order within the front, not a redundant
    copy of that constant.
    """

    entry_ids: list[str]
    metrics: dict[str, float]
    rank: int | None = None


@dataclass
class OptimizationResult:
    pareto_front: list[ParetoPackage]
    cache: PackageCache = field(default_factory=PackageCache)


class _BinaryPackageProblem(Problem):
    """pymoo `Problem` adapter: binary catalog selection -> objective pair.

    pymoo always minimizes, so `"estimated_benefit"` (maximize) is
    negated before being handed to pymoo; callers reading `ParetoPackage.
    metrics` see the original, un-negated values.
    """

    def __init__(self, problem: PackageProblem, evaluator: Evaluator) -> None:
        super().__init__(n_var=problem.n_entries, n_obj=2, xl=0, xu=1, vtype=bool)
        self._problem = problem
        self._evaluator = evaluator

    def _evaluate(self, x: np.ndarray, out: dict, *args: object, **kwargs: object) -> None:
        objectives = np.empty((x.shape[0], 2))
        for i, row in enumerate(x):
            selection = [bool(v) for v in row]
            if not self._problem.is_feasible(selection):
                objectives[i] = [_INFEASIBLE_COST_BRL, -_INFEASIBLE_BENEFIT]
                continue
            entries = self._problem.selected_entries(selection)
            metrics = self._evaluator(entries)
            objectives[i] = [metrics["cost_brl"], -metrics["estimated_benefit"]]
        out["F"] = objectives


def _cached_evaluator(evaluator: Evaluator, cache: PackageCache) -> Evaluator:
    def cached(entries: Sequence[CatalogEntry]) -> dict[str, float]:
        entry_ids = frozenset(entry.id for entry in entries)
        cached_metrics = cache.get(entry_ids)
        if cached_metrics is not None:
            return cached_metrics
        metrics = evaluator(entries)
        cache.put(entry_ids, metrics)
        return metrics

    return cached


def _extract_pareto_front(
    res: object, problem: PackageProblem, evaluator: Evaluator
) -> list[ParetoPackage]:
    front_x = np.atleast_2d(res.X)

    crowding: np.ndarray | None = None
    try:
        raw_crowding = res.opt.get("crowding")
        if raw_crowding is not None:
            candidate = np.asarray(raw_crowding, dtype=float)
            if candidate.shape[0] == front_x.shape[0] and not np.any(np.isnan(candidate)):
                crowding = candidate
    except Exception:  # pymoo attribute access can fail in several ways; fall back to no order.
        crowding = None

    order = range(len(front_x))
    if crowding is not None and len(crowding) == len(front_x):
        # Most isolated (largest crowding distance) first.
        order = sorted(order, key=lambda i: -crowding[i])

    packages = []
    for rank, i in enumerate(order):
        selection = [bool(v) for v in front_x[i]]
        entries = problem.selected_entries(selection)
        metrics = evaluator(entries)
        packages.append(
            ParetoPackage(
                entry_ids=sorted(entry.id for entry in entries),
                metrics=metrics,
                rank=rank,
            )
        )
    return packages


def run_nsga2(
    problem: PackageProblem,
    evaluator: Evaluator = evaluate_package_stub,
    *,
    pop_size: int = 20,
    n_gen: int = 10,
    seed: int | None = 42,
    checkpoint_path: Path | None = None,
    resume: bool = False,
) -> OptimizationResult:
    """Run pymoo's NSGA-II over `problem`'s catalog and return its Pareto front.

    `seed` is forwarded to pymoo's `minimize` for reproducibility: the
    same `problem`/`evaluator`/`seed` always returns the same front. See
    the module docstring for exactly what `checkpoint_path`/`resume`
    does and does not resume.
    """
    cache = PackageCache()
    if resume and checkpoint_path is not None and checkpoint_path.exists():
        cache = PackageCache.load(checkpoint_path)

    cached_evaluator = _cached_evaluator(evaluator, cache)
    pymoo_problem = _BinaryPackageProblem(problem, cached_evaluator)
    algorithm = NSGA2(
        pop_size=pop_size,
        sampling=BinaryRandomSampling(),
        crossover=TwoPointCrossover(),
        mutation=BitflipMutation(),
        eliminate_duplicates=True,
    )
    res = minimize(pymoo_problem, algorithm, ("n_gen", n_gen), seed=seed, verbose=False)

    pareto_front = _extract_pareto_front(res, problem, cached_evaluator)

    if checkpoint_path is not None:
        cache.save(checkpoint_path)

    return OptimizationResult(pareto_front=pareto_front, cache=cache)
