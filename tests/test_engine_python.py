def texts(items):
    return [i["text"] for i in items if i["type"] == "teacher"]


def kinds(items):
    return [i["type"] for i in items]


def py_steps():
    return [
        {"kind": "give", "lang": "python", "text": "Run this.", "shows": ["print(1 + 1)"], "after_run": "Two."},
        {"kind": "ask", "lang": "python", "text": "Write double.", "check": "print(double(4))",
         "model": "def double(x):\n    return x * 2", "narration": ["N1", "N2"],
         "wrong": [{"code": "def double(x):\n    return x + 2", "ask": "Plus or times?", "why": "times is not plus."}],
         "walk": ["Name it double.", "Hand back x times 2."],
         "return": {"text": "Write triple.", "check": "print(triple(4))", "model": "def triple(x):\n    return x * 3",
                    "narration": ["R1", "R2"]}},
        {"kind": "cold-check", "lang": "python", "text": "Cold.", "model": "print(sum([1, 2, 3]))"},
    ]


def test_a_shown_python_program_runs_and_says_it_is_python(make_engine, reach):
    e = make_engine(py_steps())
    st, items, _ = e.start()
    assert e.pending(st) == {"mode": "run", "sql": "print(1 + 1)", "lang": "python"}
    st, items, _ = e.advance(st)
    assert items[0] == {"type": "learner", "sql": "print(1 + 1)", "lang": "python"}
    assert items[1] == {"type": "result", "lang": "python", "text": "2\n", "error": None}


def test_a_python_question_asks_for_python(make_engine, reach):
    e = make_engine(py_steps())
    st = reach(e, 2)
    assert e.pending(st) == {"mode": "answer", "step": 2, "variant": "main", "lang": "python"}


def test_a_python_answer_is_judged_by_the_hidden_check(make_engine, reach):
    e = make_engine(py_steps())
    st = reach(e, 2)
    st, items, events = e.answer(st, "def double(x):\n    return x + x")
    assert events[0]["outcome"] == "correct"
    assert items[0]["lang"] == "python"
    assert items[1]["text"] == "" and texts(items)[0] in ("N1", "N2")


def test_python_has_no_slip_view_and_ignores_spacing_only_in_matching(make_engine, reach):
    e = make_engine(py_steps())
    st = reach(e, 2)
    st, items, events = e.answer(st, "def double( x ):\n    return x*2")
    assert events[0]["outcome"] == "correct" and "compare" not in kinds(items)


def test_the_ladder_works_for_python_and_shows_python_at_the_end(make_engine, reach):
    e = make_engine(py_steps())
    st = reach(e, 2)
    st, _, events = e.answer(st, "x = 1")
    assert events[0]["outcome"] == "miss"
    st, items, _ = e.answer(st, "def double(x):\n    return x + 2")
    assert texts(items) == ["Plus or times?"]
    st, items, _ = e.answer(st, "x = 1")
    assert "1. Name it double." in texts(items)[0]
    st, items, _ = e.answer(st, "x = 1")
    assert "```python\ndef double(x):\n    return x * 2\n```" in texts(items)[0]
    st, items, _ = e.answer(st, "def double(x):\n    return x * 2")
    assert texts(items)[0] == "Times is not plus."


def test_a_missed_python_step_comes_back_as_a_python_return(make_engine, reach):
    e = make_engine(py_steps())
    st = reach(e, 2)
    st, _, _ = e.answer(st, "x = 1")
    st, _, _ = e.answer(st, "def double(x):\n    return x * 2")
    st, *_ = e.advance(st)
    assert e.pending(st) == {"mode": "answer", "step": 2, "variant": "return", "lang": "python"}
    st, items, events = e.answer(st, "def triple(x):\n    return x * 3")
    assert events[0] == {"step": 2, "variant": "return", "typed": "def triple(x):\n    return x * 3",
                         "outcome": "correct", "misses": 0}


def test_a_python_cold_check_shows_both_outputs(make_engine, reach):
    e = make_engine(py_steps())
    st = reach(e, 3)
    st, items, events = e.answer(st, "print(0)")
    assert [i.get("label") for i in items if i["type"] == "result"] == ["Yours", "Model"]
    assert items[1]["text"] == "0\n" and items[2]["text"] == "6\n"
    assert events[0]["outcome"] == "shown"


def test_teacher_text_in_a_python_step_is_marked_python_and_in_sql_it_is_not(make_engine, reach, play_steps):
    e = make_engine(py_steps())
    st, items, _ = e.start()
    assert items[0]["lang"] == "python"
    sql_engine = make_engine(play_steps)
    st, items, _ = sql_engine.start()
    assert "lang" not in items[0]
