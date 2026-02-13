from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable, List, Sequence

import click
import yaml
from jsonschema import Draft7Validator

from .inferrer import infer_schema


def _load_json_items_from_text(text: str) -> List[object]:
    text = text.strip()
    if not text:
        return []
    if "\n" in text and not text.startswith("["):
        items = []
        for line in text.splitlines():
            line = line.strip()
            if line:
                items.append(json.loads(line))
        return items
    parsed = json.loads(text)
    if isinstance(parsed, list):
        return parsed
    return [parsed]


def _load_items(files: Sequence[Path], from_stdin: bool) -> Iterable[object]:
    for file in files:
        yield from _load_json_items_from_text(file.read_text(encoding="utf-8"))
    if from_stdin and not sys.stdin.isatty():
        yield from _load_json_items_from_text(sys.stdin.read())


@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option("--samples", default=None, type=int)
@click.option("--confidence", default=0.8, show_default=True, type=float)
@click.option("--strict/--lenient", default=False, show_default=True)
@click.option("--format", "output_format", type=click.Choice(["json", "yaml"]), default="json")
@click.option("--title", default=None)
@click.option("--description", default=None)
@click.option("--stdin/--no-stdin", "read_stdin", default=False, show_default=True)
def main(
    files: Sequence[Path],
    samples: int | None,
    confidence: float,
    strict: bool,
    output_format: str,
    title: str | None,
    description: str | None,
    read_stdin: bool,
) -> None:
    """Infer JSON Schema from input samples."""
    if not files and not read_stdin and sys.stdin.isatty():
        raise click.ClickException("Provide JSON files or pass --stdin.")
    try:
        all_items = list(_load_items(files, from_stdin=read_stdin or not files))
        if samples is not None:
            all_items = all_items[:samples]
        schema = infer_schema(
            all_items,
            confidence=confidence,
            strict=strict,
            title=title,
            description=description,
        )
        # Ensure schema itself is valid Draft 7.
        Draft7Validator.check_schema(schema)
        if output_format == "yaml":
            click.echo(yaml.safe_dump(schema, sort_keys=False))
        else:
            click.echo(json.dumps(schema, indent=2, ensure_ascii=False))
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    main()
