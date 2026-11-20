from checker.lesson import load_strand


def test_load_strand_returns_thoughts_and_lessons_in_order(write_strand, thoughts, steps):
    folder = write_strand(steps)
    (folder / "lesson-02.yaml").write_text("lesson: t-02\nsteps: []\n", encoding="utf-8")
    loaded_thoughts, lessons = load_strand(folder)
    assert loaded_thoughts == thoughts
    assert lessons == [("t-01", steps), ("t-02", [])]
