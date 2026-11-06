from pathlib import Path

from arteria.optimize.cache import PackageCache

ABC = frozenset({"a", "b", "c"})
AB = frozenset({"a", "b"})


def test_get_on_empty_cache_misses() -> None:
    cache = PackageCache()
    assert cache.get(ABC) is None


def test_put_then_get_returns_stored_metrics() -> None:
    cache = PackageCache()
    cache.put(ABC, {"cost_brl": 100.0, "estimated_benefit": 3.0})
    assert cache.get(ABC) == {"cost_brl": 100.0, "estimated_benefit": 3.0}


def test_get_is_order_independent_and_key_is_the_id_set_not_insertion_order() -> None:
    cache = PackageCache()
    cache.put(frozenset({"b", "a", "c"}), {"cost_brl": 1.0, "estimated_benefit": 1.0})
    assert cache.get(frozenset({"c", "b", "a"})) == {"cost_brl": 1.0, "estimated_benefit": 1.0}


def test_different_entry_id_set_misses() -> None:
    cache = PackageCache()
    cache.put(ABC, {"cost_brl": 100.0, "estimated_benefit": 3.0})
    assert cache.get(AB) is None


def test_save_and_load_round_trips(tmp_path: Path) -> None:
    cache = PackageCache()
    cache.put(ABC, {"cost_brl": 100.0, "estimated_benefit": 3.0})
    cache.put(AB, {"cost_brl": 50.0, "estimated_benefit": 2.0})

    path = tmp_path / "cache.json"
    cache.save(path)

    loaded = PackageCache.load(path)
    assert loaded.get(ABC) == {"cost_brl": 100.0, "estimated_benefit": 3.0}
    assert loaded.get(AB) == {"cost_brl": 50.0, "estimated_benefit": 2.0}
    assert len(loaded) == 2
