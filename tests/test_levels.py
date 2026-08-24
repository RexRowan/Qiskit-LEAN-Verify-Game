import pytest

from qiskit_lean_verify_game.grader import grade_circuit
from qiskit_lean_verify_game.levels import LEVELS, build_circuit


@pytest.mark.parametrize("level", LEVELS, ids=[lvl.id for lvl in LEVELS])
def test_reference_solution_passes(level):
    """Every level's own reference_solution must actually grade as PASS,
    using only gates in that level's allowed_gates. If this fails, the
    level is broken content, independent of the widget or CI."""
    circuit = build_circuit(level, level.reference_solution)
    result = grade_circuit(
        circuit,
        level.target,
        initial_state=level.initial_state,
        phase_sensitive=level.phase_sensitive,
    )
    assert result.passed, f"{level.id}: {result.reason}"


@pytest.mark.parametrize("level", LEVELS, ids=[lvl.id for lvl in LEVELS])
def test_disallowed_gate_is_rejected(level):
    """A move using a gate outside allowed_gates must raise, not silently
    build an illegal circuit."""
    candidates = [name for name in ("H", "X", "Z", "S", "CNOT") if name not in level.allowed_gates]
    if not candidates:
        pytest.skip(f"{level.id} allows every gate; nothing to reject.")
    with pytest.raises(ValueError):
        build_circuit(level, [(candidates[0], 0)])
