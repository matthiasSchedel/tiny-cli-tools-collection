from schema_guesser.patterns import detect_string_format


def test_detect_email() -> None:
    assert detect_string_format("user@example.com") == "email"
