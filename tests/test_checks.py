from checker.checks import (check_all, check_audit, check_narration, check_new_limit,
                            check_returns, check_shape, check_shapes, check_sql, report_load,
                            report_spacing)


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


def test_spacing_report_lists_returns_and_gaps(thoughts, steps):
    lines = report_spacing(thoughts, [("t-01", steps)])
    assert "star: introduced t-01:3; needed at t-01:4; gaps 1" in lines
    assert "count-rows: introduced t-01:1; needed at t-01:2; gaps 1" in lines
    assert "keep-rows: never introduced" in lines


def test_spacing_report_says_when_a_thought_is_never_needed_again(thoughts, steps):
    steps[3]["requires"] = ["from-table"]
    lines = report_spacing(thoughts, [("t-01", steps)])
    assert "star: introduced t-01:3; never needed again" in lines


def test_load_report_warns_on_three_new_thoughts_in_a_row(steps):
    lines, warns = report_load([("t-01", steps)])
    assert lines == ["t-01: new thoughts at steps 1, 2, 3 (3 in 4)"]
    assert warns == ["WARN t-01 steps 1 to 3: a new thought in each of 3 steps in a row"]


def test_load_report_has_no_warning_when_relief_comes(steps):
    steps[2].pop("new")
    steps[2]["imports"] = ["star"]
    _, warns = report_load([("t-01", steps)])
    assert warns == []


def test_check_all_returns_failures_warnings_and_reports(conn, thoughts, steps):
    fails, warns, spacing, load = check_all(conn, thoughts, [("t-01", steps)])
    assert fails == []
    assert len(warns) == 1
    assert spacing and load
    steps[1]["narration"] = ["one"]
    steps[3]["requires"] = ["keep-rows"]
    fails, *_ = check_all(conn, thoughts, [("t-01", steps)])
    assert has(fails, "step 2: needs at least two") and has(fails, "step 4: requires 'keep-rows'")


def test_changing_the_table_and_adding_a_clause_is_two_changes(steps):
    steps[1]["model"] = "SELECT * FROM couriers"
    steps[3]["model"] = "SELECT * FROM orders WHERE subtotal > 100"
    assert shapes(steps) == []


def test_adding_one_clause_is_a_repeat(steps):
    steps[1]["model"] = "SELECT * FROM couriers"
    steps[3]["model"] = "SELECT * FROM couriers WHERE vehicle = 'bike'"
    assert has(shapes(steps), "step 4: same shape as step 2")


def test_changing_two_things_inside_one_clause_is_one_change(steps):
    steps[1]["model"] = "SELECT * FROM orders WHERE delivery_fee < 5"
    steps[3]["model"] = "SELECT * FROM orders WHERE subtotal > 100"
    assert has(shapes(steps), "step 4: same shape as step 2")


def with_return(steps, **changes):
    """Give step 2 a valid return, then apply changes to it."""
    steps[1]["return"] = {"text": "t", "model": "SELECT COUNT(*) FROM couriers", "rows": 1,
                          "result": [[200]], "narration": ["a", "b"], **changes}
    return steps


def returns(conn, steps):
    return check_returns(conn, "t-01", steps)


def test_steps_without_a_return_pass(conn, steps):
    assert returns(conn, steps) == []


def test_valid_return_passes(conn, steps):
    assert returns(conn, with_return(steps)) == []


def test_return_that_does_not_run(conn, steps):
    with_return(steps, model="SELECT COUNT(*) FROM nowhere")
    assert has(returns(conn, steps), "FAIL t-01 step 2: return: model answer does not run")


def test_return_with_no_rows(conn, steps):
    with_return(steps, model="SELECT * FROM couriers WHERE city = 'Nowhere'")
    del steps[1]["return"]["rows"], steps[1]["return"]["result"]
    assert has(returns(conn, steps), "step 2: return: model answer returns no rows")


def test_return_rows_and_result_must_match(conn, steps):
    with_return(steps, rows=2)
    assert has(returns(conn, steps), "step 2: return: model answer returns 1 rows, expected 2")
    with_return(steps, result=[[201]])
    assert has(returns(conn, steps), "step 2: return: model result")


