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

**What "cross-checked" precisely claims, and doesn't:** the check is that
this package's Qiskit `Statevector` result and CliffordGame's Lean-proven
result agree, for each of these 7 specific circuits. That is not the same
claim as "this package is formally verified," and that stronger phrase
should not be used. In particular this cross-check does **not** establish:
a general formal correspondence between Qiskit's `Statevector` semantics
and Lean's semantics (only agreement on these 7 instances); that Qiskit's
simulator itself is formally verified (it isn't, and this project makes
no claim about Qiskit's internals); or anything about circuits/levels this
package doesn't ship. The defensible sentence is "the target equivalences
are proven in Lean, and this package's Qiskit implementation is
independently cross-checked against those proofs" — not "verified by
Lean" on its own, which reads as a much broader claim than what's actually
been established.

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
