import os
from pathlib import Path

import pytest

from checker import mongo
from player.runner import Runner

ROOT = Path(__file__).parent.parent
needs_mongod = pytest.mark.skipif(not mongo.available(), reason="mongod is not installed here")


# ---- turning results into rows, no server needed

def test_documents_become_rows_of_their_values():
    rows = mongo.to_rows([{"_id": 1, "n": 2.0000001, "s": "a"}, {"_id": 2, "n": 3, "s": "b"}])
    assert rows == [(1, 2.0, "a"), (2, 3, "b")]


def test_a_number_a_missing_document_and_a_list_of_values_become_rows():
    assert mongo.to_rows(5601) == [(5601,)]
    assert mongo.to_rows(None) == []
    assert mongo.to_rows(["a", "b"]) == [("a",), ("b",)]
    assert mongo.to_rows({"acknowledged": True, "matchedCount": 1}) == [(True, 1)]


def test_nested_values_keep_their_names_and_dates_become_text():
    from datetime import datetime, timezone
    row = mongo.to_rows([{"_id": 1, "d": {"b": 2.00000004, "a": 1}, "l": [1.5, {"x": 1}],
                          "t": datetime(2026, 8, 1, 10, tzinfo=timezone.utc)}])[0]
    assert row == (1, (("a", 1), ("b", 2.0)), (1.5, (("x", 1),)), "2026-08-01T10:00:00Z")


def test_two_results_with_other_field_names_and_order_are_the_same_result():
    a = mongo.MongoResult(None, mongo.to_rows([{"_id": 2, "n": 113}, {"_id": 24, "n": 112}]))
    b = mongo.MongoResult(None, mongo.to_rows([{"restaurant": 2, "total": 113}, {"restaurant": 24, "total": 112}]))
    assert a.key({}) == b.key({})


def test_the_value_order_inside_a_document_is_free_and_row_order_only_when_asked():
    a = mongo.MongoResult(None, mongo.to_rows([{"x": 1, "y": "a"}, {"x": 2, "y": "b"}]))
    b = mongo.MongoResult(None, mongo.to_rows([{"y": "b", "x": 2}, {"y": "a", "x": 1}]))
    assert a.key({}) == b.key({})
    assert a.key({"ordered": True}) != b.key({"ordered": True})


def test_different_values_are_a_different_result():
    a = mongo.MongoResult(None, [(1,)])
    assert a.key({}) != mongo.MongoResult(None, [(2,)]).key({})


def test_the_screen_item_shows_the_first_documents_and_how_many_there_were():
    docs = [{"_id": i} for i in range(30)]
    item = mongo.MongoResult(None, mongo.to_rows(docs), docs).item()
    assert item["lang"] == "mongo" and item["total"] == 30 and len(item["docs"]) == 20 and item["error"] is None


def test_an_error_item_carries_only_the_error():
    item = mongo.MongoResult("nope").item()
    assert item["error"] == "nope" and item["docs"] == [] and item["total"] == 0


# ---- the private server

@pytest.fixture(scope="module")
def server():
    s = mongo.server_for(ROOT / "data")
    s.start()
    return s


@needs_mongod
def test_the_server_starts_privately_and_loads_the_course_data(server):
    db = server.db("mongo")
    assert db["orders"].count_documents({}) == 6000 and db["coupons"].count_documents({}) == 4
    assert db["orders"].find_one({"_id": 100001})["created_at"].year == 2026


@needs_mongod
def test_starting_again_changes_nothing(server):
    port = server.port
    server.start()
    assert server.port == port and server.running


@needs_mongod
def test_a_server_that_stops_leaves_no_process_and_no_folder(tmp_path):
    s = mongo.Server(ROOT / "data")
    s.start()
    folder, proc = s.folder, s._proc
    assert Path(folder).is_dir() and proc.poll() is None
    s.stop()
    assert proc.poll() is not None and not Path(folder).exists() and not s.running


def test_without_mongod_it_says_so_and_runs_nothing(monkeypatch, tmp_path):
    monkeypatch.setattr(mongo, "available", lambda: False)
    r = Runner(ROOT / "data")
    res = r.run({"lang": "mongo", "data": "mongo"}, "db.orders.find()")
    assert res.error and "MongoDB" in res.error


# ---- running sentences

def run(server, text, **kw):
    return mongo.run_mongo(server, "mongo", text, **kw)


@needs_mongod
def test_a_count_and_a_find(server):
    assert run(server, 'db.orders.countDocuments({status: "delivered"})').full == [(5601,)]
    r = run(server, 'db.orders.find({status: "cancelled", promised_minutes: 50}, {subtotal: 1})')
    assert r.error is None and r.total == 142 and len(r.item()["docs"]) == 20


@needs_mongod
def test_sort_limit_and_the_closing_sentence_of_the_pipeline_lesson(server):
    r = run(server, """db.orders.aggregate([
        {$match: {status: "delivered"}}, {$group: {_id: "$restaurant_id", n: {$sum: 1}}},
        {$sort: {n: -1}}, {$limit: 5}])""")
    assert r.error is None
    assert sorted(v for _, v in r.full) == [108, 109, 109, 112, 113]
    r = run(server, 'db.orders.find({status: "delivered", "delivery.rain": true}, {subtotal: 1}).sort({subtotal: -1}).limit(3)')
    assert [x[1] for x in r.full] == [193.68, 173.98, 173.26]


