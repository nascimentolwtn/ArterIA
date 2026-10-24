"""The `arteria` CLI (ADR 0002): one Typer entry point into `arteria/`."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import typer

from arteria import __version__

app = typer.Typer(help="ArterIA: AI-assisted decision-support tool for street-network planning.")


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


if __name__ == "__main__":
    app()
