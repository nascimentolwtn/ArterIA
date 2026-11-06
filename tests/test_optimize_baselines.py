from pathlib import Path

from arteria.interventions.catalog import load_catalog
from arteria.optimize.baselines import greedy_baseline, random_search_baseline
from arteria.optimize.problem import PackageProblem

FIXTURES = Path(__file__).parent / "fixtures"


def _problem() -> PackageProblem:
    return PackageProblem(load_catalog(FIXTURES / "toy-catalog.yaml"))


def _assert_all_feasible(problem: PackageProblem, result) -> None:
    by_id = {entry.id: i for i, entry in enumerate(problem.catalog.entries)}
    for package in result.pareto_front:
        selection = [False] * problem.n_entries
        for entry_id in package.entry_ids:
            selection[by_id[entry_id]] = True
        assert problem.is_feasible(selection)


def test_random_search_baseline_returns_a_nonempty_feasible_front() -> None:
    result = random_search_baseline(_problem(), n_samples=30, seed=42)
    assert len(result.pareto_front) > 0
    _assert_all_feasible(_problem(), result)


def test_random_search_baseline_is_reproducible_with_the_same_seed() -> None:
    first = random_search_baseline(_problem(), n_samples=30, seed=42)
    second = random_search_baseline(_problem(), n_samples=30, seed=42)

    first_front = sorted(tuple(p.entry_ids) for p in first.pareto_front)
    second_front = sorted(tuple(p.entry_ids) for p in second.pareto_front)
    assert first_front == second_front


def test_random_search_baseline_populates_the_evaluation_cache() -> None:
    result = random_search_baseline(_problem(), n_samples=30, seed=42)
    assert len(result.cache) > 0


def test_greedy_baseline_returns_a_nonempty_feasible_front() -> None:
    result = greedy_baseline(_problem())
    assert len(result.pareto_front) > 0
    _assert_all_feasible(_problem(), result)


def test_greedy_baseline_includes_the_cheapest_entry_first() -> None:
    result = greedy_baseline(_problem())
    # junction-y-turn-restriction (5000 BRL, no mutual exclusions) is the
    # cheapest entry and has nothing blocking it, so the final (priciest,
    # highest-benefit) front member always includes it.
    final_package = max(result.pareto_front, key=lambda p: p.metrics["cost_brl"])
    assert "junction-y-turn-restriction" in final_package.entry_ids


def test_greedy_baseline_is_deterministic() -> None:
    first = greedy_baseline(_problem())
    second = greedy_baseline(_problem())

    first_front = sorted(tuple(p.entry_ids) for p in first.pareto_front)
    second_front = sorted(tuple(p.entry_ids) for p in second.pareto_front)
    assert first_front == second_front


def test_greedy_baseline_skips_an_entry_that_would_make_the_package_infeasible() -> None:
    result = greedy_baseline(_problem())
    # busline-x-one-way (15000 BRL) and busline-x-bus-lane (120000 BRL) are
    # mutually exclusive; the cheaper one is kept, the pricier one dropped
    # from every package on the greedy path.
    for package in result.pareto_front:
        assert not {"busline-x-one-way", "busline-x-bus-lane"}.issubset(package.entry_ids)
