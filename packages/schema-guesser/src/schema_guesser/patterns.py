from __future__ import annotations

import re
import uuid
from datetime import datetime
from urllib.parse import urlparse

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[1-9]\d{6,14}$")
IPV4_RE = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")


def detect_string_format(value: str) -> str | None:
    if EMAIL_RE.match(value):
        return "email"
    if value.startswith(("http://", "https://")):
        parsed = urlparse(value)
        if parsed.scheme and parsed.netloc:
            return "uri"
    try:
        uuid.UUID(value)
        return "uuid"
    except Exception:
        pass
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return "date-time" if "T" in value else "date"
    except Exception:
        pass
    if PHONE_RE.match(value):
        return "phone"
    if IPV4_RE.match(value):
        return "ipv4"
    return None
