from pathlib import Path

from arteria.interventions.catalog import load_catalog
from arteria.optimize.nsga2 import run_nsga2
from arteria.optimize.problem import PackageProblem

FIXTURES = Path(__file__).parent / "fixtures"


def _problem() -> PackageProblem:
    return PackageProblem(load_catalog(FIXTURES / "toy-catalog.yaml"))


def test_run_nsga2_terminates_with_a_nonempty_pareto_front() -> None:
    result = run_nsga2(_problem(), pop_size=8, n_gen=3, seed=42)
    assert len(result.pareto_front) > 0


def test_run_nsga2_front_members_are_all_feasible() -> None:
    problem = _problem()
    result = run_nsga2(problem, pop_size=8, n_gen=3, seed=42)

    by_id = {entry.id: i for i, entry in enumerate(problem.catalog.entries)}
    for package in result.pareto_front:
        selection = [False] * problem.n_entries
        for entry_id in package.entry_ids:
            selection[by_id[entry_id]] = True
        assert problem.is_feasible(selection)


def test_run_nsga2_is_reproducible_with_the_same_seed() -> None:
    first = run_nsga2(_problem(), pop_size=8, n_gen=3, seed=42)
    second = run_nsga2(_problem(), pop_size=8, n_gen=3, seed=42)

    first_fronts = sorted(tuple(p.entry_ids) for p in first.pareto_front)
    second_fronts = sorted(tuple(p.entry_ids) for p in second.pareto_front)
    assert first_fronts == second_fronts


def test_run_nsga2_populates_the_evaluation_cache() -> None:
    result = run_nsga2(_problem(), pop_size=8, n_gen=3, seed=42)
    assert len(result.cache) > 0


def test_run_nsga2_checkpoint_resume_reuses_cached_evaluations(tmp_path: Path) -> None:
    checkpoint_path = tmp_path / "cache.json"

    first = run_nsga2(_problem(), pop_size=8, n_gen=3, seed=42, checkpoint_path=checkpoint_path)
    assert checkpoint_path.exists()

    second = run_nsga2(
        _problem(),
        pop_size=8,
        n_gen=3,
        seed=42,
        checkpoint_path=checkpoint_path,
        resume=True,
    )

    # Resuming never loses previously-cached packages; the cache only grows.
    assert len(second.cache) >= len(first.cache)
    for entry_id_tuple, metrics in [
        (tuple(sorted(p.entry_ids)), p.metrics) for p in first.pareto_front
    ]:
        assert second.cache.get(frozenset(entry_id_tuple)) == metrics
