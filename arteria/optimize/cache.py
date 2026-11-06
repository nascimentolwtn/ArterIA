"""Package evaluation cache (roadmap P7.3).

Evaluating a package is the expensive step this module set exists to
avoid repeating: a NSGA-II population routinely re-proposes a package it
(or an earlier run) already scored. `PackageCache` keys on the *sorted
tuple of included entry ids*, not the raw boolean vector, so a hit does
not depend on entry ordering in the catalog staying stable, and persists
to JSON so a later run can `load` a previous run's cache instead of
re-evaluating packages it already has scores for. With today's stub
evaluator (`problem.evaluate_package_stub`) this mostly saves wall clock
in tests; it is the same mechanism the real SUMO-backed evaluator (P6.1,
desk-only per ADR 0009) will need, where a cache hit is the difference
between skipping and re-running a full simulation.
"""

from __future__ import annotations

import json
from pathlib import Path


def _cache_key(entry_ids: frozenset[str]) -> str:
    return "|".join(sorted(entry_ids))


class PackageCache:
    """In-memory package-metrics cache, keyed by included-entry-id set."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, float]] = {}

    def get(self, entry_ids: frozenset[str]) -> dict[str, float] | None:
        return self._store.get(_cache_key(entry_ids))

    def put(self, entry_ids: frozenset[str], metrics: dict[str, float]) -> None:
        self._store[_cache_key(entry_ids)] = dict(metrics)

    def __len__(self) -> int:
        return len(self._store)

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self._store, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> PackageCache:
        cache = cls()
        with open(path, encoding="utf-8") as f:
            cache._store = json.load(f)
        return cache
