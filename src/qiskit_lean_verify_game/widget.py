"""
widget.py

Jupyter-facing widget: gate buttons that build a real QuantumCircuit move
by move, graded against a Level's target after every move. Same
clear_output() + redraw pattern used in qiskit-sqd-dashboard, rather than
a from-scratch rendering approach.

Import note: ipywidgets and IPython.display are required for this module
specifically (not for the rest of the package — grader.py and levels.py
have no notebook dependency). Import qiskit_lean_verify_game.widget only
inside a Jupyter/IPython environment.
"""

from __future__ import annotations

from typing import Callable

import ipywidgets as widgets
from IPython.display import clear_output, display

from .grader import grade_circuit
from .levels import GATE_LIBRARY, LEVELS, Level, build_circuit


class LevelWidget:
    """A single playable level, rendered as gate buttons + live feedback."""

    def __init__(self, level: Level, on_solved: Callable[[], None] | None = None):
        self.level = level
        self.on_solved = on_solved
        self.moves: list[tuple] = []
        self.output = widgets.Output()
        self._qubit_selectors: dict[str, widgets.Dropdown] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        gate_buttons = []
        for gate_name in self.level.allowed_gates:
            button = widgets.Button(description=gate_name)
            button.on_click(self._make_gate_handler(gate_name))
            gate_buttons.append(button)

        reset_button = widgets.Button(description="Reset", button_style="warning")
        reset_button.on_click(self._on_reset)

        check_button = widgets.Button(description="Check", button_style="success")
        check_button.on_click(self._on_check)

        header = widgets.HTML(
            f"<b>{self.level.title}</b><br>{self.level.goal}"
            + (f"<br><i>Hint: {self.level.hint}</i>" if self.level.hint else "")
        )

        controls = widgets.HBox(gate_buttons + [reset_button, check_button])
        self.ui = widgets.VBox([header, controls, self.output])
        self._render()

    def _make_gate_handler(self, gate_name: str):
        _, arity, _ = GATE_LIBRARY[gate_name]

        def handler(_button):
            if arity == 1:
                # Single-qubit levels in v1 only ever use qubit 0; a
                # multi-qubit single-qubit-gate picker is future work.
                self.moves.append((gate_name, 0))
            else:
                # Two-qubit gate: fixed control=0, target=1 for v1's one
                # entangling level. Generalize when a level needs it.
                self.moves.append((gate_name, 0, 1))
            self._render()

        return handler

    def _on_reset(self, _button) -> None:
        self.moves = []
        self._render()

    def _on_check(self, _button) -> None:
        self._render(show_result=True)

    def _render(self, show_result: bool = False) -> None:
        with self.output:
            clear_output(wait=True)
            try:
                circuit = build_circuit(self.level, self.moves)
            except ValueError as exc:
                print(f"Invalid move sequence: {exc}")
                return
            print(circuit.draw(output="text"))
            if show_result:
                result = grade_circuit(
                    circuit,
                    self.level.target,
                    initial_state=self.level.initial_state,
                    phase_sensitive=self.level.phase_sensitive,
                )
                if result.passed:
                    print("\u2713 PASSED —", result.reason)
                    if self.on_solved is not None:
                        self.on_solved()
                else:
                    print("\u2717 Not yet —", result.reason)

    def show(self) -> None:
        display(self.ui)


class GameShell:
    """Level-select UI: a row of level buttons plus the currently active
    LevelWidget. Clicking a level button swaps which level is shown;
    solved levels get a visible checkmark. This is the click-through-levels
    layer requested on top of individual LevelWidgets — it does not change
    how any single level is graded.
    """

    def __init__(self, levels: list[Level] | None = None):
        self.levels = levels if levels is not None else LEVELS
        if not self.levels:
            raise ValueError("GameShell needs at least one level.")
        self.solved: set[str] = set()
        self.level_buttons: dict[str, widgets.Button] = {}
        self.level_area = widgets.Output()
        self._active_level_id: str | None = None
        self._build_level_buttons()
        self.ui = widgets.VBox([self.button_row, self.level_area])
        self._show_level(self.levels[0])

    def _label(self, level: Level) -> str:
        mark = "\u2713 " if level.id in self.solved else ""
        return f"{mark}{level.title}"

    def _build_level_buttons(self) -> None:
        buttons = []
        for level in self.levels:
            button = widgets.Button(description=self._label(level))
            button.on_click(self._make_level_handler(level))
            self.level_buttons[level.id] = button
            buttons.append(button)
        self.button_row = widgets.HBox(buttons)

    def _make_level_handler(self, level: Level):
        def handler(_button):
            self._show_level(level)

        return handler

    def _mark_solved(self, level_id: str) -> None:
        self.solved.add(level_id)
        level = next(lvl for lvl in self.levels if lvl.id == level_id)
        button = self.level_buttons[level_id]
        button.description = self._label(level)
        button.button_style = "success"

    def _show_level(self, level: Level) -> None:
        self._active_level_id = level.id
        with self.level_area:
            clear_output(wait=True)
            self.active_widget = LevelWidget(
                level, on_solved=lambda lid=level.id: self._mark_solved(lid)
            )
            self.active_widget.show()

    def show(self) -> None:
        display(self.ui)