def test_return_without_a_model(conn, steps):
    steps[1]["return"] = {"text": "t", "narration": ["a", "b"]}
    assert has(returns(conn, steps), "step 2: return: has no model")


def test_return_must_not_be_the_same_sentence(conn, steps):
    with_return(steps, model="select  count(*)  from restaurants", rows=1, result=[[60]])
    assert has(returns(conn, steps), "step 2: return: model is the same sentence as the step's")


def test_return_must_not_give_the_same_result(conn, steps):
    with_return(steps, model="SELECT COUNT(*) FROM restaurants WHERE 1 = 1", rows=1, result=[[60]])
    assert has(returns(conn, steps), "step 2: return: gives the same result as the step's answer")


def test_return_needs_two_narration_lines(conn, steps):
    with_return(steps, narration=["only one", ""])
    assert has(returns(conn, steps), "step 2: return: needs at least two non-empty narration lines, has 1")


def test_cold_check_may_not_have_a_return(conn, steps):
    steps[3]["kind"] = "cold-check"
    steps[3]["return"] = {"text": "t", "model": "SELECT COUNT(*) FROM couriers", "narration": ["a", "b"]}
    assert has(returns(conn, steps), "step 4: return: is not allowed on a cold check")


def test_check_all_includes_the_return_checks(conn, thoughts, steps):
    with_return(steps, model="SELECT COUNT(*) FROM nowhere")
    fails, *_ = check_all(conn, thoughts, [("t-01", steps)])
    assert has(fails, "step 2: return: model answer does not run")


def test_return_accepted_answers_must_run_and_return_rows(conn, steps):
    with_return(steps, accepts=["SELECT * FROM nowhere"])
    assert has(returns(conn, steps), "step 2: return: accepted answer")
    with_return(steps, accepts=["SELECT COUNT(*) FROM couriers WHERE 1 = 1"])
    assert returns(conn, steps) == []


def graded(thoughts):
    return {**thoughts,
            "month": {"text": "cut a date down to its month", "grade": "shape"},
            "rank": {"text": "tied rows share a number", "grade": "name-only"}}


def test_a_step_needing_a_shape_thought_must_list_what_it_supplies(thoughts, steps):
    steps[0]["imports"] = ["month"]
    steps[3]["requires"] = ["star", "from-table", "month"]
    assert has(check_shape(graded(thoughts), [("t-01", steps)]),
               "FAIL t-01 step 4: requires the shape thought 'month', so it must list what it supplies")


def test_what_a_step_supplies_must_be_in_its_text(thoughts, steps):
    steps[0]["imports"] = ["month"]
    steps[3].update(requires=["star", "from-table", "month"], supplies=["strftime('%Y-%m', created_at)"],
                    text="Here it is: strftime('%Y-%m', created_at)")
    assert check_shape(graded(thoughts), [("t-01", steps)]) == []
    steps[3]["text"] = "No spelling here."
    assert has(check_shape(graded(thoughts), [("t-01", steps)]),
               "step 4: supplies \"strftime('%Y-%m', created_at)\" but its text does not contain it")


def test_supplies_are_checked_on_any_step(thoughts, steps):
    steps[1]["supplies"] = ["nonsense"]
    assert has(check_shape(thoughts, [("t-01", steps)]), "step 2: supplies \"nonsense\"")


def test_a_name_only_thought_is_never_asked(thoughts, steps):
    steps[0]["imports"] = ["rank"]
    steps[3]["requires"] = ["star", "from-table", "rank"]
    assert has(check_shape(graded(thoughts), [("t-01", steps)]),
               "step 4: requires the name-only thought 'rank', which is never asked")


def test_plain_string_thoughts_are_core(thoughts, steps):
    assert check_shape(thoughts, [("t-01", steps)]) == []


def test_check_all_includes_the_shape_check(conn, thoughts, steps):
    steps[1]["supplies"] = ["nonsense"]
    fails, *_ = check_all(conn, thoughts, [("t-01", steps)])
    assert has(fails, "step 2: supplies")
