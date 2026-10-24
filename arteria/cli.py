"""The `arteria` CLI (ADR 0002): one Typer entry point into `arteria/`."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import typer

from arteria import __version__
from arteria.scaffold import CityAlreadyExistsError, create_city

app = typer.Typer(help="ArterIA: AI-assisted decision-support tool for street-network planning.")
city_app = typer.Typer(help="City scaffolding (ADR 0002).")
app.add_typer(city_app, name="city")


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
    except CityAlreadyExistsError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Created {city_dir}/ — fill in crs, sumo_version, and the bounding polygon.")


if __name__ == "__main__":
    app()
