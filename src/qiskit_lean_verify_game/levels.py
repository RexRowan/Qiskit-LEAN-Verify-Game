"""
levels.py

Level content for the Clifford world, ported from CliffordGame's
docs/ROADMAP.md. Each level is expressed entirely in terms of Qiskit
objects (QuantumCircuit, Statevector) so grading never needs anything
outside the Qiskit SDK.

Levels 1-7 of CliffordGame's roadmap map directly onto "does this circuit
reach this state" and are included here. Level 8 (ZX spider fusion) is
deliberately NOT ported — a ZX diagram isn't a Qiskit circuit, and forcing
it into this package's model would misrepresent what's actually being
checked. Spider fusion stays specific to the ZX-World extension of the
lean4game submission.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# Gates a level is allowed to offer as buttons in the widget. Each entry is
# (display_label, arity, apply_fn). apply_fn takes (circuit, *qubits).
GATE_LIBRARY = {
    "H": ("H", 1, lambda qc, q: qc.h(q)),
    "X": ("X", 1, lambda qc, q: qc.x(q)),
    "Z": ("Z", 1, lambda qc, q: qc.z(q)),
    "S": ("S", 1, lambda qc, q: qc.s(q)),
    "CNOT": ("CNOT", 2, lambda qc, c, t: qc.cx(c, t)),
}


@dataclass(frozen=True)
class Level:
    id: str
    title: str
    goal: str
    num_qubits: int
    allowed_gates: list[str]
    target: Statevector
    initial_state: Statevector | None = None  # defaults to |0...0> if None
    phase_sensitive: bool = False
    hint: str | None = None
    # Optional worked solution, used only by tests to sanity-check the
    # level is actually solvable with its own allowed gate set.
    reference_solution: list[tuple] = field(default_factory=list)


def _state(label: str) -> Statevector:
    return Statevector.from_label(label)


def _bell_state() -> Statevector:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return Statevector.from_instruction(qc)


def _superposition_minus() -> Statevector:
    # |-> = (|0> - |1>)/sqrt(2), reached by X then H, or H then Z.
    return Statevector([1 / np.sqrt(2), -1 / np.sqrt(2)])


LEVELS: list[Level] = [
    Level(
        id="level01_h_squared",
        title="Do it twice, get nothing",
        goal="Apply gates so the qubit ends up exactly where it started.",
        num_qubits=1,
        allowed_gates=["H"],
        target=_state("0"),
        hint="What gate undoes itself?",
        reference_solution=[("H", 0), ("H", 0)],
    ),
    Level(
        id="level02_x_squared",
        title="Flip and flip back",
        goal="Return the qubit to |0> using only X.",
        num_qubits=1,
        allowed_gates=["X"],
        target=_state("0"),
        reference_solution=[("X", 0), ("X", 0)],
    ),
    Level(
        id="level03_hxh_is_z",
        title="Change of basis",
        goal="Starting from |1>, use H, X, H (in that order) and land on the "
        "same state Z would have given you.",
        num_qubits=1,
        allowed_gates=["H", "X"],
        initial_state=_state("1"),
        target=_state("1"),  # Z|1> = -|1>, phase-insensitive check
        hint="H X H is a basis change of X — what does it become?",
        reference_solution=[("H", 0), ("X", 0), ("H", 0)],
    ),
    Level(
        id="level04_hzh_is_x",
        title="Change of basis, the other way",
        goal="Starting from |0>, use H, Z, H (in that order) to reach the "
        "state X would have given you.",
        num_qubits=1,
        allowed_gates=["H", "Z"],
        target=_state("1"),
        reference_solution=[("H", 0), ("Z", 0), ("H", 0)],
    ),
    Level(
        id="level05_s_squared",
        title="Two quarter turns",
        goal="Apply S twice and check the result matches Z on |1>.",
        num_qubits=1,
        allowed_gates=["S"],
        initial_state=_state("1"),
        target=_state("1"),  # phase-insensitive: S^2|1> = -|1> ~ |1>
        reference_solution=[("S", 0), ("S", 0)],
    ),
    Level(
        id="level06_interference",
        title="Make it vanish",
        goal="Starting from |0>, reach the state (|0> - |1>)/sqrt(2).",
        num_qubits=1,
        allowed_gates=["H", "X", "Z"],
        target=_superposition_minus(),
        phase_sensitive=True,
        hint="More than one gate sequence works here.",
        reference_solution=[("X", 0), ("H", 0)],
    ),
    Level(
        id="level07_bell_state",
        title="Two qubits, one fate",
        goal="Starting from |00>, entangle the two qubits into a Bell state.",
        num_qubits=2,
        allowed_gates=["H", "CNOT"],
        target=_bell_state(),
        reference_solution=[("H", 0), ("CNOT", 0, 1)],
    ),
]


def get_level(level_id: str) -> Level:
    for level in LEVELS:
        if level.id == level_id:
            return level
    raise KeyError(f"No such level: {level_id!r}")


def build_circuit(level: Level, gate_sequence: list[tuple]) -> QuantumCircuit:
    """Build a QuantumCircuit from a sequence of (gate_name, *qubits) moves,
    validating every move is in the level's allowed gate set."""
    qc = QuantumCircuit(level.num_qubits)
    for move in gate_sequence:
        gate_name, *qubits = move
        if gate_name not in level.allowed_gates:
            raise ValueError(
                f"Gate {gate_name!r} is not allowed in level {level.id!r} "
                f"(allowed: {level.allowed_gates})."
            )
        _, arity, apply_fn = GATE_LIBRARY[gate_name]
        if len(qubits) != arity:
            raise ValueError(f"Gate {gate_name!r} expects {arity} qubit(s), got {qubits}.")
        apply_fn(qc, *qubits)
    return qc
