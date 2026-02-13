from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Mapping, Optional


def _constant_eq(left: str, right: str) -> bool:
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))


def validate_signature(
    provider: str | None,
    secret: str | None,
    headers: Mapping[str, str],
    body: bytes,
) -> Optional[bool]:
    if not provider:
        return None
    if not secret:
        return False

    provider_key = provider.lower()
    lower_headers = {k.lower(): v for k, v in headers.items()}

    if provider_key == "github":
        header = lower_headers.get("x-hub-signature-256", "")
        expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return _constant_eq(header, expected)

    if provider_key == "shopify":
        header = lower_headers.get("x-shopify-hmac-sha256", "")
        expected = base64.b64encode(
            hmac.new(secret.encode(), body, hashlib.sha256).digest()
        ).decode()
        return _constant_eq(header, expected)

    if provider_key == "stripe":
        signature = lower_headers.get("stripe-signature", "")
        parts = dict(part.split("=", 1) for part in signature.split(",") if "=" in part)
        timestamp = parts.get("t")
        v1 = parts.get("v1")
        if not timestamp or not v1:
            return False
        payload = f"{timestamp}.{body.decode('utf-8', errors='ignore')}".encode()
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return _constant_eq(v1, expected)

    # Generic fallback: X-Signature-256 header with hex SHA-256 HMAC
    header = lower_headers.get("x-signature-256", "")
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return _constant_eq(header, expected)
