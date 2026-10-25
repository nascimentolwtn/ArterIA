"""The `arteria` CLI (ADR 0002): one Typer entry point into `arteria/`."""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

import typer

from arteria import __version__
from arteria.scaffold import CityAlreadyExistsError, InvalidCityNameError, create_city

app = typer.Typer(help="ArterIA: AI-assisted decision-support tool for street-network planning.")
city_app = typer.Typer(help="City scaffolding (ADR 0002).")
app.add_typer(city_app, name="city")
studyarea_app = typer.Typer(help="Study-area polygon drafting (roadmap P1.4).")
app.add_typer(studyarea_app, name="studyarea")
osm_app = typer.Typer(help="OSM source download and extraction (roadmap P2.1).")
app.add_typer(osm_app, name="osm")
network_app = typer.Typer(help="netconvert build and validation (roadmap P2.2/P2.3/P2.5).")
app.add_typer(network_app, name="network")


@app.callback()
def main() -> None:
    """Forces subcommand mode (`arteria doctor`, ...) even with a single command today."""


@app.command()
def doctor() -> None:
    """Report the environment: Python/SUMO toolchain, SUMO_HOME, ARTERIA_DATA, disk space."""
    typer.echo(f"arteria {__version__}")
    typer.echo(f"Python: {sys.version.split()[0]}")

    sumo_home = os.environ.get("SUMO_HOME")
    typer.echo(f"SUMO_HOME: {sumo_home or 'not set'}")

    for binary in ("sumo", "netconvert", "osmium"):
        found = shutil.which(binary)
        typer.echo(f"{binary}: {found or 'not found on PATH'}")

    for var in ("ARTERIA_DATA", "ARTERIA_PRIVATE"):
        value = os.environ.get(var)
        if not value:
            typer.echo(f"{var}: not set")
            continue
        path = Path(value)
        writable = path.is_dir() and os.access(path, os.W_OK)
        typer.echo(f"{var}: {value} ({'writable' if writable else 'missing or not writable'})")

    try:
        usage = shutil.disk_usage(Path.cwd())
        typer.echo(f"Disk free at {Path.cwd()}: {usage.free / (1 << 30):.1f} GiB")
    except OSError as exc:
        typer.echo(f"Disk check failed: {exc}")


