from json_patcher.query import query_document


def test_query_document() -> None:
    payload = {"users": [{"active": True}, {"active": False}]}
    matches = query_document(payload, "$.users[*].active")
    assert matches == [True, False]
