import threading

import pytest

from player.sql import fix_quotes, normalise, open_database, run_sql


@pytest.fixture(scope="module")
def db(data_dir):
    return open_database(data_dir)


def test_double_quoted_words_become_text():
    assert fix_quotes('SELECT * FROM couriers WHERE vehicle = "bike"') == \
        "SELECT * FROM couriers WHERE vehicle = 'bike'"


def test_single_quoted_text_is_left_alone():
    assert fix_quotes("WHERE note = 'say \"hi\"'") == "WHERE note = 'say \"hi\"'"


def test_normalise_ignores_case_spacing_quotes_and_semicolon():
    a = normalise('select  count( * ) FROM couriers WHERE vehicle = "bike";')
    assert a == normalise("SELECT COUNT(*) FROM couriers WHERE vehicle = 'bike'")


def test_normalise_keeps_case_inside_quotes():
    assert normalise("WHERE a = 'Bike'") != normalise("WHERE a = 'bike'")


def test_result_is_capped_but_counted(db):
    r = run_sql(db, "SELECT * FROM orders")
    assert r.error is None
    assert r.total == 6000 and len(r.rows) == 20 and len(r.full) == 6000
    assert r.columns[0] == "order_id"
    assert r.item() == {"type": "result", "columns": r.columns, "rows": r.rows, "total": 6000, "error": None}
    assert r.item("Yours")["label"] == "Yours"


def test_double_quoted_word_runs_as_text(db):
    assert run_sql(db, 'SELECT COUNT(*) FROM couriers WHERE vehicle = "bike"').rows == [[73]]


def test_error_is_returned_as_the_databases_own_text(db):
    r = run_sql(db, "SELECT * FROM nowhere")
    assert r.error == "no such table: nowhere"
    assert r.rows == [] and r.total == 0 and r.full == []


@pytest.mark.parametrize("bad", [
    "ATTACH DATABASE 'x.db' AS x",
    "PRAGMA query_only = OFF",
    "DELETE FROM orders",
    "CREATE TABLE t (a)",
])
def test_only_reads_are_allowed(db, bad):
    assert run_sql(db, bad).error is not None


def test_two_statements_are_refused(db):
    assert run_sql(db, "SELECT 1; SELECT 2").error is not None


def test_runaway_query_is_stopped(db):
    r = run_sql(db, "WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM c) SELECT COUNT(*) FROM c",
                timeout=0.2)
    assert r.error == "That took too long, so it was stopped."


def test_database_still_works_after_a_stopped_query(db):
    assert run_sql(db, "SELECT COUNT(*) FROM restaurants").rows == [[60]]


def test_works_from_another_thread(db):
    out = []
    t = threading.Thread(target=lambda: out.append(run_sql(db, "SELECT COUNT(*) FROM couriers").rows))
    t.start()
    t.join()
    assert out == [[[200]]]
