import pytest


def texts(items):
    return [i["text"] for i in items if i["type"] == "teacher"]


def kinds(items):
    return [i["type"] for i in items]


def test_a_lesson_opens_with_the_first_step(make_engine):
    e = make_engine()
    st, items, events = e.start()
    assert items == [{"type": "teacher", "text": "Welcome."}]
    assert e.pending(st) == {"mode": "run", "sql": "SELECT COUNT(*) FROM orders"}
    assert events == []


def test_running_the_shown_sentence_then_continuing(make_engine):
    e = make_engine()
    st, _, _ = e.start()
    st, items, events = e.advance(st)
    assert kinds(items) == ["learner", "result", "teacher"]
    assert items[0]["sql"] == "SELECT COUNT(*) FROM orders"
    assert items[1]["rows"] == [[6000]]
    assert items[2]["text"] == "6,000 orders."
    assert e.pending(st) == {"mode": "continue"}
    st, items, _ = e.advance(st)
    assert items == [{"type": "teacher", "text": "How many restaurants?"}]
    assert e.pending(st) == {"mode": "answer", "step": 2, "variant": "main"}


def test_aside_and_recap_carry_a_style(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, items, _ = e.answer(st, "SELECT COUNT(*) FROM restaurants")
    st, items, _ = e.advance(st)
    assert items == [{"type": "teacher", "text": "An aside.", "style": "aside"}]
    st, items, _ = e.advance(st)
    assert items == [{"type": "teacher", "text": "A recap.", "style": "recap"}]


def test_a_correct_answer_shows_the_work_and_one_narration_line(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, items, events = e.answer(st, "SELECT COUNT(*) FROM restaurants")
    assert kinds(items)[:2] == ["learner", "result"]
    assert items[1]["rows"] == [[60]]
    assert texts(items)[0] in ("N1", "N2", "N3")
    assert e.pending(st) == {"mode": "continue"}
    assert events == [{"step": 2, "variant": "main", "typed": "SELECT COUNT(*) FROM restaurants",
                       "outcome": "correct", "misses": 0}]


def test_narration_is_never_the_same_text_twice_in_a_row(make_engine, reach):
    for seed in range(20):
        e = make_engine(seed=seed)
        st = reach(e, 2)
        st["last_narration"] = "N1"
        st, items, _ = e.answer(st, "SELECT COUNT(*) FROM restaurants")
        assert texts(items)[0] in ("N2", "N3")
        assert st["last_narration"] == texts(items)[0]


def test_an_empty_narration_line_says_nothing(make_engine, reach, play_steps):
    play_steps[1]["narration"] = ["", ""]
    e = make_engine(play_steps)
    st = reach(e, 2)
    st, items, _ = e.answer(st, "SELECT COUNT(*) FROM restaurants")
    assert kinds(items) == ["learner", "result"]


def test_a_difference_in_looks_only_is_simply_correct(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, items, events = e.answer(st, "select  count(*) from restaurants;")
    assert "compare" not in kinds(items)
    assert events[0]["outcome"] == "correct"
    assert e.pending(st) == {"mode": "continue"}


def test_double_quotes_are_correct_not_a_miss(make_engine, reach, play_steps):
    play_steps[4]["model"] = "SELECT * FROM couriers WHERE vehicle = 'bike'"
    e = make_engine(play_steps)
    st = reach(e, 5)
    st, items, events = e.answer(st, 'SELECT * FROM couriers WHERE vehicle = "bike"')
    assert events[0]["outcome"] == "correct" and "compare" not in kinds(items)


def test_a_different_sentence_with_the_same_result_is_correct(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, items, events = e.answer(st, "SELECT COUNT(*) FROM restaurants WHERE restaurant_id > 0")
    assert events[0]["outcome"] == "correct"


def test_column_order_follows_the_step_flags(make_engine, reach, play_steps):
    play_steps[1].update(model="SELECT city, COUNT(*) FROM restaurants GROUP BY city")
    e = make_engine(play_steps)
    st = reach(e, 2)
    _, _, events = e.answer(st, "SELECT COUNT(*), city FROM restaurants GROUP BY city")
    assert events[0]["outcome"] == "miss"
    play_steps[1]["any_column_order"] = True
    e = make_engine(play_steps)
    st = reach(e, 2)
    _, _, events = e.answer(st, "SELECT COUNT(*), city FROM restaurants GROUP BY city")
    assert events[0]["outcome"] == "correct"


def test_accepts_are_correct_too(make_engine, reach, play_steps):
    play_steps[1]["accepts"] = ["SELECT COUNT(*), 1 FROM restaurants"]
    e = make_engine(play_steps)
    st = reach(e, 2)
    _, _, events = e.answer(st, "SELECT COUNT(*), 1 FROM restaurants")
    assert events[0]["outcome"] == "correct"


def test_answering_when_not_waiting_is_an_error(make_engine):
    e = make_engine()
    st, _, _ = e.start()
    with pytest.raises(ValueError):
        e.answer(st, "SELECT 1")


def miss(e, st, text="SELECT 1"):
    st, items, events = e.answer(st, text)
    assert events[0]["outcome"] == "miss"
    return st, items, events


def test_first_miss_asks_again_and_adds_the_thinking_order_version(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, items, events = miss(e, st)
    assert kinds(items) == ["learner", "result", "teacher", "teacher"]
    assert items[2]["text"] in ("AGAIN-1", "AGAIN-2")
    assert items[3]["text"] == "From restaurants, how many?"
    assert events == [{"step": 2, "variant": "main", "typed": "SELECT 1", "outcome": "miss", "misses": 0}]
    assert e.pending(st) == {"mode": "answer", "step": 2, "variant": "main"}


def test_a_step_with_no_thinking_order_just_asks_again(make_engine, reach):
    e = make_engine()
    st = reach(e, 5)
    st, items, _ = miss(e, st)
    assert kinds(items) == ["learner", "result", "teacher"]


def test_second_miss_that_matches_a_known_wrong_answer_asks_its_question(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, items, events = miss(e, st, "SELECT COUNT(*) restaurants")
    assert texts(items) == ["From where?"]
    assert st["why"] == "without from there is no table."
    assert events[0]["misses"] == 1


def test_the_why_is_stated_after_the_learner_gets_it_right(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, _, _ = miss(e, st, "SELECT COUNT(*) restaurants")
    st, items, events = e.answer(st, "SELECT COUNT(*) FROM restaurants")
    assert texts(items)[0] == "Without from there is no table."
    assert texts(items)[1] in ("N1", "N2", "N3")
    assert events[0]["outcome"] == "correct" and events[0]["misses"] == 2


def test_a_tell_is_said_when_there_is_no_question(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, items, _ = miss(e, st, "SELECT COUNT(restaurants)")
    assert texts(items) == ["Tell line."]


def test_a_known_wrong_answer_matches_by_result(make_engine, reach, play_steps):
    play_steps[1]["wrong"] = [{"sql": "SELECT COUNT(*) FROM couriers", "ask": "Wrong table?"}]
    e = make_engine(play_steps)
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, items, _ = miss(e, st, "SELECT COUNT(*) FROM couriers WHERE courier_id > 0")
    assert texts(items) == ["Wrong table?"]


def test_second_miss_that_matches_nothing_goes_to_the_walk(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, items, _ = miss(e, st, "SELECT 2")
    assert texts(items)[0].startswith(("WALK-1", "WALK-2"))
    assert "1. Piece one." in texts(items)[0] and "2. Piece two." in texts(items)[0]


def test_a_miss_after_a_question_goes_to_the_walk(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, _, _ = miss(e, st, "SELECT COUNT(*) restaurants")
    st, items, _ = miss(e, st)
    assert "1. Piece one." in texts(items)[0]


def test_a_miss_after_the_walk_shows_the_answer_to_type(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, _, _ = miss(e, st, "SELECT 2")
    st, items, _ = miss(e, st)
    assert texts(items)[0].startswith(("SHOW-1", "SHOW-2"))
    assert "```sql\nSELECT COUNT(*) FROM restaurants\n```" in texts(items)[0]
    st, items, events = miss(e, st)
    assert "```sql" in texts(items)[0]
    assert e.pending(st)["mode"] == "answer"


def test_a_repeat_miss_after_the_answer_is_shown_points_at_the_piece_that_differs(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, _, _ = miss(e, st, "SELECT 2")
    st, shown, _ = miss(e, st)
    assert not any(t.startswith("DIFF") for t in texts(shown))
    st, again, _ = e.answer(st, "SELECT COUNT(*) FROM restaurant")
    assert texts(again)[-1] == "DIFF yours=restaurant usual=restaurants"
    assert not any("wrong" in t.lower() for t in texts(again))


def test_a_repeat_miss_with_a_missing_piece_says_so(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, _, _ = miss(e, st, "SELECT 2")
    st, _, _ = miss(e, st)
    st, again, _ = e.answer(st, "SELECT COUNT(*) restaurants")
    assert texts(again)[-1] == "DIFF yours=(nothing) usual=FROM"


def test_an_exact_known_wrong_answer_beats_an_earlier_one_with_the_same_result(make_engine, reach, play_steps):
    play_steps[1]["wrong"] = [
        {"sql": "SELECT COUNT(*) FROM restaurants WHERE city = 'x'", "ask": "FIRST"},
        {"sql": "SELECT COUNT(*) FROM restaurants WHERE cuisine = 'y'", "ask": "SECOND"}]
    e = make_engine(play_steps)
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, items, _ = e.answer(st, "SELECT COUNT(*) FROM restaurants WHERE cuisine = 'y'")
    assert texts(items)[-1] == "SECOND"


def test_with_no_walk_the_ladder_goes_from_again_to_the_answer(make_engine, reach):
    e = make_engine()
    st = reach(e, 5)
    st, _, _ = miss(e, st)
    st, items, _ = miss(e, st)
    assert texts(items)[0].startswith(("SHOW-1", "SHOW-2"))


def test_the_ladder_wording_changes_between_uses(make_engine, reach):
    e = make_engine(seed=3)
    st = reach(e, 5)
    st, a, _ = miss(e, st)
    st["rung"] = 0
    st, b, _ = miss(e, st)
    assert texts(a)[0] != texts(b)[0]


def test_the_ladder_never_says_wrong(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    seen = []
    for text in ["SELECT 1", "SELECT COUNT(*) restaurants", "SELECT 3", "SELECT 4"]:
        st, items, _ = e.answer(st, text)
        seen += texts(items)
    assert not any("wrong" in t.lower() for t in seen)


def finish_step(e, st, text):
    st, items, events = e.answer(st, text)
    return st, items, events


def test_a_step_missed_once_is_queued_for_a_return(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, _, events = finish_step(e, st, "SELECT COUNT(*) FROM restaurants")
    assert st["queue"] == [{"step": 1, "due": 4}]


def test_a_step_right_the_first_time_is_not_queued(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, _, _ = finish_step(e, st, "SELECT COUNT(*) FROM restaurants")
    assert st["queue"] == []


def test_a_step_without_a_return_block_is_not_queued(make_engine, reach):
    e = make_engine()
    st = reach(e, 5)
    st, _, _ = miss(e, st)
    st, _, _ = finish_step(e, st, "SELECT * FROM couriers")
    assert st["queue"] == []


def test_the_return_plays_three_steps_later(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, _, _ = finish_step(e, st, "SELECT COUNT(*) FROM restaurants")
    st, items, _ = e.advance(st)
    assert texts(items) == ["An aside."]
    st, items, _ = e.advance(st)
    assert texts(items) == ["A recap."]
    st, items, _ = e.advance(st)
    assert texts(items) == ["How many couriers?"]
    assert e.pending(st) == {"mode": "answer", "step": 2, "variant": "return"}
    assert st["queue"] == [] and st["returned"] == [1]


def test_a_correct_return_uses_the_returns_narration_and_then_the_waiting_step(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, _, _ = finish_step(e, st, "SELECT COUNT(*) FROM restaurants")
    st = reach(e, 2, "return", st)
    st, items, events = finish_step(e, st, "SELECT COUNT(*) FROM couriers")
    assert texts(items)[0] in ("R1", "R2")
    assert events == [{"step": 2, "variant": "return", "typed": "SELECT COUNT(*) FROM couriers",
                       "outcome": "correct", "misses": 0}]
    st, items, _ = e.advance(st)
    assert texts(items) == ["Show couriers."]
    assert e.pending(st) == {"mode": "answer", "step": 5, "variant": "main"}


def test_a_missed_return_asks_again_once_then_shows_the_answer_and_is_not_queued_again(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, _, _ = miss(e, st)
    st, _, _ = finish_step(e, st, "SELECT COUNT(*) FROM restaurants")
    st = reach(e, 2, "return", st)
    st, items, _ = miss(e, st)
    assert texts(items)[0] in ("AGAIN-1", "AGAIN-2")
    st, items, _ = miss(e, st)
    assert "```sql\nSELECT COUNT(*) FROM couriers\n```" in texts(items)[0]
    st, items, events = finish_step(e, st, "SELECT COUNT(*) FROM couriers")
    assert events[0]["outcome"] == "correct" and events[0]["variant"] == "return"
    assert st["queue"] == []


def test_queued_returns_all_play_before_the_cold_check(make_engine, reach):
    e = make_engine()
    st = reach(e, 6)
    st, _, _ = miss(e, st)
    st, _, _ = finish_step(e, st, "SELECT COUNT(*) FROM orders")
    assert st["queue"] == [{"step": 5, "due": 8}]
    st, items, _ = e.advance(st)
    assert texts(items) == ["Count customers rows."]
    assert e.pending(st) == {"mode": "answer", "step": 6, "variant": "return"}
    st, _, _ = finish_step(e, st, "SELECT COUNT(*) FROM restaurants WHERE 1 = 1")
    st, items, _ = e.advance(st)
    assert texts(items) == ["Cold."]


def test_the_cold_check_is_never_laddered_or_narrated(make_engine, reach):
    e = make_engine()
    st = reach(e, 7)
    st, items, events = e.answer(st, "SELECT 1")
    assert kinds(items) == ["learner", "result", "result", "teacher"]
    assert items[1]["label"] == "Yours" and items[2]["label"] == "Model"
    assert items[2]["rows"] == [[60]]
    assert items[3]["text"] == "Closing."
    assert events == [{"step": 7, "variant": "main", "typed": "SELECT 1", "outcome": "shown", "misses": 0}]
    assert e.pending(st) == {"mode": "continue"}
    st, items, _ = e.advance(st)
    assert items == [] and e.pending(st) == {"mode": "done"}


def test_the_cold_check_shows_a_sentence_that_fails_calmly(make_engine, reach):
    e = make_engine()
    st = reach(e, 7)
    st, items, _ = e.answer(st, "SELECT * FROM nowhere")
    assert items[1]["error"] == "no such table: nowhere"


def test_returns_still_waiting_at_the_end_of_a_lesson_with_no_cold_check_play_before_done(make_engine, reach, play_steps):
    e = make_engine(play_steps[:6])
    st = reach(e, 6)
    st, _, _ = miss(e, st)
    st, _, _ = finish_step(e, st, "SELECT COUNT(*) FROM orders")
    st, items, _ = e.advance(st)
    assert e.pending(st) == {"mode": "answer", "step": 6, "variant": "return"}
    st, _, _ = finish_step(e, st, "SELECT COUNT(*) FROM restaurants WHERE 1 = 1")
    st, items, _ = e.advance(st)
    assert e.pending(st) == {"mode": "done"}


def test_solves_is_true_only_for_code_the_step_would_accept(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    assert e.solves(st, "SELECT COUNT(*) FROM restaurants") is True
    assert e.solves(st, "select count(*)  from restaurants;") is True
    assert e.solves(st, "SELECT COUNT(*) FROM couriers") is False
    assert e.solves(st, "SELECT") is False
    assert e.solves(e.start()[0], "SELECT COUNT(*) FROM restaurants") is False  # not waiting for an answer


def test_solves_does_not_change_the_state(make_engine, reach):
    import copy
    e = make_engine()
    st = reach(e, 2)
    before = copy.deepcopy(st)
    e.solves(st, "SELECT COUNT(*) FROM restaurants")
    assert st == before
