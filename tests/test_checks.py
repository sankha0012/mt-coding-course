from checker.checks import check_audit, check_narration, check_new_limit, check_shapes, check_sql


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


def audit(thoughts, steps):
    return check_audit(thoughts, [("t-01", steps)])


def test_good_lesson_passes_audit(thoughts, steps):
    assert audit(thoughts, steps) == []


def test_requiring_a_thought_never_introduced(thoughts, steps):
    steps[3]["requires"] = ["star", "keep-rows"]
    assert has(audit(thoughts, steps), "FAIL t-01 step 4: requires 'keep-rows', which no earlier step introduces")


def test_requiring_a_thought_introduced_later(thoughts, steps):
    steps[1]["requires"] = ["count-rows", "from-table", "star"]
    assert has(audit(thoughts, steps), "step 2: requires 'star'")


def test_unknown_thought_id(thoughts, steps):
    steps[3]["requires"] = ["nonsense"]
    assert has(audit(thoughts, steps), "step 4: unknown thought 'nonsense'")


def test_thought_introduced_twice(thoughts, steps):
    steps[2]["new"] = ["count-rows"]
    assert has(audit(thoughts, steps), "step 3: thought 'count-rows' already introduced at t-01 step 1")


def test_an_import_counts_as_introduced(thoughts, steps):
    steps[0]["imports"] = ["compare-signs"]
    steps[3]["requires"] = ["star", "compare-signs"]
    assert audit(thoughts, steps) == []


def test_a_thought_from_an_earlier_lesson_counts(thoughts, steps):
    later = [{"kind": "ask", "requires": ["star"], "text": "t", "model": "SELECT * FROM couriers",
              "narration": ["a", "b"]}]
    assert check_audit(thoughts, [("t-01", steps), ("t-02", later)]) == []


def test_at_most_one_new_thought_per_step(steps):
    steps[2]["new"] = ["star", "keep-rows"]
    assert has(check_new_limit([("t-01", steps)]),
               "FAIL t-01 step 3: introduces 2 new thoughts (star, keep-rows), at most one allowed")


def test_imports_do_not_count_towards_the_limit(steps):
    steps[2]["imports"] = ["compare-signs", "keep-rows"]
    assert check_new_limit([("t-01", steps)]) == []


def shapes(steps):
    return check_shapes([("t-01", steps)])


def test_good_lesson_has_no_shape_repeat(steps):
    assert shapes(steps) == []


def test_answers_differing_in_one_place_repeat_a_shape(steps):
    steps[3]["model"] = "SELECT COUNT(*) FROM orders"
    assert has(shapes(steps), "FAIL t-01 step 4: same shape as step 2")


def test_identical_answers_repeat_a_shape(steps):
    steps[3]["model"] = steps[1]["model"]
    assert has(shapes(steps), "step 4: same shape as step 2")


def test_case_and_spacing_are_ignored(steps):
    steps[3]["model"] = "select  count(*)  from restaurants"
    assert has(shapes(steps), "step 4: same shape as step 2")


def test_two_changes_are_not_a_repeat(steps):
    steps[3]["model"] = "SELECT * FROM restaurants WHERE city = 'Curitiba'"
    assert shapes(steps) == []


def test_steps_without_a_model_are_skipped(steps):
    steps.insert(2, {"kind": "aside", "text": "t"})
    assert shapes(steps) == []
    steps[4]["model"] = "SELECT COUNT(*) FROM orders"
    assert has(shapes(steps), "step 5: same shape as step 2")
