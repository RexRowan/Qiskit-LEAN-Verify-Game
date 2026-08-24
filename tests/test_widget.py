"""
Tests for GameShell / LevelWidget that exercise the actual ipywidgets
Button.click() path, not just the internal grading logic — this is the
part that was untested before ("does clicking the button do the right
thing"), as opposed to test_levels.py / test_grader.py which only test
the logic those clicks eventually call.
"""

from qiskit_lean_verify_game.levels import get_level
from qiskit_lean_verify_game.widget import GameShell, LevelWidget


def _click(button):
    """Fire a button's registered on_click handlers directly. Equivalent
    to what ipywidgets does internally when a real UI click arrives, but
    doesn't require a running frontend/kernel."""
    for handler in button._click_handlers.callbacks:
        handler(button)


def test_level_widget_gate_clicks_build_expected_circuit():
    level = get_level("level07_bell_state")
    lw = LevelWidget(level)

    gate_buttons = {b.description: b for b in lw.ui.children[1].children}
    _click(gate_buttons["H"])
    _click(gate_buttons["CNOT"])

    assert lw.moves == [("H", 0), ("CNOT", 0, 1)]


def test_level_widget_reset_clears_moves():
    level = get_level("level01_h_squared")
    lw = LevelWidget(level)
    gate_buttons = {b.description: b for b in lw.ui.children[1].children}

    _click(gate_buttons["H"])
    assert lw.moves == [("H", 0)]

    _click(gate_buttons["Reset"])
    assert lw.moves == []


def test_level_widget_check_click_triggers_on_solved_when_correct():
    level = get_level("level01_h_squared")
    solved = []
    lw = LevelWidget(level, on_solved=lambda: solved.append(True))
    gate_buttons = {b.description: b for b in lw.ui.children[1].children}

    _click(gate_buttons["H"])
    _click(gate_buttons["H"])
    _click(gate_buttons["Check"])

    assert solved == [True]


def test_level_widget_check_click_does_not_fire_on_solved_when_wrong():
    level = get_level("level01_h_squared")
    solved = []
    lw = LevelWidget(level, on_solved=lambda: solved.append(True))
    gate_buttons = {b.description: b for b in lw.ui.children[1].children}

    _click(gate_buttons["H"])  # only one H — wrong, H^2 = I needs two
    _click(gate_buttons["Check"])

    assert solved == []


def test_game_shell_starts_on_first_level():
    shell = GameShell()
    assert shell._active_level_id == shell.levels[0].id


def test_game_shell_level_button_switches_active_level():
    shell = GameShell()
    second_level = shell.levels[1]
    _click(shell.level_buttons[second_level.id])
    assert shell._active_level_id == second_level.id
    assert shell.active_widget.level.id == second_level.id


def test_game_shell_marks_level_solved_end_to_end():
    shell = GameShell()
    first_level = shell.levels[0]  # level01_h_squared: reference solution H, H
    assert first_level.id not in shell.solved

    gate_buttons = {b.description: b for b in shell.active_widget.ui.children[1].children}
    for move in first_level.reference_solution:
        _click(gate_buttons[move[0]])
    _click(gate_buttons["Check"])

    assert first_level.id in shell.solved
    assert shell.level_buttons[first_level.id].button_style == "success"
