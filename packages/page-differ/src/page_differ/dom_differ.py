from __future__ import annotations

from typing import Dict, List

from bs4 import BeautifulSoup, Tag


def _collect_nodes(soup: BeautifulSoup) -> Dict[str, str]:
    collected: Dict[str, str] = {}

    def visit(node: Tag, path: str) -> None:
        children = [c for c in node.children if isinstance(c, Tag)]
        index_map: Dict[str, int] = {}
        for child in children:
            name = child.name
            index_map[name] = index_map.get(name, 0) + 1
            child_path = f"{path}/{name}[{index_map[name]}]"
            text_preview = child.get_text(" ", strip=True)[:200]
            collected[child_path] = text_preview
            visit(child, child_path)

    root = soup.body or soup
    if isinstance(root, Tag):
        visit(root, "/root")
    return collected


def diff_dom(before: BeautifulSoup, after: BeautifulSoup) -> Dict[str, List[dict]]:
    before_map = _collect_nodes(before)
    after_map = _collect_nodes(after)

    before_keys = set(before_map.keys())
    after_keys = set(after_map.keys())

    added = [{"selector": key, "html": after_map[key]} for key in sorted(after_keys - before_keys)]
    removed = [
        {"selector": key, "html": before_map[key]} for key in sorted(before_keys - after_keys)
    ]
    modified = []
    for key in sorted(before_keys & after_keys):
        if before_map[key] != after_map[key]:
            modified.append({"selector": key, "before": before_map[key], "after": after_map[key]})
    return {"added": added, "removed": removed, "modified": modified}
