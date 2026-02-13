import hashlib
import hmac

from webhook_relay.signatures import validate_signature


def test_github_signature_validation() -> None:
    secret = "abc123"
    body = b'{"x":1}'
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    headers = {"X-Hub-Signature-256": f"sha256={digest}"}
    assert validate_signature("github", secret, headers, body) is True