@city_app.command("new")
def city_new(name: str) -> None:
    """Scaffold `cities/<name>/` from `cities/_template/` and validate it.

    `crs`, `sumo_version`, and the bounding polygon are left as the
    template's placeholders — fill them in before relying on this city for
    anything beyond schema-level validation.
    """
    cities_root = Path.cwd() / "cities"
    try:
        city_dir = create_city(name, cities_root)
    except (CityAlreadyExistsError, InvalidCityNameError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Created {city_dir}/ — fill in crs, sumo_version, and the bounding polygon.")


@studyarea_app.command("build")
def studyarea_build(
    city: str = typer.Option(..., "--city"),
    user_agent: str = typer.Option(
        ...,
        "--user-agent",
        help="Required by Nominatim's usage policy: identify this tool and "
        "how to reach you, e.g. 'arteria-sjc/0.1 (you@example.com)'. Do not "
        "reuse a placeholder from docs — Nominatim blocks generic ones.",
    ),
    include_future: bool = typer.Option(
        False,
        "--include-future",
        help="Also geocode candidates marked `enabled: false` "
        "(future extensions not in current priority scope).",
    ),
) -> None:
    """Geocode each candidate's landmarks in `cities/<city>/study-areas.yaml`
    via Nominatim and write `cities/<city>/study-areas.geojson`.

    Needs real network access to nominatim.openstreetmap.org — blocked in
    remote Claude sessions (ADR 0009). Run this at the desk. Treat the
    output as a draft: verify it against satellite imagery/OSM before using
    it for a real P2.1 OSM extraction.
    """
    # Lazy import: shapely/pyproj/numpy are the optional `geo` extra, not a
    # dependency of the CLI as a whole (`arteria doctor` etc. must not need
    # them installed).
    from arteria.config import load_city_config
    from arteria.network.study_area import (
        build_study_areas,
        geocode_nominatim,
        load_study_area_config,
    )

    city_dir = Path.cwd() / "cities" / city
    config = load_study_area_config(city_dir / "study-areas.yaml")
    city_config = load_city_config(city_dir / "city.yaml")

    def rate_limited_geocode(query: str) -> tuple[float, float]:
        result = geocode_nominatim(query, user_agent=user_agent)
        time.sleep(1.1)  # Nominatim usage policy: max 1 request/second
        return result

    geojson = build_study_areas(
        config,
        rate_limited_geocode,
        projected_crs=city_config.crs,
        include_disabled=include_future,
    )
    out_path = city_dir / "study-areas.geojson"
    out_path.write_text(json.dumps(geojson, indent=2, ensure_ascii=False))
    typer.echo(f"Wrote {out_path} ({len(geojson['features'])} candidate polygon(s)).")


@osm_app.command("fetch")
def osm_fetch(
    city: str = typer.Option(..., "--city"),
    candidate: str = typer.Option(..., "--candidate"),
    pbf_path: Path | None = typer.Option(
        None,
        "--pbf-path",
        help="Use this local .osm.pbf instead of downloading one.",
    ),
    source_url: str | None = typer.Option(
        None,
        "--source-url",
        help="Regional OSM extract to download if --pbf-path isn't given. "
        "Defaults to the Geofabrik 'sudeste' extract (default_geofabrik_url()).",
    ),
) -> None:
    """Fetch (or reuse) a regional OSM PBF and clip it to a study-area
    candidate's polygon, per `cities/<city>/study-areas.geojson`.

    Needs real network access and a real `osmium` binary — blocked in
    remote Claude sessions (ADR 0009). Run this at the desk.
    """
    from arteria.network.osm_fetch import (
        OsmExtractError,
        OsmFetchError,
        default_geofabrik_url,
        download_source_pbf,
        extract_candidate_polygon,
        extract_osm,
    )

    city_dir = Path.cwd() / "cities" / city
    raw_dir = city_dir / "network" / "raw"

    try:
        if pbf_path is not None:
            source_pbf = pbf_path
        else:
            url = source_url or default_geofabrik_url()
            source_pbf = raw_dir / url.rsplit("/", 1)[-1]
            if source_pbf.exists():
                typer.echo(f"Reusing cached {source_pbf}")
            else:
                download_source_pbf(url, source_pbf)
                typer.echo(f"Downloaded {url} -> {source_pbf}")

        polygon = extract_candidate_polygon(city_dir / "study-areas.geojson", candidate)
        output_path = raw_dir / f"{city}-{candidate}.osm.pbf"
        extract_result = extract_osm(
            pbf_path=source_pbf, polygon_geojson=polygon, output_path=output_path
        )
    except (OsmFetchError, OsmExtractError, FileNotFoundError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Wrote {extract_result.output_path} (sha256={extract_result.sha256})")


@network_app.command("build")
def network_build(
    city: str = typer.Option(..., "--city"),
    osm_pbf: Path = typer.Option(..., "--osm-pbf"),
    type_files: str | None = typer.Option(
        None,
        "--type-files",
        help="Comma-separated list of SUMO typemap files for netconvert --type-files.",
    ),
    extra: list[str] = typer.Option(
        [],
        "--extra",
        help="Extra netconvert option, appended last; repeatable.",
    ),
) -> None:
    """Run `netconvert` against `--osm-pbf`, writing `cities/<city>/network/<city>.net.xml`,
    then validate the result.
    """
    from arteria.network.build import NetconvertError, build_network

    city_dir = Path.cwd() / "cities" / city
    output_path = city_dir / "network" / f"{city}.net.xml"
    type_file_paths = [Path(p.strip()) for p in type_files.split(",")] if type_files else []

    try:
        result = build_network(
            osm_pbf_path=osm_pbf,
            output_path=output_path,
            type_files=type_file_paths,
            extra_options=extra,
        )
    except (NetconvertError, FileNotFoundError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Wrote {result.net_xml_path}")
    typer.echo(
        f"Validation: {result.validation_errors} error(s), "
        f"{result.validation_warnings} warning(s)"
    )
    if result.validation_errors > 0:
        typer.echo("Run `arteria network validate` for the full report.")


@network_app.command("validate")
def network_validate(
    city: str = typer.Option(..., "--city"),
    net: Path | None = typer.Option(
        None,
        "--net",
        help="Defaults to cities/<city>/network/<city>.net.xml.",
    ),
) -> None:
    """Validate a built network with `arteria.network.validate.validate_network`
    and print every finding."""
    from arteria.network.validate import validate_network

    city_dir = Path.cwd() / "cities" / city
    net_path = net or city_dir / "network" / f"{city}.net.xml"

    try:
        report = validate_network(net_path)
    except (FileNotFoundError, OSError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    for finding in report.findings:
        typer.echo(f"[{finding.severity}] {finding.check}: {finding.message}")

    if report.has_blocking_issues:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
