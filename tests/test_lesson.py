from checker.lesson import load_strand


def test_load_strand_returns_thoughts_and_lessons_in_order(write_strand, thoughts, steps):
    folder = write_strand(steps)
    (folder / "lesson-02.yaml").write_text("lesson: t-02\nsteps: []\n", encoding="utf-8")
    loaded_thoughts, lessons = load_strand(folder)
    assert loaded_thoughts == thoughts
    assert lessons == [("t-01", steps), ("t-02", [])]


import pytest
import yaml

from checker.lesson import is_course, load_content, ui_path


def make_course(root, manifest, strands):
    """strands: {"sql": {"thoughts": {...}, "lessons": {"lesson-01": [steps]}}, ...}"""
    for strand, spec in strands.items():
        (root / strand).mkdir(parents=True)
        (root / strand / "thoughts.yaml").write_text(yaml.safe_dump({"thoughts": spec["thoughts"]}))
        for name, steps in spec["lessons"].items():
            (root / strand / f"{name}.yaml").write_text(
                yaml.safe_dump({"lesson": f"{strand}-{name[-2:]}", "steps": steps}))
    (root / "course.yaml").write_text(yaml.safe_dump({"course": manifest}))
    return root


STEP = {"kind": "recap", "text": "t"}


def test_a_course_interleaves_strands_in_the_order_of_its_manifest(tmp_path):
    make_course(tmp_path, ["sql/lesson-01", "py/lesson-01", "sql/lesson-02"], {
        "sql": {"thoughts": {"a": "x"}, "lessons": {"lesson-01": [STEP], "lesson-02": [STEP]}},
        "py": {"thoughts": {"b": "y"}, "lessons": {"lesson-01": [STEP]}}})
    thoughts, lessons = load_content(tmp_path)
    assert thoughts == {"a": "x", "b": "y"}
    assert [name for name, _ in lessons] == ["sql-01", "py-01", "sql-02"]


def test_a_thought_defined_in_two_strands_is_an_error(tmp_path):
    make_course(tmp_path, ["sql/lesson-01", "py/lesson-01"], {
        "sql": {"thoughts": {"a": "x"}, "lessons": {"lesson-01": [STEP]}},
        "py": {"thoughts": {"a": "y"}, "lessons": {"lesson-01": [STEP]}}})
    with pytest.raises(ValueError, match="'a'.*sql.*py"):
        load_content(tmp_path)


def test_a_manifest_naming_a_lesson_that_is_not_there_is_an_error(tmp_path):
    make_course(tmp_path, ["sql/lesson-01", "sql/lesson-09"], {
        "sql": {"thoughts": {}, "lessons": {"lesson-01": [STEP]}}})
    with pytest.raises(FileNotFoundError):
        load_content(tmp_path)


def test_a_folder_without_a_manifest_is_loaded_as_one_strand(write_strand, steps):
    folder = write_strand(steps)
    assert not is_course(folder)
    _, lessons = load_content(folder)
    assert [name for name, _ in lessons] == ["t-01"]


def test_the_ui_lines_sit_beside_the_manifest_or_above_a_strand(tmp_path):
    make_course(tmp_path, ["sql/lesson-01"], {"sql": {"thoughts": {}, "lessons": {"lesson-01": [STEP]}}})
    assert ui_path(tmp_path) == tmp_path / "ui.yaml"
    assert ui_path(tmp_path / "sql") == tmp_path / "ui.yaml"


def test_a_lesson_can_define_the_thoughts_it_introduces(tmp_path):
    make_course(tmp_path, ["sql/lesson-01", "sql/lesson-02"], {
        "sql": {"thoughts": {"a": "x"}, "lessons": {"lesson-01": [STEP], "lesson-02": [STEP]}}})
    lesson = yaml.safe_load((tmp_path / "sql" / "lesson-02.yaml").read_text())
    lesson["thoughts"] = {"b": "defined in the lesson", "c": {"text": "graded", "grade": "shape"}}
    (tmp_path / "sql" / "lesson-02.yaml").write_text(yaml.safe_dump(lesson))
    thoughts, lessons = load_content(tmp_path)
    assert thoughts == {"a": "x", "b": "defined in the lesson", "c": {"text": "graded", "grade": "shape"}}
    assert [name for name, _ in lessons] == ["sql-01", "sql-02"]


def test_a_thought_defined_twice_across_files_is_an_error(tmp_path):
    make_course(tmp_path, ["sql/lesson-01"], {"sql": {"thoughts": {"a": "x"}, "lessons": {"lesson-01": [STEP]}}})
    lesson = yaml.safe_load((tmp_path / "sql" / "lesson-01.yaml").read_text())
    lesson["thoughts"] = {"a": "again"}
    (tmp_path / "sql" / "lesson-01.yaml").write_text(yaml.safe_dump(lesson))
    with pytest.raises(ValueError, match="'a'"):
        load_content(tmp_path)


def test_a_strand_without_a_thoughts_file_works_if_its_lessons_define_theirs(tmp_path):
    (tmp_path / "py").mkdir()
    (tmp_path / "py" / "lesson-01.yaml").write_text(yaml.safe_dump(
        {"lesson": "py-01", "thoughts": {"d": "from the lesson"}, "steps": [STEP]}))
    (tmp_path / "course.yaml").write_text(yaml.safe_dump({"course": ["py/lesson-01"]}))
    thoughts, _ = load_content(tmp_path)
    assert thoughts == {"d": "from the lesson"}
