from player import ai

UI = {"ask_persona": "PERSONA. Never write the answer."}


def test_thought_lines_keep_order_and_skip_unknown():
    thoughts = {"a": "Count rows.", "b": {"text": "Sort rows.", "grade": "shape"}}
    assert ai.thought_lines(thoughts, ["b", "zzz", "a"]) == ["Sort rows.", "Count rows."]


def test_schema_lines_name_files_and_columns_only(tmp_path):
    (tmp_path / "orders.csv").write_text("order_id,subtotal\n1,9.5\n2,7\n")
    (tmp_path / "notes.txt").write_text("ignored")
    assert ai.schema_lines(tmp_path) == ["orders: order_id, subtotal"]


def test_attempt_text_for_sql_and_for_python():
    sql = [{"type": "teacher", "text": "t"}, {"type": "learner", "sql": "SELECT 1", "lang": "sql"},
           {"type": "result", "columns": ["x"], "rows": [[1]], "total": 1}]
    text = ai.attempt_text(sql)
    assert "SELECT 1" in text and "x" in text and "1" in text
    py = [{"type": "learner", "sql": "print(1)", "lang": "python"},
          {"type": "result", "lang": "python", "text": "1\n", "error": None}]
    assert "print(1)" in ai.attempt_text(py) and "1" in ai.attempt_text(py)
    err = [{"type": "learner", "sql": "SELECT", "lang": "sql"},
           {"type": "result", "error": "no such column", "columns": [], "rows": [], "total": 0}]
    assert "no such column" in ai.attempt_text(err)
    assert ai.attempt_text([{"type": "teacher", "text": "t"}]) == ""


def test_the_messages_carry_the_context_in_the_system_message():
    msgs = ai.build_messages(UI, ["Count rows."], ["Welcome.", "How many?"], "How many couriers?",
                             "SELECT 1", ["couriers: city"], [], "what is count?")
    system = msgs[0]["content"]
    assert msgs[0]["role"] == "system"
    for part in ("PERSONA", "Count rows.", "Welcome.", "How many couriers?", "SELECT 1", "couriers: city"):
        assert part in system
    assert msgs[-1] == {"role": "user", "content": "what is count?"}


def test_the_thread_comes_between_the_system_message_and_the_question():
    thread = [{"role": "user", "text": "q1"}, {"role": "teacher", "text": "a1"}]
    msgs = ai.build_messages(UI, [], [], "p", "", [], thread, "q2")
    assert [m["role"] for m in msgs] == ["system", "user", "assistant", "user"]
    assert [m["content"] for m in msgs[1:]] == ["q1", "a1", "q2"]


def test_no_attempt_leaves_that_part_out():
    msgs = ai.build_messages(UI, [], [], "p", "", [], [], "q")
    assert "attempt" not in msgs[0]["content"]


def test_code_candidates_find_fences_and_inline_spans():
    reply = "Try this:\n```sql\nSELECT 1\n```\nor `SELECT 2` too. Also ```SELECT 3```."
    assert ai.code_candidates(reply)[:2] == ["SELECT 1", "SELECT 2"]
    assert "SELECT 3" in ai.code_candidates(reply)
    assert ai.code_candidates("no code here") == []
