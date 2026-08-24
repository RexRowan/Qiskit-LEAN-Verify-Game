import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from qiskit_lean_verify_game.grader import grade_circuit


def test_h_squared_returns_to_zero():
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.h(0)
    result = grade_circuit(qc, Statevector.from_label("0"))
    assert result.passed


def test_single_h_does_not_match_zero():
    qc = QuantumCircuit(1)
    qc.h(0)
    result = grade_circuit(qc, Statevector.from_label("0"))
    assert not result.passed


def test_hxh_equals_z_up_to_phase():
    # Z|1> = -|1>; H X H should match |1> up to global phase.
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.x(0)
    qc.h(0)
    result = grade_circuit(qc, Statevector.from_label("1"), initial_state=Statevector.from_label("1"))
    assert result.passed


def test_phase_sensitive_mode_catches_sign_flip():
    # S^2 = Z introduces a genuine -1 global phase on |1>; in
    # phase_sensitive mode this must NOT be treated as a match.
    qc = QuantumCircuit(1)
    qc.s(0)
    qc.s(0)
    result = grade_circuit(
        qc,
        Statevector.from_label("1"),
        initial_state=Statevector.from_label("1"),
        phase_sensitive=True,
    )
    assert not result.passed


def test_bell_state_from_h_cnot():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    target = Statevector([1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)])
    result = grade_circuit(qc, target)
    assert result.passed


def test_qubit_count_mismatch_fails_cleanly():
    qc = QuantumCircuit(1)
    qc.h(0)
    target = Statevector.from_label("00")
    result = grade_circuit(qc, target)
    assert not result.passed
    assert "mismatch" in result.reason.lower()
