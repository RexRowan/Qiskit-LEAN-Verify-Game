/-
PrintResults.lean

Standalone driver (bare `lean`, no Lake/GameServer/Mathlib needed) that
evaluates each Clifford-world level's authored gate sequence and prints
the resulting unnormalized amplitude vector. `crosscheck_against_lean.py`
runs this and compares the output against Qiskit's independently-computed
Statevector for the same circuit.

Kept in sync manually with CliffordGame's `Game/CliffordMath.lean` — that
repo is the source of truth; this is a vendored copy for a fast,
dependency-free cross-check without needing to fetch GameServer.
-/
import CliffordMath

def printQubit1 (label : String) (v : Qubit1) : IO Unit :=
  IO.println s!"{label} {v.a0.re} {v.a0.im} {v.a1.re} {v.a1.im}"

def printQubit2 (label : String) (v : Qubit2) : IO Unit := do
  IO.println s!"{label} {v.a00.re} {v.a00.im} {v.a01.re} {v.a01.im} {v.a10.re} {v.a10.im} {v.a11.re} {v.a11.im}"

def main : IO Unit := do
  printQubit1 "level01_h_squared/result" (applyAll1 [.H, .H] zeroState)
  printQubit1 "level01_h_squared/target" zeroState

  printQubit1 "level02_x_squared/result" (applyAll1 [.X, .X] zeroState)
  printQubit1 "level02_x_squared/target" zeroState

  printQubit1 "level03_hxh_is_z/result" (applyAll1 [.H, .X, .H] oneState)
  printQubit1 "level03_hxh_is_z/target" (applyGate1 .Z oneState)

  printQubit1 "level04_hzh_is_x/result" (applyAll1 [.H, .Z, .H] zeroState)
  printQubit1 "level04_hzh_is_x/target" (applyGate1 .X zeroState)

  printQubit1 "level05_s_squared/result" (applyAll1 [.S, .S] oneState)
  printQubit1 "level05_s_squared/target" (applyGate1 .Z oneState)

  printQubit1 "level06_interference/result" (applyAll1 [.X, .H] zeroState)
  printQubit1 "level06_interference/target" minusState

  printQubit2 "level07_bell_state/result" (applyCNOT (applyH0 (tensor1 zeroState zeroState)))
  printQubit2 "level07_bell_state/target" bellTarget
