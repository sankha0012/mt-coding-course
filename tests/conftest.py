import random
from pathlib import Path

import pytest
import yaml

from checker.data import load_db
from player.runner import Runner

ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def data_dir():
    return ROOT / "data"


@pytest.fixture(scope="session")
def conn(data_dir):
    return load_db(data_dir)


@pytest.fixture
def thoughts():
    names = ["count-rows", "from-table", "star", "keep-rows", "compare-signs"]
    return {name: f"The thought {name}." for name in names}


@pytest.fixture
def steps():
    """A small lesson that passes every check. Tests change one thing at a time."""
    return [
        {"kind": "give", "new": ["count-rows"], "text": "t",
         "shows": ["SELECT COUNT(*) FROM orders"]},
        {"kind": "ask", "new": ["from-table"], "requires": ["count-rows", "from-table"], "text": "t",
         "model": "SELECT COUNT(*) FROM restaurants", "rows": 1, "result": [[60]],
         "narration": ["a", "b"],
         "wrong": [{"sql": "SELECT COUNT(*) restaurants", "ask": "q"}]},
        {"kind": "give", "new": ["star"], "text": "t", "shows": ["SELECT * FROM orders"]},
        {"kind": "ask", "requires": ["star", "from-table"], "text": "t",
         "model": "SELECT * FROM couriers", "rows": 200, "narration": ["a", "b"]},
    ]


@pytest.fixture
def write_strand(tmp_path, thoughts):
    """Write a thoughts file and one lesson to a temporary folder, return the folder."""
    def write(lesson_steps):
        (tmp_path / "thoughts.yaml").write_text(
            yaml.safe_dump({"thoughts": thoughts}, allow_unicode=True), encoding="utf-8")
        (tmp_path / "lesson-01.yaml").write_text(
            yaml.safe_dump({"lesson": "t-01", "steps": lesson_steps}, allow_unicode=True),
            encoding="utf-8")
        return tmp_path
    return write


@pytest.fixture(scope="session")
def play_runner(data_dir):
    return Runner(data_dir)


@pytest.fixture
def ui():
    return {
        "again": ["AGAIN-1", "AGAIN-2"],
        "walk_intro": ["WALK-1", "WALK-2"],
        "show_answer": ["SHOW-1", "SHOW-2"],
    }


@pytest.fixture
def play_steps():
    """A small lesson that uses every kind of step. Indexes: 0 give, 1 typed with ladder and return,
    2 aside, 3 recap, 4 typed without walk, 5 typed with return, 6 cold check."""
    return [
        {"kind": "give", "text": "Welcome.", "shows": ["SELECT COUNT(*) FROM orders"], "after_run": "6,000 orders."},
        {"kind": "ask", "text": "How many restaurants?", "thinking_order": "From restaurants, how many?",
         "model": "SELECT COUNT(*) FROM restaurants", "narration": ["N1", "N2", "N3"],
         "wrong": [
             {"sql": "SELECT COUNT(*) restaurants", "ask": "From where?", "why": "without from there is no table."},
             {"sql": "SELECT COUNT(restaurants)", "tell": "Tell line."}],
         "walk": ["Piece one.", "Piece two."],
         "return": {"text": "How many couriers?", "model": "SELECT COUNT(*) FROM couriers",
                    "narration": ["R1", "R2"]}},
        {"kind": "aside", "text": "An aside."},
        {"kind": "recap", "text": "A recap."},
        {"kind": "ask", "text": "Show couriers.", "model": "SELECT * FROM couriers", "narration": ["A", "B"]},
        {"kind": "ask", "text": "Count orders.", "model": "SELECT COUNT(*) FROM orders", "narration": ["C", "D"],
         "return": {"text": "Count customers rows.", "model": "SELECT COUNT(*) FROM restaurants WHERE 1 = 1",
                    "narration": ["R3", "R4"]}},
        {"kind": "cold-check", "text": "Cold.", "model": "SELECT COUNT(*) FROM restaurants", "after_run": "Closing."},
    ]


@pytest.fixture
def make_engine(play_runner, ui, play_steps):
    from player.engine import Engine  # imported here so conftest loads before the engine exists

    def make(steps=None, seed=1):
        return Engine(steps if steps is not None else play_steps, play_runner, ui, random.Random(seed))
    return make


@pytest.fixture
def reach():
    """Play an engine up to the point where it waits for an answer to the given step (1-based) and
    variant. Steps on the way are run, continued, and answered correctly with their model answer."""
    def go(engine, step, variant="main", state=None):
        st = state if state else engine.start()[0]
        for _ in range(200):
            p = engine.pending(st)
            if p["mode"] == "answer" and p["step"] == step and p["variant"] == variant:
                return st
            if p["mode"] == "answer":
                s = engine.steps[p["step"] - 1]
                st, *_ = engine.answer(st, (s["return"] if p["variant"] == "return" else s)["model"])
            else:
                assert p["mode"] in ("run", "continue"), p
                st, *_ = engine.advance(st)
        raise AssertionError("never reached the step")
    return go
