from pathlib import Path

from player.store import Store

EVENT = {"step": 2, "variant": "main", "typed": "SELECT 1", "outcome": "miss", "misses": 0}


def test_a_new_store_has_no_run(tmp_path):
    assert Store(tmp_path).latest("sql-01") is None


def test_a_run_keeps_its_state_items_and_events(tmp_path):
    s = Store(tmp_path)
    run_id = s.new_run("sql-01", {"pos": 0}, [{"type": "teacher", "text": "Hi"}])
    s.apply(run_id, {"pos": 1}, [{"type": "teacher", "text": "Next"}], [EVENT])
    assert s.latest("sql-01") == (run_id, {"pos": 1})
    assert [i["text"] for i in s.items(run_id)] == ["Hi", "Next"]
    assert s.events() == [{**EVENT, "run_id": run_id, "id": 1, "ts": s.events()[0]["ts"], "lesson": "sql-01"}]


def test_progress_survives_reopening_the_file(tmp_path):
    run_id = Store(tmp_path).new_run("sql-01", {"pos": 3}, [{"type": "teacher", "text": "Hi"}])
    again = Store(tmp_path)
    assert again.latest("sql-01") == (run_id, {"pos": 3})
    assert again.items(run_id) == [{"type": "teacher", "text": "Hi"}]


def test_a_new_run_keeps_the_old_one(tmp_path):
    s = Store(tmp_path)
    first = s.new_run("sql-01", {"n": 1}, [{"type": "teacher", "text": "one"}], finished=True)
    second = s.new_run("sql-01", {"n": 2}, [{"type": "teacher", "text": "two"}])
    assert second > first
    assert s.latest("sql-01") == (second, {"n": 2})
    assert [i["text"] for i in s.items(first)] == ["one"]


def test_finishing_a_run_is_recorded_once(tmp_path):
    s = Store(tmp_path)
    run_id = s.new_run("sql-01", {}, [])
    s.apply(run_id, {}, [], [], finished=True)
    first = s.conn.execute("SELECT finished_at FROM runs").fetchone()[0]
    assert first
    s.apply(run_id, {}, [], [], finished=True)
    assert s.conn.execute("SELECT finished_at FROM runs").fetchone()[0] == first


def test_lessons_have_separate_runs(tmp_path):
    s = Store(tmp_path)
    s.new_run("sql-01", {"a": 1}, [])
    assert s.latest("sql-02") is None


def test_the_store_never_deletes_or_drops():
    source = (Path(__file__).parent.parent / "player" / "store.py").read_text().upper()
    assert "DELETE" not in source and "DROP" not in source


def test_latest_any_is_the_newest_run_of_any_lesson(tmp_path):
    s = Store(tmp_path)
    assert s.latest_any() is None
    s.new_run("sql-01", {"n": 1}, [], finished=True)
    second = s.new_run("sql-02", {"n": 2}, [])
    assert s.latest_any() == (second, "sql-02", {"n": 2})


def test_events_say_which_lesson_they_belong_to(tmp_path):
    s = Store(tmp_path)
    a = s.new_run("sql-01", {}, [])
    b = s.new_run("sql-02", {}, [])
    s.apply(a, {}, [], [EVENT])
    s.apply(b, {}, [], [{**EVENT, "step": 5}])
    assert [(e["lesson"], e["step"]) for e in s.events()] == [("sql-01", 2), ("sql-02", 5)]
