"""Rust 2021 source emitter for legalized scalar/control-flow MIR."""

from __future__ import annotations

import json
import math
import re
from dataclasses import replace

from .codegen_cpp import MIRCodegenError
from .legalization import legalize_mir
from .model import (
    AggregateRValue,
    AssertTerminator,
    AssignStatement,
    BinaryRValue,
    CastRValue,
    CallTerminator,
    ConstOperand,
    ConstantIndexProjection,
    CopyOperand,
    FieldProjection,
    GotoTerminator,
    IndexProjection,
    MIRFunction,
    MIRModule,
    MIRStructDef,
    MoveOperand,
    NopStatement,
    Operand,
    Place,
    ReturnTerminator,
    StorageDeadStatement,
    StorageLiveStatement,
    SwitchIntTerminator,
    SwitchValueTerminator,
    UnaryRValue,
    UnreachableTerminator,
    UseRValue,
)
from .types import MIRType


_RUNTIME = r'''trait NyxDisplay {
    fn nyx_display(&self) -> String;
}

impl NyxDisplay for i64 { fn nyx_display(&self) -> String { self.to_string() } }
impl NyxDisplay for bool {
    fn nyx_display(&self) -> String {
        if *self { "true".to_string() } else { "false".to_string() }
    }
}
impl NyxDisplay for f64 {
    fn nyx_display(&self) -> String {
        if self.is_nan() { return "nan".to_string(); }
        if *self == f64::INFINITY { return "inf".to_string(); }
        if *self == f64::NEG_INFINITY { return "-inf".to_string(); }
        if *self == 0.0 { return "0".to_string(); }
        self.to_string()
    }
}
impl NyxDisplay for String { fn nyx_display(&self) -> String { self.clone() } }

fn nyx_display<T: NyxDisplay + ?Sized>(value: &T) -> String { value.nyx_display() }

fn nyx_i64_div(left: i64, right: i64) -> i64 {
    if right == 0 { panic!("division by zero"); }
    if left == i64::MIN && right == -1 { i64::MIN } else { left / right }
}

fn nyx_i64_rem(left: i64, right: i64) -> i64 {
    if right == 0 { panic!("remainder by zero"); }
    if left == i64::MIN && right == -1 { 0 } else { left % right }
}

fn nyx_index<T>(values: &[T], index: i64) -> &T {
    if index < 0 || index as usize >= values.len() { panic!("array index out of bounds"); }
    &values[index as usize]
}

fn nyx_index_mut<T>(values: &mut [T], index: i64) -> &mut T {
    if index < 0 || index as usize >= values.len() { panic!("array index out of bounds"); }
    &mut values[index as usize]
}'''


