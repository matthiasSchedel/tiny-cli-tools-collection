from schema_guesser.inferrer import infer_schema


def test_infer_basic_object_schema() -> None:
    samples = [{"email": "a@example.com", "age": 20}, {"email": "b@example.com", "age": 30}]
    schema = infer_schema(samples)
    assert schema["type"] == "object"
    assert "email" in schema["properties"]
    assert schema["properties"]["email"]["format"] == "email"
