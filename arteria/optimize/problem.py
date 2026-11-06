"""Package decision problem over the intervention catalog (roadmap P7.1).

A *package* is a subset of `InterventionCatalog.entries`, encoded as one
boolean per entry (included / not included) in catalog order.
`PackageProblem` wraps a catalog and answers the two questions every
optimizer backend (NSGA-II today, Bayesian optimization or a surrogate
later — P7.2/P7.4) needs about a candidate package: is it feasible, and
which entries does it actually contain. It deliberately knows nothing
about *how* a package is evaluated or searched; `nsga2.py` builds the
pymoo-facing problem on top of this one.

`evaluate_package_stub` is the synthetic evaluator this remote session is
scoped to (ADR 0009): there is no real SUMO run available here, so its
numbers are placeholder objective values derived only from catalog
metadata (cost, complexity), never a traffic-impact estimate. Same
synthetic-vs-real framing as `arteria/calibration/goodness_of_fit.py`. The
real evaluator — running SUMO per package (roadmap P6.1) — is desk-only
future work and is not attempted here.
"""

from __future__ import annotations

from collections.abc import Sequence

from arteria.interventions.catalog import CatalogEntry, InterventionCatalog

#: Ordinal weight used by `evaluate_package_stub` to turn a qualitative
#: `Complexity` into a number; higher complexity contributes more to the
#: synthetic "benefit" score, which is the opposite of intuition but keeps
#: the stub's two objectives in tension (more/costlier entries score higher
#: on both axes) so a toy NSGA-II run actually has a front to find.
_COMPLEXITY_WEIGHT: dict[str, float] = {"low": 1.0, "medium": 2.0, "high": 3.0}


class PackageProblem:
    """Feasibility and decoding rules for packages drawn from a catalog.

    `budget_brl`, when set, rejects any selection whose included entries'
    summed `cost_estimate_brl` exceeds it; entries with no cost estimate
    (`cost_estimate_brl is None`) count as zero cost for this check, since
    an unestimated cost is not evidence the package is unaffordable.
    """

    def __init__(self, catalog: InterventionCatalog, *, budget_brl: float | None = None) -> None:
        self.catalog = catalog
        self.budget_brl = budget_brl

    @property
    def n_entries(self) -> int:
        return len(self.catalog.entries)

    def selected_entries(self, selection: Sequence[bool]) -> list[CatalogEntry]:
        """The catalog entries `selection` includes, in catalog order.

        `selection` must have exactly `n_entries` elements, one per entry
        in `self.catalog.entries`, in that same order.
        """
        if len(selection) != self.n_entries:
            raise ValueError(
                f"selection has {len(selection)} elements, catalog has {self.n_entries} entries"
            )
        return [entry for entry, included in zip(self.catalog.entries, selection) if included]

    def is_feasible(self, selection: Sequence[bool]) -> bool:
        """Whether `selection` violates no mutual exclusion and fits the budget."""
        entries = self.selected_entries(selection)
        included_ids = {entry.id for entry in entries}
        for entry in entries:
            if included_ids & set(entry.mutual_exclusions):
                return False
        if self.budget_brl is not None:
            total_cost = sum(entry.cost_estimate_brl or 0.0 for entry in entries)
            if total_cost > self.budget_brl:
                return False
        return True


def evaluate_package_stub(entries: Sequence[CatalogEntry]) -> dict[str, float]:
    """Synthetic, deterministic placeholder objective values for `entries`.

    **This is not a traffic-impact estimate.** No SUMO run backs these
    numbers; they are a stub for wiring the optimizer (roadmap R9) ahead
    of the real evaluator (P6.1, desk-only — see ADR 0009). Output depends
    only on `entries`' catalog metadata, never on randomness, so the same
    package always scores the same:

    - `"cost_brl"` (minimize): the sum of `cost_estimate_brl`, treating a
      missing estimate as zero.
    - `"estimated_benefit"` (maximize): entry count plus each entry's
      ordinal complexity weight (`low=1, medium=2, high=3`) — a package
      with more, costlier-to-execute entries scores a higher placeholder
      benefit, standing in for "more intervention = more plausible
      traffic effect" until a real evaluator can measure it.
    """
    cost_brl = sum(entry.cost_estimate_brl or 0.0 for entry in entries)
    estimated_benefit = sum(1.0 + _COMPLEXITY_WEIGHT[entry.complexity] for entry in entries)
    return {"cost_brl": cost_brl, "estimated_benefit": estimated_benefit}
