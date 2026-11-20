import sqlite3
import threading

import pytest

from checker.data import load_db, run, same_rows


def test_tables_load_with_expected_sizes(conn):
    assert run(conn, "SELECT COUNT(*) FROM orders") == [(6000,)]
    assert run(conn, "SELECT COUNT(*) FROM restaurants") == [(60,)]
    assert run(conn, "SELECT COUNT(*) FROM couriers") == [(200,)]


def test_empty_cells_are_null_and_numbers_are_numbers(conn):
    assert run(conn, "SELECT COUNT(*) FROM orders WHERE subtotal IS NULL") == [(25,)]
    assert run(conn, "SELECT typeof(subtotal) FROM orders WHERE subtotal IS NOT NULL LIMIT 1") == [("real",)]
    assert run(conn, "SELECT typeof(order_id) FROM orders LIMIT 1") == [("integer",)]
    assert run(conn, "SELECT typeof(city) FROM restaurants LIMIT 1") == [("text",)]


def test_database_is_read_only(conn):
    with pytest.raises(sqlite3.OperationalError):
        conn.execute("DELETE FROM orders")


def test_row_order_is_ignored_unless_ordered():
    assert same_rows([(1,), (2,)], [(2,), (1,)])
    assert not same_rows([(1,), (2,)], [(2,), (1,)], ordered=True)


def test_floats_compare_after_rounding():
    assert same_rows([(0.1 + 0.2,)], [(0.3,)])
    assert same_rows([(60.3992,)], [(60.4,)], ndigits=2)
    assert not same_rows([(60.3992,)], [(60.4,)])


def test_column_order_matters_unless_any_column_order():
    assert not same_rows([("a", 1)], [(1, "a")])
    assert same_rows([("a", 1)], [(1, "a")], any_column_order=True)


def test_connection_can_be_used_from_another_thread(data_dir):
    conn = load_db(data_dir, check_same_thread=False)
    out = []
    t = threading.Thread(target=lambda: out.append(run(conn, "SELECT COUNT(*) FROM couriers")))
    t.start()
    t.join()
    assert out == [[(200,)]]
