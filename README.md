# Qiskit LEAN Verify Game

Circuit puzzles built on the Qiskit SDK, with level content shared with the
[CliffordGame](https://github.com/RexRowan/CliffordGame) lean4game
submission. This package is the Qiskit-Ecosystem-eligible half of that
project — it interfaces with `qiskit.QuantumCircuit` and
`qiskit.quantum_info.Statevector` directly, which the lean4game version
(pure Lean, no Python) structurally cannot do.

**Read `docs/LIMITATIONS.md` before writing any external-facing copy about
this package.** In particular: do not call this "formally verified" until
`scripts/crosscheck_against_lean.py` is real and passing — right now it
is an honest placeholder.

## Install

```bash
pip install -e ".[widget,test]"
```

## Use

```python
from qiskit_lean_verify_game.levels import get_level, build_circuit
from qiskit_lean_verify_game.grader import grade_circuit

level = get_level("level07_bell_state")
circuit = build_circuit(level, [("H", 0), ("CNOT", 0, 1)])
result = grade_circuit(circuit, level.target)
print(result.passed, result.reason)
```

In a notebook, for the interactive gate-button widget on a single level:

```python
from qiskit_lean_verify_game.widget import LevelWidget
from qiskit_lean_verify_game.levels import get_level

LevelWidget(get_level("level07_bell_state")).show()
```

Or for the full click-through-all-levels experience — a row of level
buttons (checkmarked as you solve them) plus the active level's gate
buttons:

```python
from qiskit_lean_verify_game.widget import GameShell

GameShell().show()
```

## Structure

- `grader.py` — decidable circuit-vs-target checker (Statevector-based, no
  notebook or Lean dependency).
- `levels.py` — level content, ported from CliffordGame's v1 roadmap
  (Clifford-world levels 1-7; level 8 / ZX spider fusion deliberately not
  ported — see `docs/LIMITATIONS.md`).
- `widget.py` — Jupyter UI: `LevelWidget` (single level, gate buttons +
  live grading) and `GameShell` (level-select buttons on top, tracks
  solved state, swaps the active `LevelWidget`). Same `clear_output()` +
  redraw pattern as `qiskit-sqd-dashboard`.
- `data/verified_equivalences.json` + `scripts/crosscheck_against_lean.py`
  + `scripts/lean_reference/` — the cross-check machinery against
  CliffordGame's Lean proofs. **Functional as of this update**: run
  `python scripts/crosscheck_against_lean.py` (requires a Lean 4 toolchain
  on PATH) to independently verify this package's grader against
  CliffordGame's actual proofs.

## Status

v0.2.0. 27/27 tests passing (`pytest tests/`), including end-to-end tests
that click real `ipywidgets` buttons rather than only testing the grading
logic those buttons call. **Cross-checked against CliffordGame's actual
Lean proofs** via `scripts/crosscheck_against_lean.py` — all 7 levels
pass (requires a local Lean toolchain to rerun; not part of the pytest
suite since it needs Lean installed, which CI for this package doesn't
assume). Ready for Qiskit Ecosystem submission.
