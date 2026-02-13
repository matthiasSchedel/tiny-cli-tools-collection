from __future__ import annotations

from pathlib import Path
from typing import Optional

import click
import uvicorn

from .server import create_app, load_spec


@click.command()
@click.argument("spec_file", type=click.Path(exists=True, path_type=Path))
@click.option("--port", default=8000, show_default=True, type=int)
@click.option("--host", default="127.0.0.1", show_default=True, type=str)
@click.option("--log/--no-log", "log_requests", default=True, show_default=True)
@click.option("--log-file", type=click.Path(path_type=Path), default=None)
@click.option("--replay/--no-replay", default=False, show_default=True)
@click.option("--delay", "delay_ms", default=0, show_default=True, type=int)
@click.option("--cors/--no-cors", default=True, show_default=True)
@click.option("--validate/--no-validate", "validate_requests", default=True, show_default=True)
def main(
    spec_file: Path,
    port: int,
    host: str,
    log_requests: bool,
    log_file: Optional[Path],
    replay: bool,
    delay_ms: int,
    cors: bool,
    validate_requests: bool,
) -> None:
    """Run an OpenAPI-based mock server."""
    try:
        spec = load_spec(spec_file)
        app = create_app(
            spec,
            log_requests=log_requests,
            log_file=log_file,
            replay=replay,
            delay_ms=delay_ms,
            cors=cors,
            validate_requests=validate_requests,
        )
        uvicorn.run(app, host=host, port=port)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    main()
