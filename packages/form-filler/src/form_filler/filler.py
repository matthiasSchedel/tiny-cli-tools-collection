from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

from playwright.sync_api import Page, sync_playwright


def _fill_field(page: Page, field: Dict[str, Any]) -> None:
    selector = field["selector"]
    value = field.get("value")
    field_type = field.get("type", "text")
    if field_type in {
        "text",
        "email",
        "tel",
        "number",
        "url",
        "textarea",
        "date",
        "datetime-local",
    }:
        page.fill(selector, str(value))
        return
    if field_type == "select":
        if isinstance(value, list):
            page.select_option(selector, [str(v) for v in value])
        else:
            page.select_option(selector, str(value))
        return
    if field_type == "checkbox":
        checked = bool(value)
        if checked:
            page.check(selector)
        else:
            page.uncheck(selector)
        return
    if field_type == "radio":
        page.check(selector)
        return
    if field_type == "file":
        page.set_input_files(selector, str(value))
        return
    page.fill(selector, str(value))


def _run_step(page: Page, step: Dict[str, Any], should_submit: bool) -> int:
    if "url" in step:
        page.goto(step["url"], wait_until="domcontentloaded")
    if step.get("wait_for"):
        page.wait_for_selector(step["wait_for"], timeout=10000)
    fields = step.get("fields", [])
    for field in fields:
        _fill_field(page, field)
    if should_submit and step.get("submit"):
        page.click(step["submit"])
    if step.get("wait_after_submit"):
        page.wait_for_timeout(int(step["wait_after_submit"]))
    return len(fields)


def fill_form(
    *,
    url: str,
    data: Dict[str, Any],
    browser_name: str,
    wait_for: str | None,
    should_submit: bool,
    screenshot: bool,
) -> Dict[str, Any]:
    started = time.time()
    screenshots = {}
    errors: List[str] = []
    filled_fields = 0
    final_url = url
    with sync_playwright() as p:
        browser_type = getattr(p, browser_name)
        browser = browser_type.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        if wait_for:
            page.wait_for_selector(wait_for, timeout=10000)

        if screenshot:
            before = Path("before.png")
            page.screenshot(path=str(before), full_page=True)
            screenshots["before"] = str(before)

        if "steps" in data:
            for step in data["steps"]:
                filled_fields += _run_step(page, step, should_submit=should_submit)
        else:
            if data.get("wait_for"):
                page.wait_for_selector(data["wait_for"], timeout=10000)
            for field in data.get("fields", []):
                _fill_field(page, field)
                filled_fields += 1
            if should_submit and data.get("submit_button"):
                page.click(data["submit_button"])
            if data.get("wait_after_submit"):
                page.wait_for_timeout(int(data["wait_after_submit"]))

        final_url = page.url
        expected_redirect = data.get("expected_redirect")
        if expected_redirect and not final_url.startswith(expected_redirect):
            errors.append(f"Expected redirect '{expected_redirect}', got '{final_url}'")

        if screenshot:
            after = Path("after.png")
            page.screenshot(path=str(after), full_page=True)
            screenshots["after"] = str(after)

        browser.close()

    duration_ms = int((time.time() - started) * 1000)
    return {
        "status": "success" if not errors else "partial",
        "url": url,
        "filled_fields": filled_fields,
        "submitted": should_submit,
        "final_url": final_url,
        "screenshots": screenshots,
        "duration_ms": duration_ms,
        "errors": errors,
    }
