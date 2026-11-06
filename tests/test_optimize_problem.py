from pathlib import Path

from arteria.interventions.catalog import load_catalog
from arteria.optimize.problem import PackageProblem, evaluate_package_stub

FIXTURES = Path(__file__).parent / "fixtures"

BUS_LANE = 0
ONE_WAY = 1
TURN_RESTRICTION = 2


def _problem(**kwargs: object) -> PackageProblem:
    catalog = load_catalog(FIXTURES / "toy-catalog.yaml")
    return PackageProblem(catalog, **kwargs)


def test_n_entries_matches_catalog() -> None:
    assert _problem().n_entries == 3


def test_is_feasible_rejects_both_mutually_exclusive_entries() -> None:
    problem = _problem()
    selection = [False, False, False]
    selection[BUS_LANE] = True
    selection[ONE_WAY] = True
    assert problem.is_feasible(selection) is False


def test_is_feasible_accepts_only_one_of_the_mutually_exclusive_pair() -> None:
    problem = _problem()

    only_bus_lane = [False, False, False]
    only_bus_lane[BUS_LANE] = True
    assert problem.is_feasible(only_bus_lane) is True

    only_one_way = [False, False, False]
    only_one_way[ONE_WAY] = True
    assert problem.is_feasible(only_one_way) is True


def test_is_feasible_accepts_unconstrained_entry_alongside_either() -> None:
    problem = _problem()
    selection = [False, False, False]
    selection[ONE_WAY] = True
    selection[TURN_RESTRICTION] = True
    assert problem.is_feasible(selection) is True


def test_is_feasible_respects_budget_cutoff() -> None:
    # bus lane alone costs 120000.0, well above a 50000 budget.
    problem = _problem(budget_brl=50000.0)
    selection = [False, False, False]
    selection[BUS_LANE] = True
    assert problem.is_feasible(selection) is False


def test_is_feasible_accepts_package_within_budget() -> None:
    # one-way (15000) + turn restriction (5000) = 20000, within a 50000 budget.
    problem = _problem(budget_brl=50000.0)
    selection = [False, False, False]
    selection[ONE_WAY] = True
    selection[TURN_RESTRICTION] = True
    assert problem.is_feasible(selection) is True


def test_is_feasible_with_no_budget_set_is_unconstrained_by_cost() -> None:
    # bus lane (120000) + turn restriction (5000) would fail any small budget,
    # but with no budget_brl set, cost plays no role in feasibility.
    problem = _problem()
    selection = [False, False, False]
    selection[BUS_LANE] = True
    selection[TURN_RESTRICTION] = True
    assert problem.is_feasible(selection) is True


def test_selected_entries_returns_only_included_entries_in_catalog_order() -> None:
    problem = _problem()
    selection = [False, False, False]
    selection[BUS_LANE] = True
    selection[TURN_RESTRICTION] = True
    entries = problem.selected_entries(selection)
    assert [e.id for e in entries] == ["busline-x-bus-lane", "junction-y-turn-restriction"]


def test_selected_entries_rejects_wrong_length_selection() -> None:
    problem = _problem()
    try:
        problem.selected_entries([True, False])
    except ValueError as exc:
        assert "3" in str(exc)
    else:
        raise AssertionError("expected ValueError for mismatched selection length")


def test_evaluate_package_stub_is_deterministic() -> None:
    catalog = load_catalog(FIXTURES / "toy-catalog.yaml")
    entries = catalog.entries[:2]
    first = evaluate_package_stub(entries)
    second = evaluate_package_stub(entries)
    assert first == second


def test_evaluate_package_stub_empty_package_scores_zero_cost() -> None:
    metrics = evaluate_package_stub([])
    assert metrics["cost_brl"] == 0.0
    assert metrics["estimated_benefit"] == 0.0


def test_evaluate_package_stub_sums_cost_and_treats_missing_cost_as_zero() -> None:
    catalog = load_catalog(FIXTURES / "toy-catalog.yaml")
    bus_lane = next(e for e in catalog.entries if e.id == "busline-x-bus-lane")
    one_way = next(e for e in catalog.entries if e.id == "busline-x-one-way")

    metrics = evaluate_package_stub([bus_lane, one_way])
    assert metrics["cost_brl"] == 120000.0 + 15000.0


def test_evaluate_package_stub_benefit_grows_with_more_entries() -> None:
    catalog = load_catalog(FIXTURES / "toy-catalog.yaml")
    one = evaluate_package_stub(catalog.entries[:1])
    two = evaluate_package_stub(catalog.entries[:2])
    assert two["estimated_benefit"] > one["estimated_benefit"]
