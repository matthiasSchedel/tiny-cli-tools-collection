from __future__ import annotations

import json
from pathlib import Path

import click

from .filler import fill_form
from .utils import load_data_file, resolve_config_urls, resolve_input_url
from .validators import validate_config


@click.command()
@click.argument("url")
@click.argument("data_file", type=click.Path(exists=True, path_type=Path))
@click.option("--format", "data_format", type=click.Choice(["json", "yaml"]), default=None)
@click.option("--wait-for", default=None)
@click.option("--screenshot/--no-screenshot", default=False, show_default=True)
@click.option("--submit/--no-submit", "should_submit", default=True, show_default=True)
@click.option("--output", type=click.Path(path_type=Path), default=None)
@click.option(
    "--browser",
    "browser_name",
    type=click.Choice(["chromium", "firefox", "webkit"]),
    default="chromium",
    show_default=True,
)
def main(
    url: str,
    data_file: Path,
    data_format: str | None,
    wait_for: str | None,
    screenshot: bool,
    should_submit: bool,
    output: Path | None,
    browser_name: str,
) -> None:
    """Fill forms from declarative JSON/YAML."""
    try:
        data = load_data_file(data_file, explicit_format=data_format)
        data = resolve_config_urls(data, base_dir=data_file.parent)
        errors = validate_config(data)
        if errors:
            raise click.ClickException("; ".join(errors))
        raw_url = data.get("url")
        effective_url = resolve_input_url(
            raw_url if isinstance(raw_url, str) else url, base_dir=data_file.parent
        )
        result = fill_form(
            url=effective_url,
            data=data,
            browser_name=browser_name,
            wait_for=wait_for,
            should_submit=should_submit,
            screenshot=screenshot,
        )
        rendered = json.dumps(result, indent=2, ensure_ascii=False)
        if output:
            output.write_text(rendered, encoding="utf-8")
        else:
            click.echo(rendered)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    main()
