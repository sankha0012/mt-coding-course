import shutil
from pathlib import Path

import yaml

from checker.__main__ import main

ROOT = Path(__file__).parent.parent


def test_lesson_1_passes(capsys):
    code = main([str(ROOT / "content" / "sql"), "--data", str(ROOT / "data")])
    out = capsys.readouterr().out
    assert code == 0, out
    assert "0 failures, 2 warnings" in out


def test_broken_copy_of_lesson_1_fails_with_clear_messages(tmp_path, capsys):
    shutil.copytree(ROOT / "content" / "sql", tmp_path / "sql")
    path = tmp_path / "sql" / "lesson-01.yaml"
    lesson = yaml.safe_load(path.read_text(encoding="utf-8"))
    steps = lesson["steps"]
    steps[6]["model"] = "SELECT COUNT(*) FROM orders WHERE delivry_fee < 5"
    steps[17]["model"] = steps[16]["model"]
    steps[3]["requires"].append("keep-rows")
    path.write_text(yaml.safe_dump(lesson, allow_unicode=True), encoding="utf-8")

    code = main([str(tmp_path / "sql"), "--data", str(ROOT / "data")])
    out = capsys.readouterr().out

    assert code == 1
    assert "FAIL sql-01 step 7: model answer does not run: no such column: delivry_fee" in out
    assert "FAIL sql-01 step 18: same shape as step 17" in out
    assert "FAIL sql-01 step 4: requires 'keep-rows', which no earlier step introduces" in out
