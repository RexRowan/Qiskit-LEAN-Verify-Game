"""qiskit_lean_verify_game — a decidable-checker circuit puzzle package
built on the Qiskit SDK, with level content ported from the CliffordGame
lean4game submission.

See docs/LIMITATIONS.md before describing this package's "verified"
status anywhere external-facing.
"""

from .grader import GradeResult, grade_circuit
from .levels import LEVELS, Level, build_circuit, get_level

__all__ = [
    "GradeResult",
    "grade_circuit",
    "LEVELS",
    "Level",
    "build_circuit",
    "get_level",
]

__version__ = "0.1.0"
