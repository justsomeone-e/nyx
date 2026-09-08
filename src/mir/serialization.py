"""Canonical serialization and fingerprints for experimental MIR."""

from __future__ import annotations

from dataclasses import MISSING, fields, is_dataclass
from hashlib import sha256
import inspect
import json
from typing import Any

from . import model
from .model import MIRModule
from .types import MIRType


_NODE_TYPES = {
    name: value
    for module in (model,)
    for name, value in inspect.getmembers(module, inspect.isclass)
    if value.__module__ == module.__name__
}
_NODE_TYPES["MIRType"] = MIRType


def to_data(value: Any) -> Any:
    if is_dataclass(value):
        result = {"node": type(value).__name__}
        for item in fields(value):
            result[item.name] = to_data(getattr(value, item.name))
        return result
    if isinstance(value, (tuple, list)):
        return [to_data(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): to_data(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"MIR value is not canonically serializable: {type(value).__name__}")


def from_data(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(from_data(item) for item in value)
    if isinstance(value, dict):
        node_name = value.get("node")
        if node_name is None:
            return {key: from_data(item) for key, item in value.items()}
        node_type = _NODE_TYPES.get(node_name)
        if node_type is None:
            raise ValueError(f"Unknown MIR node type: {node_name}")
        expected_fields = {item.name for item in fields(node_type)}
        supplied_fields = set(value) - {"node"}
        unknown_fields = supplied_fields - expected_fields
        missing_fields = {
            item.name
            for item in fields(node_type)
            if item.name not in supplied_fields
            and item.default is MISSING
            and item.default_factory is MISSING
        }
        if unknown_fields:
            raise ValueError(f"Unknown fields for {node_name}: {sorted(unknown_fields)}")
        if missing_fields:
            raise ValueError(f"Missing fields for {node_name}: {sorted(missing_fields)}")
        arguments = {
            key: from_data(item)
            for key, item in value.items()
            if key != "node"
        }
        return node_type(**arguments)
    return value


def to_json(value: Any, *, indent: int | None = None) -> str:
    return json.dumps(
        to_data(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":") if indent is None else None,
        indent=indent,
    )


def from_json(source: str) -> MIRModule:
    value = from_data(json.loads(source))
    if not isinstance(value, MIRModule):
        raise ValueError("Serialized MIR root must be MIRModule")
    return value


def fingerprint(value: Any) -> str:
    return sha256(to_json(value).encode("utf-8")).hexdigest()
