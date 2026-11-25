import random
from pathlib import Path

import pytest
import yaml

from checker import mongo
from player.engine import Engine
from player.runner import Runner

ROOT = Path(__file__).parent.parent
LESSONS = sorted((ROOT / "content" / "mongo").glob("lesson-*.yaml"))
needs_mongod = pytest.mark.skipif(not mongo.available(), reason="mongod is not installed here")
UI = yaml.safe_load((ROOT / "content" / "ui.yaml").read_text(encoding="utf-8"))


def play(steps, miss_first):
    """Sit a lesson as a learner who types each model answer, optionally missing every typed step once first.
    Returns the outcomes of every answer."""
    engine = Engine(steps, Runner(ROOT / "data"), UI, random.Random(1))
    st, _, _ = engine.start()
    outcomes = []
    for _ in range(400):
        p = engine.pending(st)
        if p["mode"] == "done":
            return outcomes
        if p["mode"] in ("run", "continue"):
            st, items, _ = engine.advance(st)
            assert not [i for i in items if i["type"] == "result" and i["error"]], items
            continue
        step = steps[p["step"] - 1]
        model = (step["return"] if p["variant"] == "return" else step)["model"]
        if miss_first and p["variant"] == "main" and step["kind"] != "cold-check" and st["misses"] == 0:
            st, _, events = engine.answer(st, "db.orders.countDocuments({_id: -1})")
            outcomes += [e["outcome"] for e in events]
        st, _, events = engine.answer(st, model)
        outcomes += [e["outcome"] for e in events]
    raise AssertionError("the lesson never ended")


@needs_mongod
@pytest.mark.parametrize("path", LESSONS, ids=[p.stem for p in LESSONS])
def test_a_learner_who_types_every_model_answer_finishes_the_lesson_and_is_never_missed(path):
    steps = yaml.safe_load(path.read_text(encoding="utf-8"))["steps"]
    assert set(play(steps, miss_first=False)) <= {"correct", "shown"}  # a cold check is shown, never missed


@needs_mongod
@pytest.mark.parametrize("path", LESSONS, ids=[p.stem for p in LESSONS])
def test_a_learner_who_misses_every_step_once_is_laddered_and_still_finishes_with_every_return_accepted(path):
    steps = yaml.safe_load(path.read_text(encoding="utf-8"))["steps"]
    outcomes = play(steps, miss_first=True)
    assert outcomes.count("miss") >= 5 and "correct" in outcomes
    # after a miss, the model answer is the right way to answer, and so is the return that comes back later
    assert set(outcomes) <= {"correct", "miss", "shown"}
