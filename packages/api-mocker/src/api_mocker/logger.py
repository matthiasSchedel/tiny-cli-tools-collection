from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class RequestLogEntry:
    id: int
    timestamp: str
    method: str
    path: str
    headers: Dict[str, Any]
    body: Any
    response_status: int
    response_body: Any


class RequestLogger:
    def __init__(self, log_file: Optional[Path] = None) -> None:
        self._lock = threading.Lock()
        self._entries: List[RequestLogEntry] = []
        self._log_file = log_file

    def add(
        self,
        method: str,
        path: str,
        headers: Dict[str, Any],
        body: Any,
        response_status: int,
        response_body: Any,
    ) -> RequestLogEntry:
        with self._lock:
            entry = RequestLogEntry(
                id=len(self._entries),
                timestamp=datetime.now(timezone.utc).isoformat(),
                method=method,
                path=path,
                headers=headers,
                body=body,
                response_status=response_status,
                response_body=response_body,
            )
            self._entries.append(entry)
            if self._log_file:
                self._log_file.parent.mkdir(parents=True, exist_ok=True)
                with self._log_file.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
            return entry

    def list_entries(self) -> List[RequestLogEntry]:
        with self._lock:
            return list(self._entries)

    def get(self, entry_id: int) -> Optional[RequestLogEntry]:
        with self._lock:
            if 0 <= entry_id < len(self._entries):
                return self._entries[entry_id]
            return None
