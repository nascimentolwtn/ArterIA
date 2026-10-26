"""Cross-platform task runner (ADR 0002). Remote Claude sessions only ever run
`nox -s lint tests` (roadmap R1); `smoke` needs a real `sumo`/`netconvert`
binary and stays desktop-only.
"""

import pathlib
import shutil
import tempfile
import xml.etree.ElementTree as ET

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
    """Real toy-network SUMO run: netconvert + sumo, desktop-only (roadmap P0.5)."""
    if not shutil.which("sumo") or not shutil.which("netconvert"):
        session.skip("desktop-only: no `sumo`/`netconvert` on PATH (expected in a remote session)")
    src = pathlib.Path("tests/fixtures/smoke").resolve()
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp)
        for f in src.iterdir():
            shutil.copy(f, work)
        with session.chdir(work):
            session.run(
                "netconvert",
                "--node-files=toy.nod.xml",
                "--edge-files=toy.edg.xml",
                "--output-file=toy.net.xml",
                "--no-warnings",
                external=True,
            )
            session.run(
                "sumo",
                "-c",
                "toy.sumocfg",
                "--no-step-log",
                "--tripinfo-output=tripinfo.xml",
                "--error-log=sumo-errors.txt",
                external=True,
            )
        trips = ET.parse(work / "tripinfo.xml").getroot().findall("tripinfo")
        errors = (work / "sumo-errors.txt").read_text().strip()
        if errors:
            session.error(f"sumo reported errors:\n{errors}")
        if len(trips) < 10:
            session.error(f"expected >=10 completed trips, got {len(trips)}")
        session.log(f"smoke OK: {len(trips)} vehicles completed the toy network")