@needs_mongod
def test_distinct_and_find_one(server):
    assert len(run(server, 'db.orders.distinct("customer_id")').full) == 1475
    assert run(server, "db.orders.findOne({_id: 100001})").full[0][0] == 100001
    assert run(server, "db.orders.findOne({_id: -1})").full == []


@needs_mongod
def test_a_server_error_is_shown_as_the_servers_own_words(server):
    r = run(server, "db.orders.find({$bogus: 1})")
    assert r.error and "bogus" in r.error and r.full == []


@needs_mongod
def test_a_sentence_that_cannot_be_read_is_an_error_not_a_crash(server):
    assert "could not read" in run(server, "SELECT 1").error


@needs_mongod
@pytest.mark.parametrize("text", [
    'db.orders.aggregate([{$out: "copy"}])',
    'db.orders.aggregate([{$merge: {into: "copy"}}])',
    'db.orders.find({$where: "this.subtotal > 1"})',
    'db.orders.aggregate([{$group: {_id: 1, f: {$function: {body: "function(){return 1}", args: [], lang: "js"}}}}])',
])
def test_stages_that_write_or_run_code_are_refused_and_nothing_is_written(server, text):
    r = run(server, text)
    assert r.error and "not part of this course" in r.error
    assert "copy" not in server.db("mongo").list_collection_names()


@needs_mongod
def test_a_write_method_is_refused_on_the_course_data(server):
    before = server.db("mongo")["orders"].find_one({"_id": 100001})
    r = run(server, 'db.orders.updateOne({_id: 100001}, {$set: {status: "oops"}})')
    assert r.error and "scratch" in r.error
    assert server.db("mongo")["orders"].find_one({"_id": 100001}) == before


@needs_mongod
def test_a_write_on_a_scratch_copy_reports_and_never_reaches_the_course_data(server):
    before = server.db("mongo")["orders"].find_one({"_id": 100001})
    r = run(server, 'db.orders.updateOne({_id: 100001}, {$set: {status: "oops"}})', scratch=True)
    assert r.error is None and r.full == [(True, 1, 1, 0)]
    again = run(server, 'db.orders.updateOne({_id: 100001}, {$set: {status: "delivered"}})', scratch=True)
    assert again.full == [(True, 1, 1, 0)] or again.full == [(True, 1, 0, 0)]
    assert server.db("mongo")["orders"].find_one({"_id": 100001}) == before
    assert not [n for n in server.client.list_database_names() if n.startswith("scratch")]


@needs_mongod
def test_every_scratch_sentence_starts_from_the_course_data(server):
    run(server, "db.orders.deleteMany({})", scratch=True)
    assert run(server, "db.orders.countDocuments()", scratch=True).full == [(6000,)]


@needs_mongod
def test_a_slow_sentence_is_stopped(server, monkeypatch):
    monkeypatch.setattr(mongo, "TIMEOUT_MS", 50)
    r = run(server, 'db.orders.aggregate([{$project: {n: {$reduce: {input: {$range: [0, 100000]}, initialValue: 0, in: {$add: ["$$value", 1]}}}}}])')
    assert r.error and ("took too long" in r.error or "time limit" in r.error)


@needs_mongod
def test_the_runner_runs_a_mongo_step_and_the_try_panel_may_write_on_a_scratch_copy():
    runner = Runner(ROOT / "data")
    assert runner.available("mongo", "mongo")
    res = runner.run({"lang": "mongo", "data": "mongo"}, "db.coupons.countDocuments()")
    assert res.error is None and res.key({}) == mongo.MongoResult(None, [(4,)]).key({})
    item = runner.play("mongo", 'db.coupons.deleteMany({})', "mongo")
    assert item["error"] is None
    assert runner.run({"lang": "mongo", "data": "mongo"}, "db.coupons.countDocuments()").full == [(4,)]


@needs_mongod
def test_a_program_that_is_killed_leaves_no_server_and_no_folder(tmp_path):
    import signal
    import subprocess
    import sys
    import time
    code = ("import sys; sys.path.insert(0, %r)\n"
            "from checker import mongo\n"
            "s = mongo.Server(%r); s.start()\n"
            "print(s._proc.pid, s.folder, flush=True)\n"
            "import time; time.sleep(60)\n") % (str(ROOT), str(ROOT / "data"))
    p = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, text=True)
    pid, folder = p.stdout.readline().split()
    assert Path(folder).is_dir()
    p.send_signal(signal.SIGKILL)  # no time to clean up
    p.wait()
    for _ in range(300):
        try:
            os.kill(int(pid), 0)
        except ProcessLookupError:
            break
        time.sleep(0.1)
    else:
        os.kill(int(pid), signal.SIGKILL)
        pytest.fail("the server was left running")
    for _ in range(50):
        if not Path(folder).exists():
            break
        time.sleep(0.1)
    assert not Path(folder).exists()
