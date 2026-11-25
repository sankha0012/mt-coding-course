import re
import sqlite3

from .data import run, same_rows
from .env import as_env
from .mongo import run_mongo
from .mongoparse import ParseError, normalise as mongo_normalise, parse as mongo_parse
from .pyrun import run_python, same_output


def _is_mongo(step):
    return step.get("lang", "sql") == "mongo"


def _flags(step):
    # a MongoDB document is judged by its values, so the order of its fields is always free
    return {"ordered": step.get("ordered", False),
            "any_column_order": step.get("any_column_order", False) or _is_mongo(step)}


def _is_python(step):
    return step.get("lang", "sql") == "python"


def _code(entry):
    """The sentence of a wrong-answer entry: `sql` in an SQL step, `code` in a Python one."""
    return entry.get("sql") or entry.get("code")


def _run(env, step, code, check=True):
    """Run one sentence of a step. Returns (value, None) or (None, error message).
    SQL gives its rows. Python gives its output, with the step's hidden `check` code added after it."""
    dataset = step.get("data", "")
    if _is_python(step):
        full = code + ("\n" + step["check"] if check and step.get("check") else "")
        r = run_python(full, env.path(dataset), timeout=120)
        return (r.output, None) if r.error is None else (None, r.error)
    if not env.available(dataset):
        return None, f"The data folder was not found: {dataset}"
    if _is_mongo(step):
        r = run_mongo(env.mongo(), dataset, code, scratch=bool(step.get("scratch")))
        return (r.full, None) if r.error is None else (None, r.error)
    try:
        return run(env.sql(dataset), code), None
    except sqlite3.Error as e:
        return None, str(e)


def _empty(step, value):
    return not value.strip() if _is_python(step) else not value


def _same(step, a, b, **flags):
    if _is_mongo(step):
        flags["any_column_order"] = True
    return same_output(a, b) if _is_python(step) else same_rows(a, b, **flags)


def _model_problems(env, step):
    """Run a step's model answer. Return (its value, or None if it fails to run; list of problems)."""
    value, err = _run(env, step, step["model"])
    if err:
        return None, [f"model answer does not run: {err}"]
    problems = []
    if _empty(step, value):
        problems.append("model answer prints nothing" if _is_python(step) else "model answer returns no rows")
    if _is_python(step):
        if "output" in step and not same_output(value, step["output"]):
            problems.append(f"model output {value.strip()!r} differs from expected output {step['output']!r}")
        return value, problems
    if "rows" in step and len(value) != step["rows"]:
        problems.append(f"model answer returns {len(value)} rows, expected {step['rows']}")
    if "result" in step and not same_rows(value, step["result"], ndigits=2, **_flags(step)):
        problems.append(f"model result {value[:4]} differs from expected result {step['result']}")
    return value, problems


def _accept_problems(env, step):
    problems = []
    for code in step.get("accepts", []):
        got, err = _run(env, step, code)
        if err or _empty(step, got):
            problems.append(f"accepted answer does not run or returns no rows ({err or 'no rows'}): {code}")
    return problems


def check_sql(env, lesson, steps):
    """Checks 1 and 1b: every sentence in the lesson runs, or fails, as the step says.
    (The name is older than Python steps. It checks both languages.)"""
    env = as_env(env)
    fails = []

    def fail(n, msg):
        fails.append(f"FAIL {lesson} step {n}: {msg}")

    for n, s in enumerate(steps, 1):
        for code in s.get("shows", []):
            _, err = _run(env, s, code, check=False)
            if err:
                fail(n, f"shown sentence does not run: {err}: {code}")
        if "broken" in s and _run(env, s, s["broken"], check=False)[1] is None:
            fail(n, f"broken sentence runs without error: {s['broken']}")
        if "model" not in s:
            continue
        value, problems = _model_problems(env, s)
        for p in problems:
            fail(n, p)
        if value is None:
            continue
        for p in _accept_problems(env, s):
            fail(n, p)
        for w in s.get("wrong", []):
            if "ask" not in w and "tell" not in w:
                fail(n, f"wrong answer needs ask or tell: {_code(w)}")
            if _code(w) is None:
                fail(n, "wrong answer has no sql")
                continue
            got, err = _run(env, s, _code(w))
            if err is None and _same(s, got, value, **_flags(s)):
                what = "output" if _is_python(s) else "result"
                fail(n, f"wrong answer gives the model {what}: {_code(w)}")
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


def _norm_code(step, code):
    if _is_mongo(step):
        return mongo_normalise(code)
    return " ".join(code.split()) if _is_python(step) else _tokens(code)


def check_returns(env, lesson, steps):
    """Check 8: a return sentence runs, differs from its step, and has narration."""
    env = as_env(env)
    fails = []
    for n, s in enumerate(steps, 1):
        r = s.get("return")
        if r is None:
            continue

        def fail(msg, n=n):
            fails.append(f"FAIL {lesson} step {n}: return: {msg}")

        if s.get("kind") == "cold-check":
            fail("is not allowed on a cold check")
            continue
        if "model" not in r:
            fail("has no model")
            continue
        if _is_python(s) and s.get("check") and not r.get("check"):
            fail("needs its own check, because its step has one")
            continue
        # a return runs in the same language and data folder as its step
        ret = {**{k: s[k] for k in ("lang", "data") if k in s}, **r}
        value, problems = _model_problems(env, ret)
        for p in problems + _accept_problems(env, ret):
            fail(p)
        if value is not None:
            if _norm_code(s, r["model"]) == _norm_code(s, s["model"]):
                fail("model is the same sentence as the step's")
            else:
                original, err = _run(env, s, s["model"])
                flags = {k: r.get(k, False) or s.get(k, False) for k in ("ordered", "any_column_order")}
                if err is None and _same(s, value, original, **flags):
                    fail("gives the same result as the step's answer")
        lines = [x for x in r.get("narration", []) if x.strip()]
        if len(lines) < 2:
            fail(f"needs at least two non-empty narration lines, has {len(lines)}")
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


