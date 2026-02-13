from __future__ import annotations

from pathlib import Path

import click

from .utils import convert_with_pandoc, detect_format, expand_batch


def _output_path_for(input_path: Path, target_format: str, explicit_output: Path | None) -> Path:
    if explicit_output:
        return explicit_output
    return input_path.with_suffix(f".{target_format}")


@click.command()
@click.argument("input", required=False, type=click.Path(path_type=Path))
@click.argument("output", required=False, type=click.Path(path_type=Path))
@click.option(
    "--from", "from_format", type=click.Choice(["md", "html", "rst", "docx", "odt"]), default=None
)
@click.option(
    "--to", "to_format", type=click.Choice(["md", "html", "pdf", "docx", "odt"]), required=True
)
@click.option("--template", type=click.Path(path_type=Path), default=None)
@click.option("--css", type=click.Path(path_type=Path), default=None)
@click.option("--metadata", type=click.Path(path_type=Path), default=None)
@click.option("--toc/--no-toc", default=False, show_default=True)
@click.option("--batch", "batch_pattern", default=None)
def main(
    input: Path | None,
    output: Path | None,
    from_format: str | None,
    to_format: str,
    template: Path | None,
    css: Path | None,
    metadata: Path | None,
    toc: bool,
    batch_pattern: str | None,
) -> None:
    """Convert documents between common formats."""
    try:
        if batch_pattern:
            files = list(expand_batch(batch_pattern))
            if not files:
                raise click.ClickException(f"No files matched pattern: {batch_pattern}")
            for path in files:
                src_format = from_format or detect_format(path)
                out = path.with_suffix(f".{to_format}")
                convert_with_pandoc(
                    path,
                    out,
                    from_format=src_format,
                    to_format=to_format,
                    toc=toc,
                    template=template,
                    css=css,
                    metadata=metadata,
                )
                click.echo(str(out))
            return

        if not input:
            raise click.ClickException("INPUT is required unless --batch is used.")
        src_format = from_format or detect_format(input)
        out = _output_path_for(input, to_format, output)
        convert_with_pandoc(
            input,
            out,
            from_format=src_format,
            to_format=to_format,
            toc=toc,
            template=template,
            css=css,
            metadata=metadata,
        )
        click.echo(str(out))
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    main()
