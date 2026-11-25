from pathlib import Path

import yaml

from checker.lesson import prerequisites

ROOT = Path(__file__).parent.parent


def course(tmp_path, lessons):
    """lessons: (strand, name, stage, steps) in played order. Writes a course folder and returns it."""
    manifest = []
    for i, (strand, name, stage, steps) in enumerate(lessons):
        (tmp_path / strand).mkdir(exist_ok=True)
        entry = f"{strand}/lesson-{i:02d}"
        (tmp_path / f"{entry}.yaml").write_text(yaml.safe_dump(
            {"lesson": name, "title": name, "strand": strand, "stage": stage, "steps": steps}), encoding="utf-8")
        manifest.append(entry)
    (tmp_path / "course.yaml").write_text(yaml.safe_dump({"course": manifest}), encoding="utf-8")
    return tmp_path


def step(new=(), requires=(), kind="give"):
    return {"kind": kind, "text": "t", "new": list(new), "requires": list(requires)}


def test_a_lesson_waits_for_the_one_before_it_in_its_own_strand(tmp_path):
    d = course(tmp_path, [("a", "a-1", 1, [step()]), ("b", "b-1", 1, [step()]), ("a", "a-2", 1, [step()])])
    pre = prerequisites(d)
    assert pre == {"a-1": set(), "b-1": set(), "a-2": {"a-1"}}


def test_a_thought_from_another_strand_needs_that_strands_whole_foundation(tmp_path):
    d = course(tmp_path, [
        ("a", "a-1", 1, [step(new=["x"])]), ("a", "a-2", 1, [step(new=["y"])]), ("a", "a-3", 2, [step(new=["z"])]),
        ("b", "b-1", 1, [step(requires=["x"])])])
    assert prerequisites(d)["b-1"] == {"a-1", "a-2"}


def test_a_thought_from_an_interview_layer_lesson_needs_only_that_lesson(tmp_path):
    d = course(tmp_path, [
        ("a", "a-1", 1, [step(new=["x"])]), ("a", "a-2", 2, [step(new=["z"])]), ("a", "a-3", 2, [step()]),
        ("b", "b-1", 1, [step(requires=["z"])])])
    assert prerequisites(d)["b-1"] == {"a-2"}


def test_what_a_cold_check_borrows_is_not_a_prerequisite(tmp_path):
    d = course(tmp_path, [
        ("a", "a-1", 1, [step(new=["x"])]),
        ("b", "b-1", 1, [step(requires=["x"], kind="cold-check"), step()])])
    assert prerequisites(d)["b-1"] == set()


def test_a_cold_sitting_needs_everything_it_asks(tmp_path):
    d = course(tmp_path, [
        ("a", "a-1", 1, [step(new=["x"])]), ("cold", "c-1", 1, [step(requires=["x"], kind="cold-check")])])
    assert prerequisites(d)["c-1"] == {"a-1"}


def test_a_thought_within_a_strand_adds_nothing_beyond_the_chain(tmp_path):
    d = course(tmp_path, [
        ("a", "a-1", 1, [step(new=["x"])]), ("a", "a-2", 1, [step()]), ("a", "a-3", 1, [step(requires=["x"])])])
    assert prerequisites(d)["a-3"] == {"a-2"}


def test_the_real_course_opens_as_the_owner_asked():
    pre = prerequisites(ROOT / "content")
    sql_foundation = {"sql-01", "sql-02", "sql-03", "sql-04"}
    py_foundation = {f"py-0{i}" for i in range(1, 7)}
    assert pre["sql-05"] == {"sql-04"}                      # the interview layer opens with the foundation
    assert pre["py-01"] == sql_foundation                   # Python imports SQL thoughts
    assert pre["py-07"] == {"py-06"}                        # its opening SQL cold check is only borrowed
    assert pre["pd-01"] == py_foundation | sql_foundation
    assert pre["pd-05"] >= {"pd-04"} and "ml-01" not in pre["pd-05"]
    assert "py-08" in pre["ml-03"] and "py-09" not in pre["ml-03"]
    assert pre["cold-a"] >= sql_foundation | py_foundation | {"pd-04"}
