from checker.checks import check_narration, check_sql


def has(fails, text):
    return any(text in f for f in fails)


def sql(conn, steps):
    return check_sql(conn, "t-01", steps)


def test_good_lesson_passes_sql_checks(conn, steps):
    assert sql(conn, steps) == []


def test_model_that_does_not_run(conn, steps):
    steps[1]["model"] = "SELECT COUNT(*) FROM restaurant"
    assert has(sql(conn, steps), "FAIL t-01 step 2: model answer does not run: no such table")


def test_model_that_returns_no_rows(conn, steps):
    steps[1]["model"] = "SELECT * FROM restaurants WHERE city = 'Nowhere'"
    del steps[1]["rows"], steps[1]["result"]
    assert has(sql(conn, steps), "step 2: model answer returns no rows")


def test_rows_must_match(conn, steps):
    steps[1]["rows"] = 2
    assert has(sql(conn, steps), "step 2: model answer returns 1 rows, expected 2")


def test_result_must_match(conn, steps):
    steps[1]["result"] = [[61]]
    assert has(sql(conn, steps), "step 2: model result")


def test_shown_sentence_must_run(conn, steps):
    steps[0]["shows"] = ["SELECT COUNT(*) FROM nowhere"]
    assert has(sql(conn, steps), "step 1: shown sentence does not run")


def test_broken_sentence_must_fail(conn, steps):
    steps[0]["broken"] = "SELECT COUNT(*) FROM orders"
    assert has(sql(conn, steps), "step 1: broken sentence runs without error")


def test_accepted_answer_must_run_and_return_rows(conn, steps):
    steps[1]["accepts"] = ["SELECT * FROM nowhere"]
    assert has(sql(conn, steps), "step 2: accepted answer")


def test_wrong_answer_that_matches_model_fails(conn, steps):
    steps[1]["wrong"] = [{"sql": "SELECT COUNT(*) FROM restaurants", "ask": "q"}]
    assert has(sql(conn, steps), "step 2: wrong answer gives the model result")


def test_wrong_answer_that_errors_is_fine(conn, steps):
    steps[1]["wrong"] = [{"sql": "SELECT COUNT(restaurants)", "ask": "q"}]
    assert sql(conn, steps) == []


def test_wrong_answer_needs_ask_or_tell_and_sql(conn, steps):
    steps[1]["wrong"] = [{"sql": "SELECT 1"}, {"ask": "q"}]
    fails = sql(conn, steps)
    assert has(fails, "step 2: wrong answer needs ask or tell: SELECT 1")
    assert has(fails, "step 2: wrong answer has no sql")


def test_any_column_order_applies_to_wrong_answers(conn, steps):
    steps[1].update(model="SELECT city, COUNT(*) FROM restaurants GROUP BY city", rows=4)
    del steps[1]["result"]
    steps[1]["wrong"] = [{"sql": "SELECT COUNT(*), city FROM restaurants GROUP BY city", "ask": "q"}]
    assert not has(sql(conn, steps), "gives the model result")
    steps[1]["any_column_order"] = True
    assert has(sql(conn, steps), "gives the model result")


def test_typed_step_needs_two_narration_lines(steps):
    steps[1]["narration"] = ["only one", ""]
    assert has(check_narration("t-01", steps), "FAIL t-01 step 2: needs at least two non-empty narration lines, has 1")


def test_cold_check_needs_no_narration(steps):
    steps[3]["kind"] = "cold-check"
    del steps[3]["narration"]
    assert check_narration("t-01", steps) == []
