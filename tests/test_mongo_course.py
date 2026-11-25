import pytest

from checker import mongo
from checker.__main__ import main

needs_mongod = pytest.mark.skipif(not mongo.available(), reason="mongod is not installed here")


def texts(items):
    return [i["text"] for i in items if i["type"] == "teacher"]


def mg_steps():
    base = {"lang": "mongo", "data": "mongo"}
    return [
        {"kind": "give", **base, "new": ["count-rows"], "text": "t", "shows": ["db.orders.countDocuments()"],
         "after_run": "6,000 orders."},
        {"kind": "ask", **base, "new": ["from-table"], "requires": ["count-rows", "from-table"], "text": "How many coupons?",
         "model": "db.coupons.countDocuments()", "rows": 1, "result": [[4]], "narration": ["N1", "N2"],
         "wrong": [{"code": "db.couriers.countDocuments()", "ask": "Which collection?", "why": "the name is the table."}],
         "walk": ["Name the collection.", "Count it."],
         "return": {"text": "How many couriers?", "model": "db.couriers.countDocuments()", "narration": ["R1", "R2"]}},
        {"kind": "give", **base, "new": ["star"], "text": "t", "shows": ["db.coupons.find()"]},
        {"kind": "ask", **base, "requires": ["star", "from-table"], "text": "Moto couriers' cities.",
         "model": 'db.couriers.find({vehicle: "moto"}, {city: 1})', "rows": 110, "narration": ["A", "B"]},
    ]


# ---- the checker

@needs_mongod
def test_a_mongo_lesson_that_is_right_passes(write_strand, data_dir, capsys):
    assert main([str(write_strand(mg_steps())), "--data", str(data_dir)]) == 0
    assert "FAIL" not in capsys.readouterr().out


@needs_mongod
def test_a_model_that_does_not_run_fails_with_the_servers_words(write_strand, data_dir, capsys):
    steps = mg_steps()
    steps[1]["model"] = "db.coupons.find({$bogus: 1})"
    assert main([str(write_strand(steps)), "--data", str(data_dir)]) == 1
    assert "FAIL t-01 step 2: model answer does not run" in capsys.readouterr().out


@needs_mongod
def test_a_wrong_answer_that_gives_the_models_result_fails(write_strand, data_dir, capsys):
    steps = mg_steps()
    steps[1]["wrong"][0]["code"] = "db.coupons.countDocuments({})"
    assert main([str(write_strand(steps)), "--data", str(data_dir)]) == 1
    assert "wrong answer gives the model result" in capsys.readouterr().out


@needs_mongod
def test_a_shown_sentence_that_does_not_run_fails(write_strand, data_dir, capsys):
    steps = mg_steps()
    steps[2]["shows"] = ["db.coupons.find({a: })"]
    assert main([str(write_strand(steps)), "--data", str(data_dir)]) == 1
    assert "shown sentence does not run" in capsys.readouterr().out


@needs_mongod
def test_a_wrong_row_count_in_the_step_fails(write_strand, data_dir, capsys):
    steps = mg_steps()
    steps[3]["rows"] = 5
    assert main([str(write_strand(steps)), "--data", str(data_dir)]) == 1
    assert "model answer returns 110 rows, expected 5" in capsys.readouterr().out


@needs_mongod
def test_two_neighbouring_answers_that_differ_in_one_place_fail(write_strand, data_dir, capsys):
    steps = mg_steps()
    steps[3]["model"] = 'db.couriers.find({vehicle: "bike"}, {city: 1})'
    steps[3]["rows"] = 73
    steps[1]["model"] = 'db.couriers.find({vehicle: "moto"}, {city: 1})'
    steps[1]["rows"], steps[1]["result"] = 110, None
    del steps[1]["result"]
    steps[1]["wrong"][0]["code"] = "db.couriers.find({vehicle: \"carro\"}, {city: 1})"
    steps[1]["return"]["model"] = 'db.couriers.find({vehicle: "carro"}, {city: 1})'
    assert main([str(write_strand(steps)), "--data", str(data_dir)]) == 1
    assert "same shape as step 2" in capsys.readouterr().out


@needs_mongod
def test_a_return_that_is_the_same_sentence_in_other_spacing_fails(write_strand, data_dir, capsys):
    steps = mg_steps()
    steps[1]["return"]["model"] = "db.coupons.countDocuments( ) ;"
    assert main([str(write_strand(steps)), "--data", str(data_dir)]) == 1
    assert "model is the same sentence as the step's" in capsys.readouterr().out


def test_without_mongod_the_lesson_is_skipped_with_a_warning(write_strand, data_dir, capsys, monkeypatch):
    monkeypatch.setattr(mongo, "available", lambda: False)
    steps = mg_steps()
    steps[1]["model"] = "db.coupons.find({$bogus: 1})"
    assert main([str(write_strand(steps)), "--data", str(data_dir)]) == 0
    out = capsys.readouterr().out
    assert "WARN t-01: MongoDB is not installed here, so its answers were not run" in out and "FAIL" not in out


# ---- the engine

@needs_mongod
def test_a_mongo_step_says_it_is_mongo(make_engine, reach):
    e = make_engine(mg_steps())
    st, _, _ = e.start()
    assert e.pending(st) == {"mode": "run", "sql": "db.orders.countDocuments()", "lang": "mongo"}
    st, items, _ = e.advance(st)
    assert items[0] == {"type": "learner", "sql": "db.orders.countDocuments()", "lang": "mongo"}
    assert items[1]["lang"] == "mongo" and items[1]["docs"] == [6000] and items[1]["error"] is None
    st = reach(e, 2)
    assert e.pending(st) == {"mode": "answer", "step": 2, "variant": "main", "lang": "mongo"}


@needs_mongod
def test_another_spelling_of_the_right_answer_is_correct(make_engine, reach):
    e = make_engine(mg_steps())
    st = reach(e, 2)
    st, items, events = e.answer(st, "db.coupons.countDocuments( ) ;")
    assert events[0]["outcome"] == "correct" and texts(items)[-1] in ("N1", "N2")


@needs_mongod
def test_a_different_sentence_with_the_same_result_is_correct(make_engine, reach):
    e = make_engine(mg_steps())
    st = reach(e, 2)
    st, _, events = e.answer(st, "db.coupons.countDocuments({discount_pct: {$gte: 0}})")
    assert events[0]["outcome"] == "correct"


@needs_mongod
def test_a_known_wrong_mongo_answer_gets_its_question(make_engine, reach):
    e = make_engine(mg_steps())
    st = reach(e, 2)
    st, _, events = e.answer(st, "db.couriers.countDocuments()")
    assert events[0]["outcome"] == "miss"
    st, items, _ = e.answer(st, "db.couriers.countDocuments( )")
    assert texts(items)[-1] == "Which collection?"


@needs_mongod
def test_a_mongo_answer_shown_in_the_ladder_is_fenced_as_mongo(make_engine, reach):
    e = make_engine(mg_steps())
    st = reach(e, 2)
    for _ in range(3):
        st, items, _ = e.answer(st, "db.orders.countDocuments()")
    shown = [t for t in texts(items) if "```" in t][0]
    assert "```mongo\ndb.coupons.countDocuments()\n```" in shown


@needs_mongod
def test_an_answer_that_is_not_a_sentence_is_a_calm_miss(make_engine, reach):
    e = make_engine(mg_steps())
    st = reach(e, 2)
    st, items, events = e.answer(st, "how many coupons")
    assert events[0]["outcome"] == "miss" and items[1]["error"] and "wrong" not in items[1]["error"].lower()
