from api_mocker.generator import generate_from_schema


def test_generate_object() -> None:
    schema = {
        "type": "object",
        "properties": {"email": {"type": "string", "format": "email"}, "age": {"type": "integer"}},
    }
    payload = generate_from_schema(schema)
    assert "email" in payload
    assert "age" in payload
