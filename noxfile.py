"""Cross-platform task runner (ADR 0002). Remote Claude sessions only ever run
`nox -s lint tests` (roadmap R1); `smoke` needs a real `sumo`/`netconvert`
binary and stays desktop-only.
"""

import shutil

import nox

nox.options.sessions = ["lint", "tests"]


@nox.session
def lint(session: nox.Session) -> None:
    session.install("ruff", "mypy", "types-PyYAML", "pydantic")
    session.run("ruff", "check", ".")
    session.run("mypy", "arteria")


@nox.session
def tests(session: nox.Session) -> None:
    session.install("-e", ".[dev,geo]")
    session.run("pytest")


@nox.session
def smoke(session: nox.Session) -> None:
    """Real toy-network SUMO run — desktop-only (roadmap P0.5)."""
    if not shutil.which("sumo"):
        session.skip("desktop-only: no `sumo` binary on PATH (expected in a remote session)")
    session.install("-e", ".[dev]")
    session.log("TODO: real toy-network smoke run lands with the Phase 2 network build.")
