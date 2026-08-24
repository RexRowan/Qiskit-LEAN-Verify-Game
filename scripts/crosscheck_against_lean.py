"""
crosscheck_against_lean.py

Runs CliffordGame's Lean proofs (via a vendored, dependency-free copy of
CliffordMath.lean — see lean_reference/) and diffs the resulting
amplitude vectors against this package's own Qiskit-based grader,
computed completely independently. This is the actual cross-check the
placeholder version of this file used to only describe.

Requires a Lean 4 toolchain on PATH (matching lean_reference/lean-toolchain).
No Mathlib, no Lake, no GameServer needed — CliffordMath.lean has zero
dependencies beyond core Lean, which is exactly why this script can stay
fast and simple.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import numpy as np

from qiskit_lean_verify_game.levels import LEVELS, build_circuit

LEAN_REF_DIR = Path(__file__).parent / "lean_reference"


def run_lean_reference() -> dict[str, np.ndarray]:
    """Compile (if needed) and run PrintResults.lean, returning a dict
    from "level_id/result" and "level_id/target" to unnormalized complex
    amplitude vectors."""
    olean = LEAN_REF_DIR / "CliffordMath.olean"
    subprocess.run(
        ["lean", "CliffordMath.lean", "-o", str(olean)],
        cwd=LEAN_REF_DIR,
        check=True,
        capture_output=True,
        text=True,
    )
    result = subprocess.run(
        ["lean", "--run", "PrintResults.lean"],
        cwd=LEAN_REF_DIR,
        env={**os.environ, "LEAN_PATH": "."},
        check=True,
        capture_output=True,
        text=True,
    )

    parsed: dict[str, np.ndarray] = {}
    for line in result.stdout.strip().splitlines():
        parts = line.split()
        label = parts[0]
        nums = [int(x) for x in parts[1:]]
        amps = [complex(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
        parsed[label] = np.array(amps)
    return parsed


def proportional(v: np.ndarray, w: np.ndarray, atol: float = 1e-9) -> bool:
    """Same projective-equivalence check CliffordMath.lean's prop1/prop2
    perform, reimplemented independently here in Python/NumPy rather than
    imported from grader.py — the point of this script is an independent
    check, not routing through the same code path being validated."""
    idx = np.argmax(np.abs(w))
    if np.abs(w[idx]) < atol:
        return np.allclose(v, w, atol=atol)
    scale = v[idx] / w[idx]
    return np.allclose(v, scale * w, atol=atol)


def crosscheck_level(level_id: str, lean_results: dict[str, np.ndarray]) -> tuple[bool, str]:
    level = next(lvl for lvl in LEVELS if lvl.id == level_id)
    circuit = build_circuit(level, level.reference_solution)

    from qiskit.quantum_info import Statevector

    start = (
        level.initial_state
        if level.initial_state is not None
        else Statevector.from_label("0" * level.num_qubits)
    )
    qiskit_result = start.evolve(circuit).data

    lean_result = lean_results[f"{level_id}/result"]
    lean_target = lean_results[f"{level_id}/target"]

    # Sanity check: Lean's own claim (result proportional to target) must
    # hold, independently of anything Qiskit computed.
    if not proportional(lean_result, lean_target):
        return False, (
            "Lean's own result is not proportional to its own target — "
            "this would mean CliffordMath.lean's proofs are wrong, which "
            "should be impossible if `lake build` passed."
        )

    # The actual cross-check: does Qiskit's independently-simulated
    # circuit match Lean's computed result (both checked against the
    # same target, up to normalization and phase)?
    if not proportional(qiskit_result, lean_result):
        return False, f"Qiskit result {qiskit_result} not proportional to Lean result {lean_result}"

    return True, "OK"


def main() -> int:
    print("Running CliffordGame's Lean reference implementation...")
    try:
        lean_results = run_lean_reference()
    except FileNotFoundError:
        print(
            "ERROR: `lean` not found on PATH. Install a Lean 4 toolchain "
            f"matching {LEAN_REF_DIR / 'lean-toolchain'} to run this "
            "cross-check.",
            file=sys.stderr,
        )
        return 1
    except subprocess.CalledProcessError as exc:
        print("ERROR: Lean reference implementation failed to build/run:", file=sys.stderr)
        print(exc.stderr, file=sys.stderr)
        return 1

    all_ok = True
    for level in LEVELS:
        ok, reason = crosscheck_level(level.id, lean_results)
        status = "OK" if ok else "MISMATCH"
        print(f"  [{status}] {level.id}: {reason}")
        all_ok = all_ok and ok

    if all_ok:
        print("\nAll levels cross-checked successfully against Lean.")
        return 0
    else:
        print("\nCross-check FAILED for one or more levels.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
