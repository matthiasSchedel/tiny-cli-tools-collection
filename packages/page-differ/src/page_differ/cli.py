from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import click

from .content_differ import diff_content
from .dom_differ import diff_dom
from .utils import DEFAULT_IGNORE_SELECTORS, load_html, normalize_html
from .visual_differ import diff_visual


@click.command()
@click.argument("url1")
@click.argument("url2")
@click.option("--mode", type=click.Choice(["dom", "content", "visual", "all"]), default="all")
@click.option("--ignore-selectors", default="")
@click.option("--threshold", default=0.01, show_default=True, type=float)
@click.option(
    "--format", "output_format", type=click.Choice(["json", "html", "text"]), default="json"
)
@click.option("--screenshots/--no-screenshots", default=False, show_default=True)
@click.option("--output", type=click.Path(path_type=Path), default=None)
def main(
    url1: str,
    url2: str,
    mode: str,
    ignore_selectors: str,
    threshold: float,
    output_format: str,
    screenshots: bool,
    output: Path | None,
) -> None:
    """Compare two web pages (URLs or local HTML files)."""
    ignore = [
        x.strip() for x in ignore_selectors.split(",") if x.strip()
    ] or DEFAULT_IGNORE_SELECTORS
    try:
        html1, source1 = load_html(url1)
        html2, source2 = load_html(url2)
        soup1 = normalize_html(html1, ignore)
        soup2 = normalize_html(html2, ignore)

        changes: dict = {}
        if mode in {"dom", "all"}:
            changes["dom"] = diff_dom(soup1, soup2)
        if mode in {"content", "all"}:
            changes["content"] = diff_content(soup1, soup2)
        if mode in {"visual", "all"}:
            changes["visual"] = diff_visual(
                url1, url2, threshold=threshold, save_images=screenshots
            )

        score = 0.0
        if "content" in changes:
            score += 1.0 - changes["content"]["text_similarity"]
        if "visual" in changes:
            score += changes["visual"]["diff_percentage"] / 100.0
        if "dom" in changes:
            dom = changes["dom"]
            score += min(
                1.0, (len(dom["added"]) + len(dom["removed"]) + len(dom["modified"])) / 25.0
            )
        score = round(min(1.0, score), 4)

        payload = {
            "url1": source1,
            "url2": source2,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "changes": changes,
            "summary": {"significant_changes": score >= threshold, "change_score": score},
        }

        if output_format == "json":
            rendered = json.dumps(payload, indent=2, ensure_ascii=False)
        elif output_format == "html":
            rendered = (
                "<html><body><pre>"
                + json.dumps(payload, indent=2, ensure_ascii=False)
                + "</pre></body></html>"
            )
        else:
            rendered = (
                f"Change score: {score}\nSignificant: {payload['summary']['significant_changes']}\n"
            )

        if output:
            output.write_text(rendered, encoding="utf-8")
        else:
            click.echo(rendered)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    main()
