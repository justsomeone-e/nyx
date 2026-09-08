"""Experimental Nyx MIR infrastructure.

MIR is not part of the default compilation route. Importing this package does
not redirect any existing Typed HIR backend.
"""

from .builder import MIRFunctionBuilder
from .lowering import MIRLoweringError, lower_hir_skeleton
from .model import *
from .passes import MIRPass, MIRPassManager, MIRPassRecord, MIRPassResult
from .printer import print_mir
from .serialization import fingerprint, from_data, from_json, to_data, to_json
from .types import MIRType, from_hir_type
from .verifier import (
    MIRVerificationError,
    MIRVerificationIssue,
    collect_mir_issues,
    verify_mir,
)

__all__ = [name for name in globals() if not name.startswith("_")]
