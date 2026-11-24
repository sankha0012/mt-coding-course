import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY, lesson TEXT, started_at TEXT, finished_at TEXT, state_json TEXT);
CREATE TABLE IF NOT EXISTS items (
  run_id INTEGER, seq INTEGER, json TEXT, PRIMARY KEY (run_id, seq));
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY, run_id INTEGER, ts TEXT, step INTEGER, variant TEXT,
  typed TEXT, outcome TEXT, misses INTEGER);
CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY, run_id INTEGER, step INTEGER, asked_at TEXT,
  question TEXT, reply TEXT, provider TEXT, guarded INTEGER);
"""


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    """The owner's progress. Rows are only added. State and finish time on a run are updated."""

    def __init__(self, folder):
        Path(folder).mkdir(parents=True, exist_ok=True)
        # ponytail: one shared connection, guarded by the Player's lock. Fine for one local learner.
        self.conn = sqlite3.connect(Path(folder) / "progress.db", check_same_thread=False)
        self.conn.executescript(SCHEMA)

    def latest(self, lesson):
        row = self.conn.execute(
            "SELECT id, state_json FROM runs WHERE lesson = ? ORDER BY id DESC LIMIT 1", (lesson,)).fetchone()
        return (row[0], json.loads(row[1])) if row else None

    def latest_any(self):
        row = self.conn.execute("SELECT id, lesson, state_json FROM runs ORDER BY id DESC LIMIT 1").fetchone()
        return (row[0], row[1], json.loads(row[2])) if row else None

    def new_run(self, lesson, state, items, finished=False):
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO runs (lesson, started_at, finished_at, state_json) VALUES (?, ?, ?, ?)",
                (lesson, _now(), _now() if finished else None, json.dumps(state)))
            self._add_items(cur.lastrowid, items)
        return cur.lastrowid

    def apply(self, run_id, state, items, events, finished=False):
        with self.conn:
            self._add_items(run_id, items)
            self.conn.executemany(
                "INSERT INTO events (run_id, ts, step, variant, typed, outcome, misses) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [(run_id, _now(), e["step"], e["variant"], e["typed"], e["outcome"], e["misses"]) for e in events])
            self.conn.execute(
                "UPDATE runs SET state_json = ?, finished_at = COALESCE(finished_at, ?) WHERE id = ?",
                (json.dumps(state), _now() if finished else None, run_id))

    def _add_items(self, run_id, items):
        last = self.conn.execute(
            "SELECT COALESCE(MAX(seq), -1) FROM items WHERE run_id = ?", (run_id,)).fetchone()[0]
        self.conn.executemany(
            "INSERT INTO items (run_id, seq, json) VALUES (?, ?, ?)",
            [(run_id, last + 1 + i, json.dumps(item, ensure_ascii=False)) for i, item in enumerate(items)])

    def items(self, run_id):
        rows = self.conn.execute("SELECT json FROM items WHERE run_id = ? ORDER BY seq", (run_id,))
        return [json.loads(r[0]) for r in rows]

    def events(self):
        cur = self.conn.execute(
            "SELECT e.id, e.run_id, r.lesson, e.ts, e.step, e.variant, e.typed, e.outcome, e.misses "
            "FROM events e JOIN runs r ON r.id = e.run_id ORDER BY e.id")
        names = [d[0] for d in cur.description]
        return [dict(zip(names, r)) for r in cur.fetchall()]

    def add_question(self, run_id, step, question, reply, provider, guarded):
        with self.conn:
            self.conn.execute(
                "INSERT INTO questions (run_id, step, asked_at, question, reply, provider, guarded) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (run_id, step, _now(), question, reply, provider, int(guarded)))

    def questions(self):
        cur = self.conn.execute(
            "SELECT q.id, q.run_id, r.lesson, q.step, q.asked_at, q.question, q.reply, q.provider, q.guarded "
            "FROM questions q JOIN runs r ON r.id = q.run_id ORDER BY q.id")
        names = [d[0] for d in cur.description]
        return [dict(zip(names, r)) for r in cur.fetchall()]
