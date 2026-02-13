from __future__ import annotations

from typing import Any, List

from jsonpath_ng.ext import parse


def query_document(document: Any, expression: str) -> List[Any]:
    jsonpath = parse(expression)
    return [match.value for match in jsonpath.find(document)]
