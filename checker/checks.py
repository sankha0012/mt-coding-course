import re
import sqlite3
from difflib import SequenceMatcher

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


def check_audit(thoughts, lessons):
    """Check 2: every required thought was introduced earlier, and every id exists."""
    fails, seen = [], {}
    for lesson, steps in lessons:
        for n, s in enumerate(steps, 1):
            where = f"{lesson} step {n}"
            here = {}
            for t in s.get("new", []) + s.get("imports", []):
                if t not in thoughts:
                    fails.append(f"FAIL {where}: unknown thought '{t}'")
                elif t in seen:
                    fails.append(f"FAIL {where}: thought '{t}' already introduced at {seen[t]}")
                else:
                    here[t] = where
            for t in s.get("requires", []):
                if t not in thoughts:
                    fails.append(f"FAIL {where}: unknown thought '{t}'")
                elif t not in seen and t not in here:
                    fails.append(f"FAIL {where}: requires '{t}', which no earlier step introduces")
            seen.update(here)
    return fails


def check_new_limit(lessons):
    """Check 3: at most one new thought per step. Imports do not count."""
    return [
        f"FAIL {lesson} step {n}: introduces {len(s['new'])} new thoughts ({', '.join(s['new'])}), at most one allowed"
        for lesson, steps in lessons
        for n, s in enumerate(steps, 1)
        if len(s.get("new", [])) > 1
    ]


def _tokens(sql):
    return re.findall(r"'[^']*'|\w+|[^\s\w]", sql.lower())


def _changed_runs(a, b):
    """How many separate runs of tokens differ between two SQL sentences."""
    ops = SequenceMatcher(None, _tokens(a), _tokens(b), autojunk=False).get_opcodes()
    return sum(1 for tag, *_ in ops if tag != "equal")


def check_shapes(lessons):
    """Check 4: two consecutive typed steps must not differ in one place only."""
    fails = []
    for lesson, steps in lessons:
        typed = [(n, s) for n, s in enumerate(steps, 1) if "model" in s]
        for (n1, a), (n2, b) in zip(typed, typed[1:]):
            if _changed_runs(a["model"], b["model"]) <= 1:
                fails.append(f"FAIL {lesson} step {n2}: same shape as step {n1}; the answers differ in one place only")
    return fails


def report_spacing(thoughts, lessons):
    """Check 5: for each thought, where it is needed again after its introduction."""
    flat = [(f"{lesson}:{n}", s) for lesson, steps in lessons for n, s in enumerate(steps, 1)]
    intro, needed = {}, {}
    for i, (_, s) in enumerate(flat):
        for t in s.get("new", []) + s.get("imports", []):
            intro.setdefault(t, i)
        for t in s.get("requires", []):
            needed.setdefault(t, []).append(i)
    lines = []
    for t in sorted(thoughts, key=lambda t: intro.get(t, len(flat))):
        if t not in intro:
            lines.append(f"{t}: never introduced")
            continue
        later = [j for j in needed.get(t, []) if j > intro[t]]
        if not later:
            lines.append(f"{t}: introduced {flat[intro[t]][0]}; never needed again")
            continue
        gaps = [b - a for a, b in zip([intro[t]] + later, later)]
        lines.append(f"{t}: introduced {flat[intro[t]][0]}; needed at "
                     f"{', '.join(flat[j][0] for j in later)}; gaps {', '.join(map(str, gaps))}")
    return lines


def report_load(lessons):
    """Check 7: where new thoughts fall. Warn on three or more steps in a row."""
    lines, warns = [], []
    for lesson, steps in lessons:
        new = [n for n, s in enumerate(steps, 1) if s.get("new")]
        lines.append(f"{lesson}: new thoughts at steps {', '.join(map(str, new))} ({len(new)} in {len(steps)})")
        streak = []
        for n in new + [None]:
            if streak and (n is None or n != streak[-1] + 1):
                if len(streak) >= 3:
                    warns.append(f"WARN {lesson} steps {streak[0]} to {streak[-1]}: "
                                 f"a new thought in each of {len(streak)} steps in a row")
                streak = []
            if n is not None:
                streak.append(n)
    return lines, warns


def check_all(conn, thoughts, lessons):
    fails = []
    for lesson, steps in lessons:
        fails += check_sql(conn, lesson, steps) + check_narration(lesson, steps)
    fails += check_audit(thoughts, lessons) + check_new_limit(lessons) + check_shapes(lessons)
    load, warns = report_load(lessons)
    return fails, warns, report_spacing(thoughts, lessons), load
