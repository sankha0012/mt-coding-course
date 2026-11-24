import re
import sqlite3
import threading
import time
from dataclasses import dataclass, field

from checker.data import canon, load_db

_ALLOWED = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
_SINGLE_QUOTED = re.compile(r"('(?:[^']|'')*')")
_DOUBLE_QUOTED = re.compile(r'"([^"]*)"')
_TOKEN = re.compile(r"'(?:[^']|'')*'|\w+|[^\s\w]")
_lock = threading.Lock()


def _authorizer(action, *_):
    return sqlite3.SQLITE_OK if action in _ALLOWED else sqlite3.SQLITE_DENY


def fix_quotes(text):
    """A word in double quotes is text in this course. Single-quoted text is left alone."""
    parts = _SINGLE_QUOTED.split(text)
    return "".join(
        p if i % 2 else _DOUBLE_QUOTED.sub(lambda m: "'" + m.group(1).replace("'", "''") + "'", p)
        for i, p in enumerate(parts))


def normalise(text):
    """Text in a form that is equal when only case, spacing, quote style or a final semicolon differ."""
    t = re.sub(r";\s*$", "", fix_quotes(text).strip())
    return " ".join(tok if tok.startswith("'") else tok.lower() for tok in _TOKEN.findall(t))


@dataclass
class Result:
    error: str | None
    columns: list
    rows: list
    total: int
    full: list = field(default_factory=list, repr=False)

    def key(self, flags):
        """What two results are compared by: the rows, in the order the step cares about."""
        return canon(self.full, **flags)

    def item(self, label=None):
        out = {"type": "result", "columns": self.columns, "rows": self.rows,
               "total": self.total, "error": self.error}
        if label:
            out["label"] = label
        return out


def open_database(data_dir):
    conn = load_db(data_dir, check_same_thread=False)
    conn.set_authorizer(_authorizer)
    return conn


def run_sql(conn, text, limit=20, timeout=5.0):
    sql = fix_quotes(text)
    deadline = time.monotonic() + timeout
    with _lock:
        conn.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 10_000)
        try:
            cur = conn.execute(sql)
            full = cur.fetchall()
            columns = [d[0] for d in cur.description] if cur.description else []
        except sqlite3.OperationalError as e:
            msg = "That took too long, so it was stopped." if "interrupted" in str(e) else str(e)
            return Result(msg, [], [], 0)
        except (sqlite3.Error, sqlite3.Warning) as e:
            return Result(str(e), [], [], 0)
        finally:
            conn.set_progress_handler(None, 0)
    return Result(None, columns, [list(r) for r in full[:limit]], len(full), full)
