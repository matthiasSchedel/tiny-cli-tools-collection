from __future__ import annotations

from pathlib import Path

import click
import uvicorn

from .server import create_app


@click.command()
@click.option("--port", default=8080, show_default=True, type=int)
@click.option("--forward", "forward_url", default=None)
@click.option("--storage", type=click.Path(path_type=Path), default=None)
@click.option("--ui-port", default=8080, show_default=True, type=int)
@click.option("--validate-signature", "signature_provider", default=None)
@click.option("--secret", default=None)
@click.option("--capacity", default=1000, show_default=True, type=int)
def main(
    port: int,
    forward_url: str | None,
    storage: Path | None,
    ui_port: int,
    signature_provider: str | None,
    secret: str | None,
    capacity: int,
) -> None:
    """Run a local webhook receiver with request inspection endpoints."""
    # A single FastAPI app serves receiver + UI.
    effective_port = ui_port if ui_port != 8080 and port == 8080 else port
    try:
        app = create_app(
            forward_url=forward_url,
            storage_path=storage,
            signature_provider=signature_provider,
            secret=secret,
            capacity=capacity,
        )
        uvicorn.run(app, host="127.0.0.1", port=effective_port)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    main()
