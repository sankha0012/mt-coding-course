import pytest

from checker.checks import check_all, check_returns, check_shapes, check_sql
from checker.env import Env


@pytest.fixture
def env(data_dir):
    return Env(data_dir=data_dir)


def ask(**fields):
    return {"kind": "ask", "lang": "python", "narration": ["a", "b"], **fields}


def has(fails, text):
    return any(text in f for f in fails)


def sql(env, steps):
    return check_sql(env, "t-01", steps)


def test_a_python_step_that_passes(env):
    steps = [ask(model="print(1 + 1)", output="2", wrong=[{"code": "print(3)", "ask": "q"}])]
    assert sql(env, steps) == []


def test_a_python_model_that_does_not_run(env):
    fails = sql(env, [ask(model="print(y)")])
    assert has(fails, "FAIL t-01 step 1: model answer does not run: line 1: NameError: name 'y' is not defined")


def test_a_python_model_that_prints_nothing(env):
    assert has(sql(env, [ask(model="x = 1")]), "step 1: model answer prints nothing")


def test_the_expected_output_must_match(env):
    assert has(sql(env, [ask(model="print(5)", output="6")]), "step 1: model output")


def test_a_wrong_answer_with_the_same_output_fails(env):
    steps = [ask(model="print(2)", wrong=[{"code": "print(1 + 1)", "ask": "q"}])]
    assert has(sql(env, steps), "step 1: wrong answer gives the model output: print(1 + 1)")


def test_a_wrong_answer_that_errors_is_fine(env):
    assert sql(env, [ask(model="print(2)", wrong=[{"code": "print(", "ask": "q"}])]) == []


def test_a_hidden_check_is_added_after_the_learners_code(env):
    steps = [ask(model="def f(x):\n    return x * 2", check="print(f(3))", output="6",
                 wrong=[{"code": "def f(x):\n    return x + 2", "ask": "q"}])]
    assert sql(env, steps) == []
    steps[0]["wrong"] = [{"code": "def f(x):\n    return x + 3", "ask": "q"}]
    assert has(sql(env, steps), "wrong answer gives the model output")


def test_a_shown_program_runs_without_the_check(env):
    steps = [{"kind": "give", "lang": "python", "text": "t", "shows": ["print('hi')"], "check": "boom("}]
    assert sql(env, steps) == []


def test_python_reads_the_csv_files_of_the_data_folder(env):
    steps = [ask(model="import csv\nprint(len(list(csv.DictReader(open('couriers.csv')))))", output="200")]
    assert sql(env, steps) == []


def test_a_step_can_name_another_data_folder(env, tmp_path):
    (tmp_path / "tiny").mkdir()
    (tmp_path / "tiny" / "t.csv").write_text("a,b\n1,2\n3,4\n")
    env = Env(data_dir=tmp_path)
    py = ask(model="print(open('t.csv').read().count(chr(10)))", output="3", data="tiny")
    sq = {"kind": "ask", "model": "SELECT COUNT(*) FROM t", "rows": 1, "result": [[2]], "data": "tiny",
          "narration": ["a", "b"]}
    assert sql(env, [py, sq]) == []


def test_a_missing_data_folder_is_an_error_not_a_crash(env):
    fails = sql(env, [ask(model="print(1)", data="nowhere")])
    assert has(fails, "step 1: model answer does not run: The data folder was not found")


def test_a_python_return_inherits_the_language(env):
    step = ask(model="print(1 + 1)", **{"return": {"text": "t", "model": "print(2 + 2)", "narration": ["a", "b"]}})
    assert check_returns(env, "t-01", [step]) == []


def test_a_python_return_with_the_same_output_fails(env):
    step = ask(model="print(2)", **{"return": {"text": "t", "model": "print(1 + 1)", "narration": ["a", "b"]}})
    assert has(check_returns(env, "t-01", [step]), "step 1: return: gives the same result as the step's answer")


def test_python_answers_that_differ_in_one_place_repeat_a_shape():
    a, b = ask(model="print(len(fees))"), ask(model="print(len(prices))")
    assert has(check_shapes([("t-01", [a, b])]), "step 2: same shape as step 1")


def test_python_answers_that_differ_in_two_places_do_not():
    a, b = ask(model="print(len(fees))"), ask(model="print(sum(prices))")
    assert check_shapes([("t-01", [a, b])]) == []


def test_a_python_step_and_an_sql_step_never_repeat_a_shape():
    a = ask(model="print(1)")
    b = {"kind": "ask", "model": "SELECT 1", "narration": ["a", "b"]}
    assert check_shapes([("t-01", [a, b])]) == []


def test_a_lesson_whose_data_is_missing_is_skipped_with_a_warning(env):
    steps = [ask(model="print(y)", data="real/not-here")]
    fails, warns, *_ = check_all(env, {}, [("t-01", steps)])
    assert not has(fails, "does not run")
    assert warns[0] == "WARN t-01: the data folder 'real/not-here' was not found, so its answers were not run"


def test_a_python_return_needs_its_own_check_if_its_step_has_one(env):
    step = ask(model="def f(x):\n    return x", check="print(f(1))",
               **{"return": {"text": "t", "model": "def g(x):\n    return x", "narration": ["a", "b"]}})
    assert has(check_returns(env, "t-01", [step]), "step 1: return: needs its own check, because its step has one")
    step["return"]["check"] = "print(g(2))"
    assert check_returns(env, "t-01", [step]) == []
