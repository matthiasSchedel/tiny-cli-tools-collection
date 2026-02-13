from json_patcher.merger import merge_documents


def test_smart_merge_arrays_unique() -> None:
    left = {"items": [1, 2]}
    right = {"items": [2, 3]}
    merged = merge_documents(left, right, strategy="smart", array_strategy="unique")
    assert merged["items"] == [1, 2, 3]
