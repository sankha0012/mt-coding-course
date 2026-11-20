from pathlib import Path

import yaml

from player.__main__ import preflight

ROOT = Path(__file__).parent.parent


def test_the_real_lesson_passes_the_startup_check(data_dir):
    assert preflight(ROOT / "content" / "sql", data_dir) == []


def test_a_lesson_that_fails_the_checker_is_reported(tmp_path, data_dir):
    folder = tmp_path / "sql"
    folder.mkdir()
    (folder / "thoughts.yaml").write_text("thoughts: {a: x}\n")
    (folder / "lesson-01.yaml").write_text(yaml.safe_dump({"lesson": "t", "steps": [
        {"kind": "give", "text": "t", "shows": ["SELECT * FROM nowhere"]}]}))
    fails = preflight(folder, data_dir)
    assert fails and fails[0].startswith("FAIL t step 1: shown sentence does not run")
