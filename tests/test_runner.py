import pytest

from player.runner import Runner

SQL = {"lang": "sql"}
PY = {"lang": "python"}


@pytest.fixture
def runner(data_dir):
    return Runner(data_dir)


def test_sql_runs_on_the_data(runner):
    r = runner.run(SQL, "SELECT COUNT(*) FROM couriers")
    assert r.error is None and r.rows == [[200]]


def test_python_shows_what_it_printed(runner):
    r = runner.run(PY, "print(1 + 1)")
    assert r.error is None
    assert r.item() == {"type": "result", "lang": "python", "text": "2\n", "error": None}
    assert r.item("Yours")["label"] == "Yours"


def test_a_hidden_check_judges_but_is_not_shown(runner):
    step = {"lang": "python", "check": "print(double(4))"}
    r = runner.run(step, "def double(x):\n    return x * 2")
    assert r.item()["text"] == "" and r.error is None
    assert r.key({}) == runner.run(step, "def double(x):\n    return x + x").key({})
    assert r.key({}) != runner.run(step, "def double(x):\n    return x + 1").key({})


def test_an_error_in_the_check_is_shown_without_a_line_number(runner):
    step = {"lang": "python", "check": "print(double(4))"}
    r = runner.run(step, "x = 1")
    assert r.error == "NameError: name 'double' is not defined"


def test_an_error_in_the_learners_own_code_keeps_its_line(runner):
    r = runner.run(PY, "x = 1\nprint(y)")
    assert r.error.startswith("line 2: NameError")


def test_a_step_can_name_its_own_data_folder(tmp_path):
    (tmp_path / "tiny").mkdir()
    (tmp_path / "tiny" / "t.csv").write_text("a,b\n1,2\n3,4\n")
    runner = Runner(tmp_path)
    assert runner.run({"data": "tiny"}, "SELECT SUM(a) FROM t").rows == [[4]]
    assert runner.run({"lang": "python", "data": "tiny"}, "print(open('t.csv').read().count('1'))").item()["text"] == "1\n"


def test_a_missing_data_folder_is_an_error_in_either_language(runner):
    assert "was not found" in runner.run({"data": "nowhere"}, "SELECT 1").error
    assert "was not found" in runner.run({"lang": "python", "data": "nowhere"}, "print(1)").error


def test_play_shows_a_result_and_never_judges(runner):
    assert runner.play("sql", "SELECT 1")["rows"] == [[1]]
    assert runner.play("python", "print('hi')")["text"] == "hi\n"


def test_play_cannot_change_the_core_data(runner, data_dir):
    before = (data_dir / "couriers.csv").read_bytes()
    assert runner.play("sql", "DELETE FROM couriers")["error"] is not None
    assert runner.play("python", "open('couriers.csv', 'w').write('x')")["error"] is not None
    assert (data_dir / "couriers.csv").read_bytes() == before
    assert runner.play("sql", "SELECT COUNT(*) FROM couriers")["rows"] == [[200]]
