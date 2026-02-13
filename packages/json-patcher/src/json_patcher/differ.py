from __future__ import annotations

from typing import Any, List

import jsonpatch


def diff_documents(old: Any, new: Any) -> List[dict]:
    return jsonpatch.make_patch(old, new).patch
