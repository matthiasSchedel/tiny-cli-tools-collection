from __future__ import annotations

import random
import uuid
from typing import Any, Dict

from faker import Faker

fake = Faker()


def _from_name(name: str) -> Any:
    key = name.lower()
    if "email" in key:
        return fake.email()
    if "phone" in key:
        return fake.phone_number()
    if "uuid" in key or key.endswith("_id"):
        return str(uuid.uuid4())
    if "date" in key and "time" not in key:
        return fake.date()
    if "time" in key:
        return fake.iso8601()
    if "url" in key or "uri" in key:
        return fake.url()
    if "name" in key:
        return fake.name()
    return fake.word()


def generate_from_schema(schema: Dict[str, Any], field_name: str = "") -> Any:
    if not schema:
        return {}
    if "example" in schema:
        return schema["example"]
    if "enum" in schema and schema["enum"]:
        return random.choice(schema["enum"])

    schema_type = schema.get("type")
    schema_format = schema.get("format")

    if schema_type == "object":
        props = schema.get("properties", {})
        return {key: generate_from_schema(value, key) for key, value in props.items()}
    if schema_type == "array":
        item_schema = schema.get("items", {"type": "string"})
        min_items = int(schema.get("minItems", 1))
        max_items = int(schema.get("maxItems", 3))
        size = random.randint(min_items, max(min_items, max_items))
        return [generate_from_schema(item_schema, field_name) for _ in range(size)]
    if schema_type == "string":
        if schema_format == "email":
            return fake.email()
        if schema_format in {"date-time", "datetime"}:
            return fake.iso8601()
        if schema_format == "date":
            return fake.date()
        if schema_format == "uuid":
            return str(uuid.uuid4())
        return _from_name(field_name)
    if schema_type == "integer":
        return random.randint(int(schema.get("minimum", 0)), int(schema.get("maximum", 1000)))
    if schema_type == "number":
        low = float(schema.get("minimum", 0))
        high = float(schema.get("maximum", 1000))
        return round(random.uniform(low, high), 2)
    if schema_type == "boolean":
        return bool(random.getrandbits(1))
    return _from_name(field_name or "value")
