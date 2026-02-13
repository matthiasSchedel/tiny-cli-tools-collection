from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class StoredRequest:
    id: str
    timestamp: str
    method: str
    path: str
    headers: Dict[str, Any]
    body: str
    query_params: Dict[str, Any]
    forwarded_status: Optional[int]
    signature_valid: Optional[bool]


class RelayStorage:
    def __init__(self, storage_path: Path | None, capacity: int) -> None:
        db_path = str(storage_path) if storage_path else ":memory:"
        self.capacity = capacity
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS requests (
              id TEXT PRIMARY KEY,
              timestamp TEXT NOT NULL,
              method TEXT NOT NULL,
              path TEXT NOT NULL,
              headers TEXT NOT NULL,
              body TEXT NOT NULL,
              query_params TEXT NOT NULL,
              forwarded_status INTEGER,
              signature_valid INTEGER
            )
            """
        )
        self.conn.commit()

    def insert(
        self,
        *,
        method: str,
        path: str,
        headers: Dict[str, Any],
        body: str,
        query_params: Dict[str, Any],
        forwarded_status: Optional[int],
        signature_valid: Optional[bool],
    ) -> StoredRequest:
        request_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            """
            INSERT INTO requests (id, timestamp, method, path, headers, body, query_params, forwarded_status, signature_valid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                now,
                method,
                path,
                json.dumps(headers),
                body,
                json.dumps(query_params),
                forwarded_status,
                int(signature_valid) if signature_valid is not None else None,
            ),
        )
        self.conn.commit()
        self._prune()
        return StoredRequest(
            id=request_id,
            timestamp=now,
            method=method,
            path=path,
            headers=headers,
            body=body,
            query_params=query_params,
            forwarded_status=forwarded_status,
            signature_valid=signature_valid,
        )

    def _prune(self) -> None:
        self.conn.execute(
            """
            DELETE FROM requests
            WHERE id IN (
              SELECT id FROM requests
              ORDER BY timestamp DESC
              LIMIT -1 OFFSET ?
            )
            """,
            (self.capacity,),
        )
        self.conn.commit()

    def list(self) -> List[StoredRequest]:
        rows = self.conn.execute(
            """
            SELECT id, timestamp, method, path, headers, body, query_params, forwarded_status, signature_valid
            FROM requests
            ORDER BY timestamp DESC
            """
        ).fetchall()
        return [self._row_to_model(row) for row in rows]

    def get(self, request_id: str) -> Optional[StoredRequest]:
        row = self.conn.execute(
            """
            SELECT id, timestamp, method, path, headers, body, query_params, forwarded_status, signature_valid
            FROM requests
            WHERE id = ?
            """,
            (request_id,),
        ).fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def delete(self, request_id: str) -> bool:
        cur = self.conn.execute("DELETE FROM requests WHERE id = ?", (request_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def _row_to_model(self, row: tuple[Any, ...]) -> StoredRequest:
        return StoredRequest(
            id=row[0],
            timestamp=row[1],
            method=row[2],
            path=row[3],
            headers=json.loads(row[4]),
            body=row[5],
            query_params=json.loads(row[6]),
            forwarded_status=row[7],
            signature_valid=(None if row[8] is None else bool(row[8])),
        )
