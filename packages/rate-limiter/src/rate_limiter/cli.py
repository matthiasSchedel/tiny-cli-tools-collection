from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import Sequence

import click

from .bucket import TokenBucket
from .state import default_state, from_payload, locked_state_file, to_payload


def _run_command(command: Sequence[str]) -> int:
    proc = subprocess.run(command)
    return proc.returncode


@click.command(context_settings={"ignore_unknown_options": True})
@click.option("--rpm", default=60, show_default=True, type=int)
@click.option("--rps", default=None, type=float)
@click.option("--burst", default=1, show_default=True, type=int)
@click.option("--state-file", type=click.Path(path_type=Path), default=None)
@click.option("--wait/--no-wait", default=True, show_default=True)
@click.option("--timeout", default=300, show_default=True, type=int)
@click.option("--key", default="command", show_default=True)
@click.option("--verbose/--quiet", default=False, show_default=True)
@click.argument("command", nargs=-1, type=click.UNPROCESSED, required=True)
def main(
    rpm: int,
    rps: float | None,
    burst: int,
    state_file: Path | None,
    wait: bool,
    timeout: int,
    key: str,
    verbose: bool,
    command: Sequence[str],
) -> None:
    """Rate limit execution of any shell command."""
    refill_rate = rps if rps is not None else rpm / 60.0
    if refill_rate <= 0:
        raise click.ClickException("Refill rate must be > 0.")
    if burst <= 0:
        raise click.ClickException("Burst must be > 0.")

    started = time.time()
    if state_file is None:
        state = default_state(capacity=burst, refill_rate=refill_rate)
        bucket = TokenBucket(state)
        while not bucket.try_consume():
            if not wait:
                raise click.ClickException("Rate limit exceeded.")
            sleep_for = min(0.25, bucket.wait_time())
            if time.time() - started + sleep_for > timeout:
                raise click.ClickException("Timed out waiting for token.")
            time.sleep(max(0.01, sleep_for))
        if verbose:
            click.echo(f"[rate-limiter] executing: {' '.join(command)}", err=True)
        raise SystemExit(_run_command(command))

    with locked_state_file(state_file) as (_, payload):
        raw_state = payload.get(key)
        state = (
            from_payload(raw_state, capacity=burst, refill_rate=refill_rate)
            if raw_state
            else default_state(burst, refill_rate)
        )
        bucket = TokenBucket(state)

        while not bucket.try_consume():
            if not wait:
                raise click.ClickException("Rate limit exceeded.")
            sleep_for = min(0.25, bucket.wait_time())
            if time.time() - started + sleep_for > timeout:
                raise click.ClickException("Timed out waiting for token.")
            time.sleep(max(0.01, sleep_for))
            bucket.refill()

        payload[key] = to_payload(bucket.state)

    if verbose:
        click.echo(f"[rate-limiter] executing: {' '.join(command)}", err=True)
    code = _run_command(command)
    sys.exit(code)


if __name__ == "__main__":
    main()
