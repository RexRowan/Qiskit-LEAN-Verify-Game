# Limitations

## "Verified" status — read this before writing any external-facing copy

This package's grader (`grader.py`) checks circuits using Qiskit's own
`Statevector` simulation — ordinary, well-tested linear algebra.

**As of this update, that grader's identities are cross-checked against
real Lean proofs**, not just asserted. `scripts/crosscheck_against_lean.py`
runs CliffordGame's actual proofs (via a vendored, dependency-free copy
of `Game/CliffordMath.lean`) and diffs the result against this package's
independently-computed Qiskit `Statevector` for the same circuit. All 7
levels pass. Run the script yourself before trusting this indefinitely —
`scripts/lean_reference/` is a manually-synced copy of CliffordGame's
source and can drift out of date.

Accurate framing now: "circuit puzzles, cross-checked against Lean proofs
in the companion CliffordGame project" — this is now true, not aspirational.

## Scope limits carried over from CliffordGame

- No continuous-parameter gates (general `Rz(θ)`). Everything here is
  Clifford + `S`.
- No algorithm-level levels (Deutsch, Grover, Shor) — see CliffordGame's
  `docs/ROADMAP.md` for why these are explicitly out, not just deferred.
- Level 8 (ZX spider fusion) from CliffordGame's roadmap is not ported
  here — it isn't expressible as a Qiskit circuit-to-state check without
  distorting what's actually being verified.

## Widget

`widget.py` requires `ipywidgets` and an IPython/Jupyter environment.
`grader.py` and `levels.py` have no such dependency and can be used
headlessly (e.g. in CI, or a non-notebook script).

## Single-qubit gate targeting

v1's gate-button handlers hard-code qubit 0 for single-qubit gates and
(0, 1) for CNOT, since no v1 level needs more than that. Generalizing to
a qubit picker is straightforward but deliberately not built until a level
actually needs it.
