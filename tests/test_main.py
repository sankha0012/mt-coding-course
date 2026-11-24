from pathlib import Path

import yaml

from player.__main__ import preflight

ROOT = Path(__file__).parent.parent


def test_the_whole_course_passes_the_startup_check(data_dir):
    assert preflight(ROOT / "content", data_dir) == []


def test_a_lesson_that_fails_the_checker_is_reported(tmp_path, data_dir):
    folder = tmp_path / "sql"
    folder.mkdir()
    (folder / "thoughts.yaml").write_text("thoughts: {a: x}\n")
    (folder / "lesson-01.yaml").write_text(yaml.safe_dump({"lesson": "t", "steps": [
        {"kind": "give", "text": "t", "shows": ["SELECT * FROM nowhere"]}]}))
    fails = preflight(folder, data_dir)
    assert fails and fails[0].startswith("FAIL t step 1: shown sentence does not run")


def test_skip_check_starts_without_running_the_checker(monkeypatch, tmp_path, data_dir, capsys):
    import player.__main__ as m
    calls = []
    monkeypatch.setattr(m, "preflight", lambda *a: calls.append(a) or ["FAIL would have stopped it"])
    monkeypatch.setattr(m.uvicorn, "run", lambda *a, **k: calls.append("served"))
    args = ["--content", str(ROOT / "content"), "--data", str(data_dir), "--progress", str(tmp_path)]
    assert m.main(args) == 1 and calls == [(str(ROOT / "content"), str(data_dir))]
    calls.clear()
    assert m.main(args + ["--skip-check"]) == 0 and calls == ["served"]
