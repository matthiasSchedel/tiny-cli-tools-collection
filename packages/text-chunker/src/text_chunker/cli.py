from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import click

from .chunker import chunk_text


def _read_input(file: Optional[Path]) -> str:
    if file:
        return file.read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise click.ClickException("Provide a file or pipe text via stdin.")


@click.command()
@click.argument("file", required=False, type=click.Path(path_type=Path))
@click.option("--max-tokens", default=1000, show_default=True, type=int)
@click.option("--max-chars", default=None, type=int)
@click.option("--overlap", default=0, show_default=True, type=int)
@click.option(
    "--strategy",
    type=click.Choice(["character", "token", "sentence", "paragraph", "semantic"]),
    default="sentence",
    show_default=True,
)
@click.option(
    "--encoding",
    type=click.Choice(["cl100k_base", "p50k_base", "r50k_base"]),
    default="cl100k_base",
    show_default=True,
)
@click.option("--metadata/--no-metadata", default=True, show_default=True)
@click.option(
    "--format", "output_format", type=click.Choice(["json", "jsonl", "text"]), default="json"
)
def main(
    file: Optional[Path],
    max_tokens: int,
    max_chars: Optional[int],
    overlap: int,
    strategy: str,
    encoding: str,
    metadata: bool,
    output_format: str,
) -> None:
    """Split text for LLM processing."""
    try:
        source = _read_input(file)
        payload = chunk_text(
            source,
            max_tokens=max_tokens,
            max_chars=max_chars,
            overlap=overlap,
            strategy=strategy,
            encoding=encoding,
            include_metadata=metadata,
        )
        if output_format == "json":
            click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
            return
        if output_format == "jsonl":
            for chunk in payload["chunks"]:
                click.echo(json.dumps(chunk, ensure_ascii=False))
            return
        for chunk in payload["chunks"]:
            click.echo(
                f"# chunk={chunk['index']} tokens={chunk['tokens']} chars={chunk['characters']}"
            )
            click.echo(chunk["text"])
            click.echo("---")
    except click.ClickException:
        raise
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    main()
