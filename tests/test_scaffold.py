from pathlib import Path

import pytest

from arteria.scaffold import CityAlreadyExistsError, create_city

REPO_ROOT = Path(__file__).parent.parent


def test_creates_and_validates_a_new_city(tmp_path: Path) -> None:
    cities_root = tmp_path / "cities"
    cities_root.mkdir()
    import shutil

    shutil.copytree(REPO_ROOT / "cities" / "_template", cities_root / "_template")

    city_dir = create_city("newcity", cities_root)

    assert city_dir == cities_root / "newcity"
    assert "name: newcity" in (city_dir / "city.yaml").read_text()


def test_refuses_to_overwrite_an_existing_city(tmp_path: Path) -> None:
    cities_root = tmp_path / "cities"
    cities_root.mkdir()
    (cities_root / "existing").mkdir()

    with pytest.raises(CityAlreadyExistsError):
        create_city("existing", cities_root)
