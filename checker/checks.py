import sqlite3

from .data import run, same_rows


def _flags(step):
    return {"ordered": step.get("ordered", False),
            "any_column_order": step.get("any_column_order", False)}


def _try(conn, sql):
    """Return (rows, None), or (None, error message) if the sentence fails."""
    try:
        return run(conn, sql), None
    except sqlite3.Error as e:
        return None, str(e)


def check_sql(conn, lesson, steps):
    """Checks 1 and 1b: every SQL sentence in the lesson runs, or fails, as the step says."""
    fails = []

    def fail(n, msg):
        fails.append(f"FAIL {lesson} step {n}: {msg}")

    for n, s in enumerate(steps, 1):
        for sql in s.get("shows", []):
            _, err = _try(conn, sql)
            if err:
                fail(n, f"shown sentence does not run: {err}: {sql}")
        if "broken" in s and _try(conn, s["broken"])[1] is None:
            fail(n, f"broken sentence runs without error: {s['broken']}")
        if "model" not in s:
            continue
        rows, err = _try(conn, s["model"])
        if err:
            fail(n, f"model answer does not run: {err}")
            continue
        if not rows:
            fail(n, "model answer returns no rows")
        if "rows" in s and len(rows) != s["rows"]:
            fail(n, f"model answer returns {len(rows)} rows, expected {s['rows']}")
        if "result" in s and not same_rows(rows, s["result"], ndigits=2, **_flags(s)):
            fail(n, f"model result {rows[:4]} differs from expected result {s['result']}")
        for sql in s.get("accepts", []):
            got, err = _try(conn, sql)
            if err or not got:
                fail(n, f"accepted answer does not run or returns no rows ({err or 'no rows'}): {sql}")
        for w in s.get("wrong", []):
            if "ask" not in w and "tell" not in w:
                fail(n, f"wrong answer needs ask or tell: {w.get('sql')}")
            if "sql" not in w:
                fail(n, "wrong answer has no sql")
                continue
            got, err = _try(conn, w["sql"])
            if err is None and same_rows(got, rows, **_flags(s)):
                fail(n, f"wrong answer gives the model result: {w['sql']}")
    return fails


def check_narration(lesson, steps):
    """Check 6: a typed step, except a cold check, has two non-empty narration lines."""
    fails = []
    for n, s in enumerate(steps, 1):
        if "model" in s and s.get("kind") != "cold-check":
            lines = [x for x in s.get("narration", []) if x.strip()]
            if len(lines) < 2:
                fails.append(f"FAIL {lesson} step {n}: needs at least two non-empty narration lines, has {len(lines)}")
    return fails
