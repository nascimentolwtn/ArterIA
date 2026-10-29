from pathlib import Path

import pytest
from pydantic import ValidationError

from arteria.config import (
    ScenarioConfig,
    load_city_config,
    load_data_manifest,
    load_scenario_config,
)

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


def test_toy_scenario_config_validates() -> None:
    scenario = load_scenario_config(FIXTURES / "toy-scenario.yaml")
    assert scenario.name == "baseline"
    assert scenario.city == "toy"
    assert scenario.net_file == "../../network/toy.net.xml"
    assert scenario.route_files == ["toy.rou.xml"]
    assert scenario.time_window is not None
    assert scenario.time_window.start == "07:00"
    assert scenario.seeds == [1, 2, 3]
    assert scenario.replications == 3


def test_scenario_config_defaults_to_one_replication_and_no_seeds() -> None:
    scenario = ScenarioConfig.model_validate({"name": "baseline", "city": "toy", "net_file": "n"})
    assert scenario.replications == 1
    assert scenario.seeds == []
    assert scenario.route_files == []


def test_scenario_config_rejects_seed_count_mismatching_replications() -> None:
    with pytest.raises(ValidationError, match="replications=2"):
        ScenarioConfig.model_validate(
            {
                "name": "baseline",
                "city": "toy",
                "net_file": "n",
                "seeds": [1, 2, 3],
                "replications": 2,
            }
        )
