from pathlib import Path

from checker.__main__ import main

ROOT = Path(__file__).parent.parent


def test_lesson_1_passes(capsys):
    code = main([str(ROOT / "content" / "sql"), "--data", str(ROOT / "data")])
    out = capsys.readouterr().out
    assert code == 0, out
    assert "0 failures, 2 warnings" in out
