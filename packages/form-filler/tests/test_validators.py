from form_filler.validators import validate_config


def test_validate_config_requires_fields_or_steps() -> None:
    errors = validate_config({})
    assert errors
