from pathlib import Path

import pytest
import yaml

from checker.data import load_db

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
