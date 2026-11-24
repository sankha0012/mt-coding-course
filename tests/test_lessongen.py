import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from lessongen import emit, w  # noqa: E402


def roundtrip(tmp_path, steps, thoughts=None):
    path = tmp_path / "lesson.yaml"
    emit(path, "t-01", "A title", "py", steps, thoughts)
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_a_lesson_round_trips_through_yaml(tmp_path):
    steps = [
        {"kind": "give", "lang": "python", "new": ["a"], "text": "One.\n\n```python\nprint(1)\n```\n\nRun it.",
         "shows": ["print(1)", "x = 1\nprint(x)"], "after_run": "Done: yes.", "note": "A \"quoted\" note: with a colon"},
        {"kind": "ask", "lang": "python", "requires": ["a"], "text": "Write f.", "check": "print(f(2))\nprint(f(3))",
         "model": "def f(x):\n    return x * 2", "output": "4\n6", "narration": ["a: b", "", "São Paulo"],
         "wrong": [w("def f(x):\n    return x", ask="Plus?", why="because", lang="python"),
                   w("SELECT 1", tell="plain", lang="sql")],
         "walk": ["one", "two"],
         "return": {"text": "Write g.", "check": "print(g(2))", "model": "def g(x):\n    return x * 3",
                    "narration": ["r1", "r2"]}},
    ]
    got = roundtrip(tmp_path, steps, {"a": "text a", "b": {"text": "text b", "grade": "shape"}})
    assert got["thoughts"] == {"a": "text a", "b": {"text": "text b", "grade": "shape"}}
    first, second = got["steps"]
    assert first["text"] == steps[0]["text"] and first["shows"] == steps[0]["shows"]
    assert first["note"] == steps[0]["note"]
    assert second["model"] == steps[1]["model"] and second["check"] == steps[1]["check"]
    assert second["narration"] == steps[1]["narration"]
    assert second["wrong"][0] == {"code": "def f(x):\n    return x", "ask": "Plus?", "why": "because"}
    assert second["wrong"][1] == {"sql": "SELECT 1", "tell": "plain"}
    assert second["return"]["model"] == steps[1]["return"]["model"]


def test_an_unknown_field_is_refused(tmp_path):
    import pytest
    with pytest.raises(ValueError, match="notafield"):
        roundtrip(tmp_path, [{"kind": "give", "notafield": 1}])
