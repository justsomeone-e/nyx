"""Canonical builtin signatures shared by HIR lowering and verification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .types import ANY, BOOL, INT, STRING, VOID, IRType, array_of, function_type


@dataclass(frozen=True, slots=True)
class BuiltinSignature:
    parameters: Tuple[IRType, ...]
    result: IRType
    min_args: int
    max_args: Optional[int]

    @property
    def type(self) -> IRType:
        return function_type(self.parameters, self.result)


def _exact(parameters: Tuple[IRType, ...], result: IRType) -> BuiltinSignature:
    return BuiltinSignature(parameters, result, len(parameters), len(parameters))


BUILTINS: Dict[str, BuiltinSignature] = {
    "print": BuiltinSignature((), VOID, 0, None),
    "input": BuiltinSignature((STRING,), STRING, 0, 1),
    "to_string": _exact((ANY,), STRING),
    "to_int": _exact((STRING,), INT),
    "contains": _exact((STRING, STRING), BOOL),
    "is_number": _exact((STRING,), BOOL),
    "addr": _exact((ANY,), IRType("uintptr")),
    "peek": _exact((IRType("uintptr"),), IRType("uintptr")),
    "memdump": _exact((IRType("uintptr"), INT), VOID),
    "delay_ms": _exact((INT,), VOID),
    "channel": BuiltinSignature((), IRType("Channel"), 0, 1),
    "Ok": _exact((ANY,), IRType("Result", (ANY, ANY))),
    "Err": _exact((ANY,), IRType("Result", (ANY, ANY))),
    "len": _exact((ANY,), INT),
    "args": _exact((), array_of(STRING)),
}


BUILTIN_TYPES: Dict[str, IRType] = {
    name: signature.type for name, signature in BUILTINS.items()
}


# Private runtime calls used by stdlib wrappers. Keeping the signatures here,
# rather than inferring declarations from target-specific ``#native raw`` text,
# gives every frontend and verifier one target-neutral ABI contract.
INTRINSICS: Dict[str, BuiltinSignature] = {
    "_nyx_bootstrap_read_file": _exact((STRING,), STRING),
    "_nyx_bootstrap_write_file": _exact((STRING, STRING), BOOL),
    "_nyx_bootstrap_file_exists": _exact((STRING,), BOOL),
    "_nyx_bootstrap_remove_file": _exact((STRING,), BOOL),
    "_nyx_process_exit": _exact((INT,), VOID),
    "_nyx_toolchain_compile_cpp": _exact((STRING, STRING), INT),
    "_nyx_toolchain_last_error": _exact((), STRING),
    "_nyx_utf8_from_codepoint": _exact((INT,), STRING),
    "_nyx_math_sin": _exact((IRType("float"),), IRType("float")),
    "_nyx_math_cos": _exact((IRType("float"),), IRType("float")),
    "_nyx_math_tan": _exact((IRType("float"),), IRType("float")),
    "_nyx_math_sqrt": _exact((IRType("float"),), IRType("float")),
    "_nyx_math_pow": _exact((IRType("float"), IRType("float")), IRType("float")),
    "_nyx_math_abs": _exact((IRType("float"),), IRType("float")),
    "_nyx_math_floor": _exact((IRType("float"),), IRType("float")),
    "_nyx_math_ceil": _exact((IRType("float"),), IRType("float")),
    "_nyx_math_round": _exact((IRType("float"),), IRType("float")),
    "_nyx_math_clamp": _exact(
        (IRType("float"), IRType("float"), IRType("float")),
        IRType("float"),
    ),
    "_nyx_time_now_ms": _exact((), INT),
    "_nyx_time_now_us": _exact((), INT),
    "_nyx_time_sleep_ms": _exact((INT,), VOID),
    "_nyx_base64_encode": _exact((STRING,), STRING),
    "_nyx_base64_decode": _exact((STRING,), STRING),
    "_nyx_hash_fnv1a_64_hex": _exact((STRING,), STRING),
    "_nyx_fs_read_to_string": _exact((STRING,), STRING),
    "_nyx_fs_write_string": _exact((STRING, STRING), BOOL),
    "_nyx_fs_append_string": _exact((STRING, STRING), BOOL),
    "_nyx_fs_exists": _exact((STRING,), BOOL),
    "_nyx_fs_remove_file": _exact((STRING,), BOOL),
    "_nyx_json_get_string": _exact((STRING, STRING), STRING),
    "_nyx_json_get_int": _exact((STRING, STRING), INT),
    "_nyx_json_get_string_full": _exact((STRING, STRING), STRING),
    "_nyx_json_get_int_full": _exact((STRING, STRING), INT),
    "_nyx_json_get_bool_full": _exact((STRING, STRING), BOOL),
    "_nyx_json_has_key": _exact((STRING, STRING), BOOL),
    "_nyx_json_escape": _exact((STRING,), STRING),
    "_nyx_net_tcp_connect": _exact((STRING, INT), INT),
    "_nyx_net_tcp_send": _exact((INT, STRING), BOOL),
    "_nyx_net_tcp_recv": _exact((INT, INT), STRING),
    "_nyx_net_tcp_close": _exact((INT,), VOID),
    "_nyx_mutex_create": _exact((), INT),
    "_nyx_mutex_lock": _exact((INT,), VOID),
    "_nyx_mutex_unlock": _exact((INT,), VOID),
    "_nyx_channel_create": _exact((), INT),
    "_nyx_channel_send": _exact((INT, STRING), VOID),
    "_nyx_channel_recv": _exact((INT,), STRING),
}


INTRINSIC_TYPES: Dict[str, IRType] = {
    name: signature.type for name, signature in INTRINSICS.items()
}
