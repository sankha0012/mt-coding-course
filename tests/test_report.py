from player.report import build_report

STEPS = [{"kind": "give", "text": "x"},
         {"kind": "ask", "text": "x", "model": "SELECT 1", "requires": ["count-rows", "from-table"]},
         {"kind": "ask", "text": "x", "model": "SELECT 2", "requires": ["star"]}]


def ev(step, outcome, misses=0, typed="SELECT 9", variant="main"):
    return {"step": step, "variant": variant, "typed": typed, "outcome": outcome, "misses": misses}


def test_steps_with_most_misses_come_first():
    events = [ev(2, "correct"), ev(3, "miss"), ev(3, "miss", 1, "SELECT 8"), ev(3, "miss", 2, "SELECT 8"),
              ev(3, "correct", 3)]
    lines = build_report(events, STEPS)
    assert lines[0].startswith("step 3:")
    assert "4 answers" in lines[0] and "0 right the first time" in lines[0] and "3 misses" in lines[0]
    assert "most common miss: SELECT 8" in lines[0]
    assert "needs: star" in lines[0]
    assert lines[1].startswith("step 2:") and "1 right the first time" in lines[1]


def test_returns_are_listed_apart_from_their_step():
    lines = build_report([ev(2, "miss"), ev(2, "correct", 1, variant="return")], STEPS)
    assert any(l.startswith("step 2 (return):") for l in lines)


def test_no_events_gives_a_plain_line():
    assert build_report([], STEPS) == ["No answers yet."]
