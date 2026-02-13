from __future__ import annotations

from pathlib import Path
from typing import Dict

from PIL import Image, ImageChops


def _screenshot(source: str, destination: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Playwright is required for visual mode.") from exc

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 2000})
        if Path(source).exists():
            page.goto(Path(source).resolve().as_uri(), wait_until="networkidle")
        else:
            page.goto(source, wait_until="networkidle")
        page.screenshot(path=str(destination), full_page=True)
        browser.close()


def diff_visual(
    source_a: str, source_b: str, threshold: float, save_images: bool
) -> Dict[str, object]:
    before_img = Path("before.png")
    after_img = Path("after.png")
    diff_img = Path("diff.png")

    _screenshot(source_a, before_img)
    _screenshot(source_b, after_img)

    left = Image.open(before_img).convert("RGB")
    right = Image.open(after_img).convert("RGB")
    if left.size != right.size:
        right = right.resize(left.size)

    diff = ImageChops.difference(left, right)
    bbox = diff.getbbox()
    total = left.size[0] * left.size[1]
    changed = sum(1 for pix in diff.getdata() if pix != (0, 0, 0))
    ratio = changed / total if total else 0.0

    if save_images:
        diff.save(diff_img)
    else:
        before_img.unlink(missing_ok=True)
        after_img.unlink(missing_ok=True)

    return {
        "diff_percentage": round(ratio * 100, 4),
        "changed_regions": (
            []
            if bbox is None
            else [
                {
                    "x": bbox[0],
                    "y": bbox[1],
                    "width": bbox[2] - bbox[0],
                    "height": bbox[3] - bbox[1],
                }
            ]
        ),
        "significant": ratio >= threshold,
        "artifacts": {
            "before": str(before_img),
            "after": str(after_img),
            "diff": str(diff_img) if save_images else None,
        },
    }
