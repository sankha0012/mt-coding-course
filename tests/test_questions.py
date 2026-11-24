from player.report import build_question_report
from player.store import Store


def make_run(store):
    return store.new_run("sql-02", {"phase": "continue"}, [{"type": "teacher", "text": "x"}])


def test_a_question_is_stored_with_its_lesson(tmp_path):
    s = Store(tmp_path)
    run = make_run(s)
    s.add_question(run, 5, "what is a pile?", "A group of rows.", "gemini", False)
    [q] = s.questions()
    assert (q["lesson"], q["step"], q["question"], q["provider"], q["guarded"]) == (
        "sql-02", 5, "what is a pile?", "gemini", 0)
    assert q["reply"] == "A group of rows."


def test_questions_do_not_touch_runs_items_or_events(tmp_path):
    s = Store(tmp_path)
    run = make_run(s)
    before = (s.latest_any(), s.items(run), s.events())
    s.add_question(run, 1, "q", "a", "groq", True)
    assert (s.latest_any(), s.items(run), s.events()) == before


def test_an_old_progress_file_gets_the_table(tmp_path):
    import sqlite3
    db = sqlite3.connect(tmp_path / "progress.db")
    db.executescript("CREATE TABLE runs (id INTEGER PRIMARY KEY, lesson TEXT, started_at TEXT, "
                     "finished_at TEXT, state_json TEXT); INSERT INTO runs VALUES (1, 'sql-01', 't', NULL, '{}');")
    db.commit()
    db.close()
    s = Store(tmp_path)
    s.add_question(1, 2, "q", "a", "gemini", False)
    assert len(s.questions()) == 1
    assert s.conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 1


def test_the_report_ranks_steps_by_questions_asked():
    qs = [{"lesson": "sql-02", "step": 5, "question": "a"}, {"lesson": "sql-01", "step": 9, "question": "b"},
          {"lesson": "sql-02", "step": 5, "question": "c"}]
    assert build_question_report(qs) == [
        "sql-02 step 5: 2 questions; latest: c", "sql-01 step 9: 1 question; latest: b"]
    assert build_question_report([]) == []
