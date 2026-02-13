from json_patcher.patcher import apply_patch


def test_apply_patch_replace() -> None:
    result, validation = apply_patch({"x": 1}, [{"op": "replace", "path": "/x", "value": 2}])
    assert result["x"] == 2
    assert validation["valid"] is True
