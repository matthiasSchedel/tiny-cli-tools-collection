from click.testing import CliRunner
from rate_limiter.cli import main


def test_cli_requires_command() -> None:
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code != 0
