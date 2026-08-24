"""
grader.py

The decidable checker every level's win condition reduces to: does this
QuantumCircuit produce this target Statevector, up to global phase (or
exactly, when a level cares about phase)?

This is deliberately built on Qiskit's own Statevector/Operator classes,
not a hand-rolled matrix type — the whole point of this package (as
opposed to the CliffordGame lean4game submission) is that grading happens
inside real Qiskit objects, since that's what makes it Ecosystem-eligible
in the first place.

"Formally verified" in this package's README refers to cross-checking this
grader's behavior against equivalences proved in the companion CliffordGame
Lean repository (see scripts/crosscheck_against_lean.py and
data/verified_equivalences.json) — it does not mean this module calls Lean
at runtime. Nothing here has a Lean dependency.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


@dataclass(frozen=True)
class GradeResult:
    passed: bool
    reason: str


def _phase_aligned(a: np.ndarray, b: np.ndarray, atol: float) -> bool:
    """True if `a` equals `b` up to a global phase, within `atol`."""
    # Find the first entry where the target has non-negligible amplitude
    # and use it to fix the phase; if the whole target is ~0 (shouldn't
    # happen for a normalized state) fall back to direct comparison.
    idx = np.argmax(np.abs(b))
    if np.abs(b[idx]) < atol:
        return np.allclose(a, b, atol=atol)
    phase = a[idx] / b[idx]
    if not np.isclose(np.abs(phase), 1.0, atol=atol):
        return False
    return np.allclose(a, phase * b, atol=atol)


def grade_circuit(
    circuit: QuantumCircuit,
    target: Statevector,
    *,
    initial_state: Statevector | None = None,
    phase_sensitive: bool = False,
    atol: float = 1e-8,
) -> GradeResult:
    """Grade a player-built circuit against a level's target state.

    Parameters
    ----------
    circuit:
        The circuit the player assembled (gates in the order applied).
    target:
        The state the level wants the player to reach.
    initial_state:
        The state the circuit is applied to. Defaults to |0...0>.
    phase_sensitive:
        If False (the default and the right choice for essentially every
        Clifford-world level), a global-phase difference does not fail
        the level — physically, global phase is unobservable. Set True
        only for levels that are specifically about phase (rare; none in
        v1's roadmap).
    atol:
        Absolute tolerance for floating-point comparison.
    """
    n = circuit.num_qubits
    start = initial_state if initial_state is not None else Statevector.from_label("0" * n)
    if start.num_qubits != n or target.num_qubits != n:
        return GradeResult(
            passed=False,
            reason=f"Qubit count mismatch: circuit has {n}, expected {start.num_qubits}.",
        )

    result = start.evolve(circuit)

    if phase_sensitive:
        ok = np.allclose(result.data, target.data, atol=atol)
    else:
        ok = _phase_aligned(result.data, target.data, atol=atol)

    if ok:
        return GradeResult(passed=True, reason="Circuit matches the target state.")
    return GradeResult(
        passed=False,
        reason="Circuit does not match the target state.",
    )
