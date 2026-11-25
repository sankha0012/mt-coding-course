from player.tables import sample


def write(folder, name, text):
    (folder / name).write_text(text, encoding="utf-8")


def test_a_table_has_its_columns_first_rows_and_true_total(tmp_path):
    write(tmp_path, "a.csv", "x,y\n" + "".join(f"{i},{i * 2}\n" for i in range(25)))
    [t] = sample(tmp_path)
    assert t["name"] == "a" and t["columns"] == ["x", "y"]
    assert len(t["rows"]) == 10 and t["rows"][0] == ["0", "0"] and t["rows"][9] == ["9", "18"]
    assert t["total"] == 25


def test_a_short_table_shows_all_its_rows(tmp_path):
    write(tmp_path, "a.csv", "x\n1\n2\n")
    [t] = sample(tmp_path)
    assert t["rows"] == [["1"], ["2"]] and t["total"] == 2


def test_empty_cells_are_none(tmp_path):
    write(tmp_path, "a.csv", "x,y\n1,\n,2\n")
    [t] = sample(tmp_path)
    assert t["rows"] == [["1", None], [None, "2"]]


def test_a_quoted_line_break_is_one_row(tmp_path):
    write(tmp_path, "a.csv", 'x,note\n1,"two\nlines"\n2,ok\n')
    [t] = sample(tmp_path)
    assert t["total"] == 2 and t["rows"][0] == ["1", "two\nlines"]


def test_only_csv_files_of_the_folder_itself_count(tmp_path):
    write(tmp_path, "b.csv", "x\n1\n")
    write(tmp_path, "a.csv", "x\n1\n")
    write(tmp_path, "notes.txt", "x\n")
    (tmp_path / "sub").mkdir()
    write(tmp_path / "sub", "c.csv", "x\n1\n")
    assert [t["name"] for t in sample(tmp_path)] == ["a", "b"]


def test_file_names_keep_the_extension_when_asked(tmp_path):
    write(tmp_path, "a.csv", "x\n1\n")
    assert sample(tmp_path, ext=True)[0]["name"] == "a.csv"


# ---- MongoDB collections: a .jsonl file is a collection of documents

import json  # noqa: E402

from player.tables import documents  # noqa: E402


def write_docs(folder, name, docs):
    (folder / name).write_text("".join(json.dumps(d) + "\n" for d in docs), encoding="utf-8")


def test_a_collection_shows_its_count_and_its_first_three_documents(tmp_path):
    write_docs(tmp_path, "orders.jsonl", [{"_id": i, "n": {"a": i}} for i in range(10)])
    [c] = documents(tmp_path)
    assert c["name"] == "orders" and c["total"] == 10
    assert c["docs"] == [{"_id": 0, "n": {"a": 0}}, {"_id": 1, "n": {"a": 1}}, {"_id": 2, "n": {"a": 2}}]
    assert c["columns"] == [] and c["rows"] == []


def test_dates_in_a_collection_are_shown_as_text(tmp_path):
    write_docs(tmp_path, "a.jsonl", [{"_id": 1, "at": {"$date": "2026-08-01T10:30:00Z"}}])
    assert documents(tmp_path)[0]["docs"] == [{"_id": 1, "at": "2026-08-01T10:30:00Z"}]


def test_only_jsonl_files_count_as_collections(tmp_path):
    write_docs(tmp_path, "b.jsonl", [{"_id": 1}])
    write_docs(tmp_path, "a.jsonl", [{"_id": 1}])
    (tmp_path / "x.csv").write_text("x\n1\n", encoding="utf-8")
    assert [c["name"] for c in documents(tmp_path)] == ["a", "b"]
