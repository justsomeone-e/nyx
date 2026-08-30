"""Target-neutral Nyx type identities used by the structured typed HIR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple


INTEGER_TYPE_NAMES = frozenset(("int", "i8", "i16", "i32", "i64", "u8", "u16", "u32", "u64", "uintptr"))


@dataclass(frozen=True, slots=True)
class IRType:
    name: str
    arguments: Tuple["IRType", ...] = ()
    optional: bool = False
    pointer: bool = False
    parameter_types: Tuple["IRType", ...] = ()
    return_type: Optional["IRType"] = None

    @property
    def is_function(self) -> bool:
        return self.return_type is not None

    @property
    def is_numeric(self) -> bool:
        return self.name in INTEGER_TYPE_NAMES | {"float", "f32", "f64"} and not self.optional and not self.pointer

    @property
    def is_unknown(self) -> bool:
        return self.name == "any"

    def with_optional(self, optional: bool = True) -> "IRType":
        return IRType(
            self.name,
            self.arguments,
            optional,
            self.pointer,
            self.parameter_types,
            self.return_type,
        )

    def canonical(self) -> str:
        if self.is_function:
            params = ",".join(item.canonical() for item in self.parameter_types)
            rendered = f"fn({params})->{self.return_type.canonical()}"
        else:
            rendered = self.name
            if self.arguments:
                rendered += "<" + ",".join(item.canonical() for item in self.arguments) + ">"
            if self.pointer:
                rendered = "*" + rendered
        if self.optional:
            rendered += "?"
        return rendered

    def __str__(self) -> str:
        return self.canonical()


ANY = IRType("any")
VOID = IRType("void")
NULL = IRType("null", optional=True)
BOOL = IRType("bool")
INT = IRType("int")
FLOAT = IRType("float")
STRING = IRType("string")


def array_of(element_type: IRType) -> IRType:
    return IRType("Array", (element_type,))


def task_of(result_type: IRType) -> IRType:
    return IRType("Task", (result_type,))


def function_type(parameters: Iterable[IRType], result: IRType) -> IRType:
    return IRType("fn", parameter_types=tuple(parameters), return_type=result)


def from_type_node(type_node: object, default: IRType = ANY) -> IRType:
    if type_node is None:
        return default
    if isinstance(type_node, IRType):
        return type_node

    name = str(getattr(type_node, "name", type_node))
    generic_args = tuple(from_type_node(item) for item in getattr(type_node, "generic_args", ()) or ())
    optional = bool(getattr(type_node, "is_optional", False))
    pointer = bool(getattr(type_node, "is_pointer", False))
    if getattr(type_node, "is_fn_type", False):
        params = tuple(from_type_node(item) for item in getattr(type_node, "param_types", ()) or ())
        result = from_type_node(getattr(type_node, "return_type", None), VOID)
        return IRType("fn", optional=optional, parameter_types=params, return_type=result)
    return IRType(name, generic_args, optional, pointer)


def from_inferred_name(name: object, default: IRType = ANY) -> IRType:
    if isinstance(name, IRType):
        return name
    if not name:
        return default
    text = str(name).strip()
    optional = text.endswith("?")
    if optional:
        text = text[:-1]
    pointer = text.startswith("*")
    if pointer:
        text = text[1:]
    for generic_name in ("Array", "Task", "Option"):
        prefix = generic_name + "<"
        if text.startswith(prefix) and text.endswith(">"):
            return IRType(
                generic_name,
                (from_inferred_name(text[len(prefix):-1]),),
                optional,
                pointer,
            )
    if text.startswith("Buffer<") and text.endswith(">"):
        body = text[7:-1]
        if "," in body:
            element, capacity = body.rsplit(",", 1)
            return IRType(
                "Buffer",
                (from_inferred_name(element), IRType(capacity.strip())),
                optional,
                pointer,
            )
    return IRType(text, optional=optional, pointer=pointer)


def compatible(expected: IRType, actual: IRType) -> bool:
    if expected.is_unknown or actual.is_unknown:
        return True
    if actual.name == "null":
        return expected.optional or expected.name in ("Option", "Result")
    if expected == actual:
        return True
    if expected.optional and expected.with_optional(False) == actual.with_optional(False):
        return True
    if expected.name in INTEGER_TYPE_NAMES and actual.name in INTEGER_TYPE_NAMES:
        return True
    if expected.name == "float" and actual.name == "int":
        return True
    if (
        expected.name == "Buffer" and len(expected.arguments) == 2
        and actual.name == "Array" and len(actual.arguments) == 1
    ):
        return compatible(expected.arguments[0], actual.arguments[0])
    if expected.pointer and actual.pointer:
        return True
    if expected.name == actual.name and expected.arguments and actual.arguments:
        return len(expected.arguments) == len(actual.arguments) and all(
            compatible(left, right) for left, right in zip(expected.arguments, actual.arguments)
        )
    return False