def _identifier(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not clean or clean[0].isdigit():
        clean = "_" + clean
    return clean


class _RustEmitter:
    def __init__(self, module: MIRModule):
        self.module = module
        self.function_names = {
            function.symbol: f"nyx_fn_{_identifier(function.name)}"
            for function in module.functions
        }
        self.function_names.update({
            function.name: self.function_names[function.symbol]
            for function in module.functions
        })
        self.functions = {function.symbol: function for function in module.functions}
        self.functions.update({function.name: function for function in module.functions})
        self.structs = {
            definition.name: definition
            for definition in module.type_definitions
            if isinstance(definition, MIRStructDef)
        }
        self.current: MIRFunction | None = None
        self.local_types: dict[int, MIRType] = {}

    def emit(self) -> str:
        parts = [
            "// Experimental Nyx legalized MIR -> Rust 2021 output.",
            "#![allow(dead_code, unused_assignments, unused_mut, unreachable_code)]",
            "",
            _RUNTIME,
            "",
        ]
        parts.extend(self._struct_definition(definition) + "\n" for definition in self.structs.values())
        parts.extend(self._function(function) + "\n" for function in self.module.functions)
        parts.append(self._entry_point())
        return "\n".join(parts).rstrip() + "\n"

    def _struct_definition(self, definition: MIRStructDef) -> str:
        lines = ["#[derive(Clone, Debug, Default, PartialEq)]", f"struct NyxType_{_identifier(definition.name)} {{"]
        for field in definition.fields:
            lines.append(f"    {_identifier(field.name)}: {self._type(field.type)},")
        lines.append("}")
        return "\n".join(lines)

    def _entry_point(self) -> str:
        by_name = {function.name: function for function in self.module.functions}
        entry = by_name.get("main") or by_name.get("__nyx_top_level")
        if entry is None:
            return "fn main() {}"
        return f"fn main() {{ {self.function_names[entry.symbol]}(); }}"

    def _function(self, function: MIRFunction) -> str:
        self.current = function
        self.local_types = {local.id: local.type for local in function.locals}
        parameters = ", ".join(
            f"l{local}: {self._type(function.locals[local].type, function)}"
            for local in function.parameters
        )
        return_type = self._type(function.locals[function.return_local].type, function)
        suffix = "" if return_type == "()" else f" -> {return_type}"
        lines = [f"fn {self.function_names[function.symbol]}({parameters}){suffix} {{"]
        parameter_ids = set(function.parameters)
        for local in function.locals:
            rendered = self._type(local.type, function)
            if local.id in parameter_ids or rendered == "()":
                continue
            lines.append(f"    let mut l{local.id}: {rendered} = {self._default(local.type)};")
        lines.extend(("    let mut pc: usize = 0;", "    loop {", "        match pc {"))
        for block in function.blocks:
            lines.append(f"            {block.id} => {{")
            for statement in block.statements:
                lines.extend(f"                {line}" for line in self._statement(statement))
            lines.extend(f"                {line}" for line in self._terminator(block.terminator))
            lines.append("            }")
        lines.extend(("            _ => unreachable!(\"invalid MIR block\"),", "        }", "    }", "}"))
        self.current = None
        self.local_types = {}
        return "\n".join(lines)

    def _statement(self, statement: object) -> list[str]:
        if isinstance(statement, AssignStatement):
            destination = self._place_type(statement.place)
            if destination.name in ("void", "any"):
                return []
            return [self._assign_place(statement.place, self._rvalue(statement.value))]
        if isinstance(statement, (StorageLiveStatement, StorageDeadStatement, NopStatement)):
            return []
        raise MIRCodegenError(f"illegal statement reached Rust emitter: {type(statement).__name__}")

    def _terminator(self, value: object) -> list[str]:
        if isinstance(value, GotoTerminator):
            return self._goto(value.target)
        if isinstance(value, SwitchIntTerminator):
            discriminator = self._operand(value.discriminator)
            discriminator_type = self._operand_type(value.discriminator)
            lines: list[str] = []
            for expected, target in value.targets:
                rendered = (
                    "true" if bool(expected) else "false"
                ) if discriminator_type.name == "bool" else self._constant(expected)
                lines.append(f"if {discriminator} == {rendered} {{")
                lines.extend(f"    {line}" for line in self._goto(target))
                lines.append("}")
            lines.extend(self._goto(value.otherwise))
            return lines
        if isinstance(value, SwitchValueTerminator):
            discriminator = self._operand(value.discriminator)
            discriminator_type = self._operand_type(value.discriminator)
            lines = []
            for expected, target in value.targets:
                if expected is None and discriminator_type.optional:
                    condition = f"({discriminator}).is_none()"
                elif discriminator_type.optional:
                    condition = f"({discriminator}).as_ref() == Some(&{self._constant(expected)})"
                else:
                    condition = f"{discriminator} == {self._constant(expected)}"
                lines.append(f"if {condition} {{")
                lines.extend(f"    {line}" for line in self._goto(target))
                lines.append("}")
            lines.extend(self._goto(value.otherwise))
            return lines
        if isinstance(value, CallTerminator):
            if value.target is None:
                raise MIRCodegenError(f"call '{value.function}' has no continuation")
            arguments = ", ".join(self._operand(argument) for argument in value.arguments)
            if value.function == "builtin::print":
                displays = ", ".join(
                    f"nyx_display(&{self._operand(argument)})" for argument in value.arguments
                )
                line = "println!();" if not displays else f"println!(\"{{}}\", [{displays}].join(\" \"));"
            elif value.function == "builtin::len":
                if len(value.arguments) != 1 or value.destination is None:
                    raise MIRCodegenError("builtin::len requires one argument and a destination")
                line = f"{self._place(value.destination)} = {self._operand(value.arguments[0])}.len() as i64;"
            elif value.function == "builtin::to_string":
                if len(value.arguments) != 1 or value.destination is None:
                    raise MIRCodegenError("builtin::to_string requires one argument and a destination")
                line = f"{self._place(value.destination)} = nyx_display(&{self._operand(value.arguments[0])});"
            elif value.function in self.function_names:
                call = f"{self.function_names[value.function]}({arguments})"
                callee = self.functions[value.function]
                result = self._type(callee.locals[callee.return_local].type, callee)
                if value.destination is not None and result != "()":
                    line = f"l{value.destination.local} = {call};"
                else:
                    line = f"{call};"
            else:
                raise MIRCodegenError(f"illegal runtime call reached Rust emitter: {value.function}")
            return [line] + self._goto(value.target)
        if isinstance(value, AssertTerminator):
            condition = self._operand(value.condition)
            expected = "true" if value.expected else "false"
            return [
                f"if ({condition}) != {expected} {{ panic!({json.dumps(value.message)}); }}"
            ] + self._goto(value.target)
        if isinstance(value, ReturnTerminator):
            assert self.current is not None
            result = self._type(self.current.locals[self.current.return_local].type, self.current)
            return ["return;"] if result == "()" else ["return l0;"]
        if isinstance(value, UnreachableTerminator):
            return ["unreachable!(\"reached unreachable MIR terminator\");"]
        raise MIRCodegenError(f"illegal terminator reached Rust emitter: {type(value).__name__}")

    @staticmethod
    def _goto(target: int) -> list[str]:
        return [f"pc = {target};", "continue;"]

    def _rvalue(self, value: object) -> str:
        if isinstance(value, UseRValue):
            return self._operand(value.operand)
        if isinstance(value, BinaryRValue):
            return self._binary(value)
        if isinstance(value, CastRValue):
            operand = self._operand(value.operand)
            if value.kind == "optional-unwrap":
                return f"({operand}).expect(\"optional unwrap failed\")"
            if value.type.optional:
                return f"Some({operand})"
            return operand
        if isinstance(value, AggregateRValue):
            operands = [self._operand(operand) for operand in value.operands]
            if value.kind == "array":
                return "vec![" + ", ".join(operands) + "]"
            if value.kind == "struct":
                fields = value.fields or tuple(str(index) for index in range(len(operands)))
                body = ", ".join(f"{_identifier(name)}: {operand}" for name, operand in zip(fields, operands))
                return f"NyxType_{_identifier(value.name)} {{ {body} }}"
            raise MIRCodegenError(f"unsupported Rust aggregate kind '{value.kind}'")
        if isinstance(value, UnaryRValue):
            operand = self._operand(value.operand)
            if value.op in ("!", "not"):
                return f"!({operand})"
            if value.op == "+":
                return operand
            if value.op == "-" and value.type.name == "int":
                return f"({operand}).wrapping_neg()"
            if value.op == "-":
                return f"-({operand})"
            if value.op == "~":
                return f"!({operand})"
            raise MIRCodegenError(f"unsupported Rust unary operation '{value.op}'")
        raise MIRCodegenError(f"illegal rvalue reached Rust emitter: {type(value).__name__}")

    def _binary(self, value: BinaryRValue) -> str:
        left = self._operand(value.left)
        right = self._operand(value.right)
        left_type = self._operand_type(value.left)
        right_type = self._operand_type(value.right)
        if value.op in ("==", "!=", "<", "<=", ">", ">="):
            return f"({left} {value.op} {right})"
        if value.op == "+" and (left_type.name == "string" or right_type.name == "string"):
            return f"format!(\"{{}}{{}}\", {left}, {right})"
        if left_type.name in ("float", "f64") or right_type.name in ("float", "f64"):
            if value.op in ("+", "-", "*", "/", "%"):
                return f"({left} {value.op} {right})"
        integer_operations = {
            "+": "wrapping_add", "-": "wrapping_sub", "*": "wrapping_mul",
        }
        if value.op in integer_operations:
            return f"({left}).{integer_operations[value.op]}({right})"
        if value.op == "/":
            return f"nyx_i64_div({left}, {right})"
        if value.op == "%":
            return f"nyx_i64_rem({left}, {right})"
        if value.op == "<<":
            return f"({left}).wrapping_shl(({right} as u32) & 63)"
        if value.op == ">>":
            return f"({left}).wrapping_shr(({right} as u32) & 63)"
        if value.op in ("&", "|", "^"):
            return f"({left} {value.op} {right})"
        raise MIRCodegenError(f"unsupported Rust binary operation '{value.op}'")

    def _operand(self, value: Operand) -> str:
        if isinstance(value, ConstOperand):
            return self._typed_constant(value)
        if isinstance(value, (CopyOperand, MoveOperand)):
            rendered = self._place(value.place)
            if isinstance(value, CopyOperand):
                return rendered + ".clone()"
            return rendered
        raise MIRCodegenError(f"illegal operand reached Rust emitter: {type(value).__name__}")

    def _operand_type(self, value: Operand) -> MIRType:
        if isinstance(value, ConstOperand):
            return value.type
        if isinstance(value, (CopyOperand, MoveOperand)):
            return self._place_type(value.place)
        raise MIRCodegenError(f"unknown Rust operand type: {type(value).__name__}")

    @staticmethod
    def _typed_constant(value: ConstOperand) -> str:
        if value.type.optional and value.value is None:
            return "None"
        if value.type.name == "string":
            return f"String::from({json.dumps(str(value.value), ensure_ascii=False)})"
        if value.type.name == "bool":
            return "true" if value.value else "false"
        if value.type.name in ("float", "f64"):
            number = float(value.value)
            if math.isnan(number):
                return "f64::NAN"
            if math.isinf(number):
                return "f64::INFINITY" if number > 0 else "f64::NEG_INFINITY"
            return repr(number)
        return str(value.value)

    @staticmethod
    def _constant(value: object) -> str:
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, str):
            return f"String::from({json.dumps(value, ensure_ascii=False)})"
        return str(value)

    @staticmethod
    def _type(value: MIRType, function: MIRFunction | None = None) -> str:
        if value.name == "any" and function is not None and function.name == "main":
            return "()"
        if value.optional:
            return f"Option<{_RustEmitter._type(replace(value, optional=False), function)}>"
        if value.name == "Array" and len(value.arguments) == 1:
            return f"Vec<{_RustEmitter._type(value.arguments[0], function)}>"
        mapping = {"void": "()", "bool": "bool", "int": "i64", "float": "f64", "f64": "f64", "string": "String"}
        rendered = mapping.get(value.name, f"NyxType_{_identifier(value.name)}")
        if value.pointer or value.arguments:
            raise MIRCodegenError(f"unsupported Rust MIR type '{value}'")
        return rendered

    @staticmethod
    def _default(value: MIRType) -> str:
        if value.optional:
            return "None"
        if value.name == "Array":
            return "Vec::new()"
        return {"bool": "false", "int": "0", "float": "0.0", "f64": "0.0", "string": "String::new()"}.get(value.name, "Default::default()")

    def _place(self, place: Place, *, mutable: bool = False) -> str:
        rendered = f"l{place.local}"
        value_type = self.local_types[place.local]
        for projection in place.projections:
            if value_type.optional:
                accessor = "as_mut" if mutable else "as_ref"
                rendered = f"({rendered}).{accessor}().expect(\"optional projection failed\")"
                value_type = replace(value_type, optional=False)
            if isinstance(projection, FieldProjection):
                rendered = f"({rendered}).{_identifier(projection.name)}"
                value_type = self._field_type(value_type, projection.name)
            elif isinstance(projection, ConstantIndexProjection):
                helper = "nyx_index_mut" if mutable else "nyx_index"
                borrow = "&mut " if mutable else "&"
                rendered = f"{helper}({borrow}{rendered}, {projection.index})"
                value_type = self._index_type(value_type)
            elif isinstance(projection, IndexProjection):
                helper = "nyx_index_mut" if mutable else "nyx_index"
                borrow = "&mut " if mutable else "&"
                rendered = f"{helper}({borrow}{rendered}, l{projection.local})"
                value_type = self._index_type(value_type)
            else:
                raise MIRCodegenError(f"illegal projection reached Rust emitter: {type(projection).__name__}")
        return rendered

    def _assign_place(self, place: Place, value: str) -> str:
        rendered = self._place(place, mutable=True)
        prefix = "*" if place.projections and isinstance(place.projections[-1], (IndexProjection, ConstantIndexProjection)) else ""
        return f"{prefix}{rendered} = {value};"

    def _place_type(self, place: Place) -> MIRType:
        value_type = self.local_types[place.local]
        for projection in place.projections:
            if value_type.optional:
                value_type = replace(value_type, optional=False)
            if isinstance(projection, FieldProjection):
                value_type = self._field_type(value_type, projection.name)
            elif isinstance(projection, (ConstantIndexProjection, IndexProjection)):
                value_type = self._index_type(value_type)
            else:
                raise MIRCodegenError(f"unknown Rust projection type: {type(projection).__name__}")
        return value_type

    def _field_type(self, value_type: MIRType, name: str) -> MIRType:
        definition = self.structs.get(value_type.name)
        if definition is None:
            raise MIRCodegenError(f"field projection requires a known struct, got '{value_type}'")
        field = next((item for item in definition.fields if item.name == name), None)
        if field is None:
            raise MIRCodegenError(f"struct '{definition.name}' has no field '{name}'")
        return field.type

    @staticmethod
    def _index_type(value_type: MIRType) -> MIRType:
        if value_type.name == "Array" and len(value_type.arguments) == 1:
            return value_type.arguments[0]
        raise MIRCodegenError(f"index projection requires Array<T>, got '{value_type}'")


def emit_legalized_rust(module: MIRModule) -> str:
    return _RustEmitter(legalize_mir(module, "rust", require_emitter=True)).emit()
