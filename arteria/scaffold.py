"""City scaffolding (roadmap P10.1, pulled forward into P0 per ADR 0002):
turn `cities/_template/` into a new, schema-validated `cities/<name>/`.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from arteria.config import load_city_config, load_data_manifest

TEMPLATE_DIRNAME = "_template"

_VALID_NAME = re.compile(r"^[a-z][a-z0-9_-]*$")


class CityAlreadyExistsError(Exception):
    pass


class InvalidCityNameError(ValueError):
    pass


def create_city(name: str, cities_root: Path) -> Path:
    """Copy `cities/_template/` to `cities/<name>/`, set `name`, and validate it.

    Raises `InvalidCityNameError` if `name` isn't a plain lowercase slug (this
    also keeps `cities_root / name` from ever resolving outside `cities/`),
    `CityAlreadyExistsError` if `cities/<name>/` already exists, and whatever
    `pydantic.ValidationError` the schema raises if the resulting config
    doesn't validate (leaving the copy in place for the caller to fix).
    """
    if not _VALID_NAME.fullmatch(name):
        raise InvalidCityNameError(
            f"{name!r} is not a valid city slug: must start with a lowercase "
            "letter and contain only lowercase letters, digits, '-' or '_'"
        )

    template_dir = cities_root / TEMPLATE_DIRNAME
    city_dir = cities_root / name

    if city_dir.exists():
        raise CityAlreadyExistsError(f"cities/{name}/ already exists")

    shutil.copytree(template_dir, city_dir)

    city_yaml = city_dir / "city.yaml"
    city_yaml.write_text(
        city_yaml.read_text().replace("name: <city-slug>", f"name: {name}", 1)
    )

    load_city_config(city_yaml)
    load_data_manifest(city_dir / "data-manifest.yaml")

    return city_dir
