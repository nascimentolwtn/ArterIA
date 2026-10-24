from typer.testing import CliRunner

from arteria.cli import app

runner = CliRunner()


def test_doctor_runs_and_reports_python_and_sumo() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Python:" in result.stdout
    assert "SUMO_HOME:" in result.stdout
