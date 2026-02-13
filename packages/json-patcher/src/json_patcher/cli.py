from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click
import yaml

from .differ import diff_documents
from .merger import merge_documents
from .patcher import apply_patch
from .query import query_document


def _load(path: Path) -> Any:
    content = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(content)
    return json.loads(content)


def _dump(value: Any, output_format: str) -> str:
    if output_format == "yaml":
        return yaml.safe_dump(value, sort_keys=False)
    return json.dumps(value, indent=2, ensure_ascii=False)


@click.group()
def main() -> None:
    """Smart JSON patching and merging."""


@main.command("patch")
@click.argument("document", type=click.Path(exists=True, path_type=Path))
@click.option("--patch", "patch_file", type=click.Path(exists=True, path_type=Path), required=True)
@click.option(
    "--validate", "schema_file", type=click.Path(exists=True, path_type=Path), default=None
)
@click.option("--in-place", is_flag=True, default=False)
@click.option("--format", "output_format", type=click.Choice(["json", "yaml"]), default="json")
def patch_cmd(
    document: Path, patch_file: Path, schema_file: Path | None, in_place: bool, output_format: str
) -> None:
    doc = _load(document)
    operations = _load(patch_file)
    schema = _load(schema_file) if schema_file else None
    result, validation = apply_patch(doc, operations, schema=schema)
    payload = {
        "success": validation["valid"],
        "operations_applied": len(operations),
        "result": result,
        "validation": validation,
    }
    if in_place:
        document.write_text(_dump(result, "json"), encoding="utf-8")
    click.echo(_dump(payload, output_format))


@main.command("merge")
@click.argument("left", type=click.Path(exists=True, path_type=Path))
@click.argument("right", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--strategy", type=click.Choice(["replace", "merge", "append", "smart"]), default="smart"
)
@click.option(
    "--array-strategy", type=click.Choice(["replace", "concat", "unique"]), default="unique"
)
@click.option("--format", "output_format", type=click.Choice(["json", "yaml"]), default="json")
def merge_cmd(
    left: Path, right: Path, strategy: str, array_strategy: str, output_format: str
) -> None:
    merged = merge_documents(
        _load(left), _load(right), strategy=strategy, array_strategy=array_strategy
    )
    click.echo(_dump(merged, output_format))


@main.command("diff")
@click.argument("old", type=click.Path(exists=True, path_type=Path))
@click.argument("new", type=click.Path(exists=True, path_type=Path))
@click.option("--format", "output_format", type=click.Choice(["json", "yaml"]), default="json")
def diff_cmd(old: Path, new: Path, output_format: str) -> None:
    patch = diff_documents(_load(old), _load(new))
    click.echo(_dump(patch, output_format))


@main.command("query")
@click.argument("document", type=click.Path(exists=True, path_type=Path))
@click.argument("expression")
@click.option("--format", "output_format", type=click.Choice(["json", "yaml"]), default="json")
def query_cmd(document: Path, expression: str, output_format: str) -> None:
    matches = query_document(_load(document), expression)
    click.echo(_dump(matches, output_format))


if __name__ == "__main__":
    main()
