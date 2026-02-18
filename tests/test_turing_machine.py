import pytest
from tm.tape import Tape
from tm.turing_machine import TuringMachine, TransitionTable


# --- Tape tests ---

def test_tape_initialization():
    tape = Tape("abc")
    assert str(tape) == "abc"
    assert len(tape) == 3


def test_tape_blank_symbol():
    tape = Tape("", blank="_")
    assert tape.read(0) == "_"
    assert str(tape) == "_"


def test_tape_read_out_of_bounds():
    tape = Tape("a")
    assert tape.read(5) == "⊔"
    assert tape.read(-1) == "⊔"


def test_tape_write_and_expand():
    tape = Tape("a")
    tape.write(1, "b")
    assert str(tape) == "ab"
    tape.write(5, "z")
    assert tape.read(5) == "z"
    assert len(tape) == 6


def test_tape_repr():
    tape = Tape("xyz")
    assert "<Tape xyz>" in repr(tape)


# --- TransitionTable tests ---

def test_basic_transition_lookup():
    table = TransitionTable({
        "q0": {"a": ("b", "R", "q1")}
    })
    result = table.get("q0", "a")
    assert result == ("b", "R", "q1")


def test_transition_missing_state():
    table = TransitionTable({})
    assert table.get("q0", "a") is None


def test_any_wildcard():
    table = TransitionTable({
        "q0": {"_any_": ("x", "S", "q1")}
    })
    result = table.get("q0", "z")
    assert result == ("x", "S", "q1")


def test_strict_palindrome_table_exists():
    table = TransitionTable.strict_palindrome_table()
    assert "q0" in table.transitions
    assert isinstance(table.transitions, dict)


# --- TuringMachine tests ---

def test_machine_initializes_with_string():
    m = TuringMachine("aba")
    assert m.tape.read(0) == "a"
    assert m.state == "q0"


def test_machine_load_and_reset():
    m = TuringMachine("abc")
    m.load_tape("xyz")
    assert str(m.tape).startswith("xyz")
    assert m.state == "q0"


def test_step_and_halt_behavior():
    table = TransitionTable({
        "q0": {"a": ("a", "R", "q1")},
        "q1": {"⊔": ("⊔", "S", "q_accept")}
    })
    m = TuringMachine(table)
    m.load_tape("a")
    result = m.step()
    assert "Символ:" in result  # обновлённый текст
    assert not m.is_halted()
    m.step()
    assert m.is_halted()
    assert m.state == "q_accept"


def test_reject_if_no_transition():
    table = TransitionTable({"q0": {"a": ("a", "R", "q1")}})
    m = TuringMachine(table)
    m.load_tape("b")
    msg = m.step()
    assert "Нет перехода" in msg
    assert m.state == m.reject_state


def test_run_accepts_palindrome():
    m = TuringMachine("aba")
    result = m.run()
    assert isinstance(result, bool)
    assert m.is_halted()


def test_run_does_not_exceed_max_steps():
    table = TransitionTable({
        "q0": {"_any_": ("_any_", "R", "q0")}  # бесконечный цикл
    })
    m = TuringMachine(table)
    m.load_tape("aaaa")
    m.max_steps = 10
    result = m.run()
    assert not result  # должно быть отклонено по лимиту
    assert m.state == m.reject_state
