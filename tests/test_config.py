from pathlib import Path

from arteria.config import load_city_config, load_data_manifest

FIXTURES = Path(__file__).parent / "fixtures"
REPO_ROOT = Path(__file__).parent.parent


def test_toy_city_config_validates() -> None:
    config = load_city_config(FIXTURES / "toy-city.yaml")
    assert config.name == "toy"
    assert config.time_windows["am-peak"].start == "07:00"


def test_toy_data_manifest_validates() -> None:
    manifest = load_data_manifest(FIXTURES / "toy-data-manifest.yaml")
    ids = {entry.id for entry in manifest.sources}
    assert ids == {"toy-public-source", "toy-restricted-source"}


def test_sjc_city_config_validates() -> None:
    load_city_config(REPO_ROOT / "cities" / "sjc" / "city.yaml")


def test_sjc_data_manifest_validates() -> None:
    manifest = load_data_manifest(REPO_ROOT / "cities" / "sjc" / "data-manifest.yaml")
    assert len(manifest.sources) >= 10
    assert all(
        entry.status in {"public_available", "deferred", "declined"} for entry in manifest.sources
    )


def test_template_city_config_validates() -> None:
    load_city_config(REPO_ROOT / "cities" / "_template" / "city.yaml")


def test_template_data_manifest_validates() -> None:
    manifest = load_data_manifest(REPO_ROOT / "cities" / "_template" / "data-manifest.yaml")
    assert manifest.sources == []
