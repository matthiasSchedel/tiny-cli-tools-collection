from webhook_relay.storage import RelayStorage


def test_storage_insert_and_get(tmp_path) -> None:
    storage = RelayStorage(tmp_path / "relay.db", capacity=10)
    saved = storage.insert(
        method="POST",
        path="/hook",
        headers={"content-type": "application/json"},
        body='{"ok":true}',
        query_params={},
        forwarded_status=None,
        signature_valid=True,
    )
    loaded = storage.get(saved.id)
    assert loaded is not None
    assert loaded.path == "/hook"
