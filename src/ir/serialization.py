"""Canonical HIR serialization used by caches, snapshots, and plugins."""

from dataclasses import fields, is_dataclass
from hashlib import sha256
import json
from typing import Any


def to_data(value: Any) -> Any:
    if is_dataclass(value):
        result = {"node": type(value).__name__}
        for item in fields(value):
            result[item.name] = to_data(getattr(value, item.name))
        return result
    if isinstance(value, tuple):
        return [to_data(item) for item in value]
    if isinstance(value, list):
        return [to_data(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_data(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"HIR value is not canonically serializable: {type(value).__name__}")


def to_json(value: Any, *, indent: int | None = None) -> str:
    return json.dumps(
        to_data(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":") if indent is None else None,
        indent=indent,
    )


def fingerprint(value: Any) -> str:
    return sha256(to_json(value).encode("utf-8")).hexdigest()