_CLAUSES = {"select", "from", "where", "group", "having", "order", "limit", "join", "on", "union"}


def _clauses(sql):
    """Split a sentence into clauses, keyed by clause word and occurrence."""
    out, seen, key = {}, {}, None
    for t in _tokens(sql):
        if t in _CLAUSES:
            seen[t] = seen.get(t, 0) + 1
            key = (t, seen[t])
            out[key] = []
        elif key:
            out[key].append(t)
    return out


def _changed_clauses(a, b):
    """How many clauses differ between two SQL sentences. A clause is a slot."""
    ca, cb = _clauses(a), _clauses(b)
    return sum(1 for k in ca.keys() | cb.keys() if ca.get(k) != cb.get(k))


def _code_tokens(code):
    return re.findall(r"'[^']*'|\"[^\"]*\"|\w+|[^\s\w]", code)


def _changed_runs(a, b):
    """How many separate runs of tokens differ between two programs. A run is a slot."""
    from difflib import SequenceMatcher
    ops = SequenceMatcher(None, _code_tokens(a), _code_tokens(b), autojunk=False).get_opcodes()
    return sum(1 for tag, *_ in ops if tag != "equal")


def _mongo_slots(sentence):
    """The pieces of a MongoDB sentence: the collection and method, each argument (each stage of a pipeline),
    and each chained word. A piece is a slot."""
    try:
        c = mongo_parse(sentence)
    except ParseError:
        return None
    args = c.args[0] if c.method == "aggregate" and c.args and isinstance(c.args[0], list) else c.args
    return [f"{c.collection}.{c.method}", *[repr(x) for x in args], *[f"{n}{a!r}" for n, a in c.mods]]


def _changed_pieces(a, b):
    pa, pb = _mongo_slots(a), _mongo_slots(b)
    if pa is None or pb is None:
        return 99
    return sum(1 for x, y in zip(pa, pb) if x != y) + abs(len(pa) - len(pb))


def _lang(step):
    return step.get("lang", "sql")


def _slots_changed(a, b):
    if _lang(a) != _lang(b):
        return 99
    if _is_python(a):
        return _changed_runs(a["model"], b["model"])
    if _is_mongo(a):
        return _changed_pieces(a["model"], b["model"])
    return _changed_clauses(a["model"], b["model"])


def check_shapes(lessons):
    """Check 4: two consecutive typed steps must not differ in one slot only."""
    fails = []
    for lesson, steps in lessons:
        typed = [(n, s) for n, s in enumerate(steps, 1) if "model" in s]
        for (n1, a), (n2, b) in zip(typed, typed[1:]):
            if _slots_changed(a, b) <= 1:
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


def check_all(env, thoughts, lessons):
    env = as_env(env)
    fails, skipped = [], []
    for lesson, steps in lessons:
        missing = sorted({s["data"] for s in steps if s.get("data") and not env.available(s["data"])})
        no_mongo = any(_is_mongo(s) for s in steps) and not env.available(lang="mongo")
        if missing or no_mongo:
            skipped += [f"WARN {lesson}: the data folder '{d}' was not found, so its answers were not run" for d in missing]
            if no_mongo:
                skipped.append(f"WARN {lesson}: MongoDB is not installed here, so its answers were not run")
            fails += check_narration(lesson, steps)
            continue
        fails += (check_sql(env, lesson, steps) + check_narration(lesson, steps)
                  + check_returns(env, lesson, steps))
    fails += (check_audit(thoughts, lessons) + check_new_limit(lessons) + check_shapes(lessons)
              + check_shape(thoughts, lessons))
    load, warns = report_load(lessons)
    return fails, skipped + warns, report_spacing(thoughts, lessons), load


def _grade(thoughts, thought):
    """A thought is core unless thoughts.yaml gives it a grade: {text: ..., grade: shape | name-only}."""
    entry = thoughts.get(thought)
    return entry.get("grade", "core") if isinstance(entry, dict) else "core"


def check_shape(thoughts, lessons):
    """Check 9: a shape thought is only asked in a step that supplies its spelling in its own text,
    and a name-only thought is never asked."""
    fails = []
    for lesson, steps in lessons:
        for n, s in enumerate(steps, 1):
            where = f"FAIL {lesson} step {n}:"
            for spelling in s.get("supplies", []):
                if spelling not in s.get("text", ""):
                    fails.append(f"{where} supplies \"{spelling}\" but its text does not contain it")
            for t in s.get("requires", []):
                grade = _grade(thoughts, t)
                if grade == "name-only":
                    fails.append(f"{where} requires the name-only thought '{t}', which is never asked")
                elif grade == "shape" and not s.get("supplies"):
                    fails.append(f"{where} requires the shape thought '{t}', so it must list what it supplies")
    return fails
