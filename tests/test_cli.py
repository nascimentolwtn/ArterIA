import shutil
from pathlib import Path

from typer.testing import CliRunner

from arteria.cli import app

runner = CliRunner()
REPO_ROOT = Path(__file__).parent.parent


def test_doctor_runs_and_reports_python_and_sumo() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Python:" in result.stdout
    assert "SUMO_HOME:" in result.stdout


def test_city_new_scaffolds_and_validates(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cities").mkdir()
    shutil.copytree(REPO_ROOT / "cities" / "_template", tmp_path / "cities" / "_template")

    result = runner.invoke(app, ["city", "new", "testcity"])

    assert result.exit_code == 0
    assert (tmp_path / "cities" / "testcity" / "city.yaml").exists()


def test_city_new_refuses_to_overwrite(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cities" / "existing").mkdir(parents=True)

    result = runner.invoke(app, ["city", "new", "existing"])

    assert result.exit_code == 1
