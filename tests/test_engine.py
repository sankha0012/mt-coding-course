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


def test_a_slip_shows_both_spellings_and_no_narration(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    st, items, events = e.answer(st, "select  count(*) from restaurants;")
    assert kinds(items) == ["learner", "result", "compare", "teacher"]
    assert items[2] == {"type": "compare", "yours": "select  count(*) from restaurants;",
                        "usual": "SELECT COUNT(*) FROM restaurants"}
    assert items[3]["text"] in ("SLIP-1", "SLIP-2")
    assert events[0]["outcome"] == "slip"
    assert e.pending(st) == {"mode": "continue"}


def test_double_quotes_are_a_slip_not_a_miss(make_engine, reach, play_steps):
    play_steps[4]["model"] = "SELECT * FROM couriers WHERE vehicle = 'bike'"
    e = make_engine(play_steps)
    st = reach(e, 5)
    st, items, events = e.answer(st, 'SELECT * FROM couriers WHERE vehicle = "bike"')
    assert events[0]["outcome"] == "slip"


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
