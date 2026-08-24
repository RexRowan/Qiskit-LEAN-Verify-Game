/-
CliffordMath.lean

Core math for CliffordGame's Clifford-world levels. Deliberately has no
Mathlib dependency (same choice qiskit-zx-verified made for its spider
fusion proof) — everything here is decidable using only core Lean 4,
which keeps the game's build fast and avoids Mathlib's noncomputable
real/complex numbers entirely.

Key design decision: gate matrices are used UNNORMALIZED (no 1/sqrt(2)
factors), and state equality is checked as PROJECTIVE equivalence
(proportional up to any nonzero Gaussian-rational scalar), not exact
equality. This is not a simplification bolted on for convenience — it is
the mathematically correct notion of "same physical state": a pure
quantum state is an equivalence class of nonzero vectors under scalar
multiplication (a ray in projective Hilbert space), so checking
proportionality is the right check, and it lets every gate here (H
included) live entirely in the Gaussian rationals with no square roots.
-/

structure GRat where
  re : Int
  im : Int
deriving DecidableEq, Repr

namespace GRat

def add (x y : GRat) : GRat := ⟨x.re + y.re, x.im + y.im⟩
def neg (x : GRat) : GRat := ⟨-x.re, -x.im⟩
def mul (x y : GRat) : GRat := ⟨x.re * y.re - x.im * y.im, x.re * y.im + x.im * y.re⟩

instance : Add GRat := ⟨add⟩
instance : Neg GRat := ⟨neg⟩
instance : Mul GRat := ⟨mul⟩
instance : Sub GRat := ⟨fun x y => add x (neg y)⟩
instance : OfNat GRat n := ⟨⟨(n : Int), 0⟩⟩

/-- The imaginary unit, used by the S gate. -/
def i : GRat := ⟨0, 1⟩

end GRat

/-- A single-qubit unnormalized amplitude vector: a0•|0> + a1•|1>. -/
structure Qubit1 where
  a0 : GRat
  a1 : GRat
deriving DecidableEq, Repr

/-- Two-qubit unnormalized amplitude vector, basis order |00>,|01>,|10>,|11>. -/
structure Qubit2 where
  a00 : GRat
  a01 : GRat
  a10 : GRat
  a11 : GRat
deriving DecidableEq, Repr

/-- Projective equivalence for Qubit1: the single cross-condition
`v.a0 * w.a1 = v.a1 * w.a0` is the standard 2x2-determinant-zero test and
fully characterizes proportionality for 2-component vectors — no other
condition is needed. `abbrev` (not `def`) so `decide` can see through it
to the underlying `DecidableEq GRat` instance during typeclass search. -/
abbrev prop1 (v w : Qubit1) : Prop := v.a0 * w.a1 = v.a1 * w.a0

/-- Projective equivalence for Qubit2: all six pairwise cross-conditions
(one per pair of components) must vanish for the two 4-vectors to be
scalar multiples of each other. `abbrev` for the same reducibility reason
as `prop1`. -/
abbrev prop2 (v w : Qubit2) : Prop :=
  v.a00 * w.a01 = v.a01 * w.a00 ∧
  v.a00 * w.a10 = v.a10 * w.a00 ∧
  v.a00 * w.a11 = v.a11 * w.a00 ∧
  v.a01 * w.a10 = v.a10 * w.a01 ∧
  v.a01 * w.a11 = v.a11 * w.a01 ∧
  v.a10 * w.a11 = v.a11 * w.a10

/-- Single-qubit Clifford + S gate set, as a closed inductive type — this
is what a level's player picks from via `use [...]`. -/
inductive Gate1 where
  | H | X | Z | S
deriving DecidableEq, Repr

def applyGate1 (g : Gate1) (v : Qubit1) : Qubit1 :=
  match g with
  | .H => ⟨v.a0 + v.a1, v.a0 - v.a1⟩
  | .X => ⟨v.a1, v.a0⟩
  | .Z => ⟨v.a0, -v.a1⟩
  | .S => ⟨v.a0, GRat.i * v.a1⟩

def applyAll1 (gs : List Gate1) (v : Qubit1) : Qubit1 :=
  gs.foldl (fun acc g => applyGate1 g acc) v

/-- Two-qubit gates needed for the entangling level: H on qubit 0 only
(tensored with identity on qubit 1), and CNOT with qubit 0 as control. -/
def tensor1 (q r : Qubit1) : Qubit2 :=
  ⟨q.a0 * r.a0, q.a0 * r.a1, q.a1 * r.a0, q.a1 * r.a1⟩

def applyH0 (v : Qubit2) : Qubit2 :=
  -- H on the control qubit only: mixes the (a00,a01) block with the
  -- (a10,a11) block the same way applyGate1 .H mixes a0 with a1.
  ⟨v.a00 + v.a10, v.a01 + v.a11, v.a00 - v.a10, v.a01 - v.a11⟩

def applyCNOT (v : Qubit2) : Qubit2 :=
  -- Flip the target bit whenever the control bit is 1: swap the
  -- a10/a11 block.
  ⟨v.a00, v.a01, v.a11, v.a10⟩

/-! ## The seven Clifford-world levels, each as an existence claim: "there
is a gate sequence taking the start state to (a state proportional to)
the target." This is what makes these real puzzles rather than fixed
verifications — the player supplies the witness list via `use`. -/

def zeroState : Qubit1 := ⟨1, 0⟩
def oneState : Qubit1 := ⟨0, 1⟩

theorem level01_h_squared :
    ∃ gs : List Gate1, prop1 (applyAll1 gs zeroState) zeroState := by
  exact ⟨[.H, .H], by decide⟩

theorem level02_x_squared :
    ∃ gs : List Gate1, prop1 (applyAll1 gs zeroState) zeroState := by
  exact ⟨[.X, .X], by decide⟩

theorem level03_hxh_is_z :
    ∃ gs : List Gate1, prop1 (applyAll1 gs oneState) (applyGate1 .Z oneState) := by
  exact ⟨[.H, .X, .H], by decide⟩

theorem level04_hzh_is_x :
    ∃ gs : List Gate1, prop1 (applyAll1 gs zeroState) (applyGate1 .X zeroState) := by
  exact ⟨[.H, .Z, .H], by decide⟩

theorem level05_s_squared :
    ∃ gs : List Gate1, prop1 (applyAll1 gs oneState) (applyGate1 .Z oneState) := by
  exact ⟨[.S, .S], by decide⟩

/-- Target for the interference level: (|0> - |1>)/sqrt(2), represented
unnormalized as (1, -1) since only direction matters here. -/
def minusState : Qubit1 := ⟨1, -1⟩

theorem level06_interference :
    ∃ gs : List Gate1, prop1 (applyAll1 gs zeroState) minusState := by
  exact ⟨[.X, .H], by decide⟩

def bellTarget : Qubit2 := ⟨1, 0, 0, 1⟩

theorem level07_bell_state :
    prop2 (applyCNOT (applyH0 (tensor1 zeroState zeroState))) bellTarget := by
  decide

/-! ## Player-facing tactic

`use` (Mathlib) isn't available here — this project deliberately has no
Mathlib dependency (see the module docstring above). `useGates` is a
minimal replacement: given a candidate gate list, it reduces the
existential goal to the remaining decidable equality, exactly like
Mathlib's `use` would, without pulling in Mathlib. -/
macro "useGates" gs:term : tactic => `(tactic| refine ⟨$gs, ?_⟩)
