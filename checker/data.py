import csv
import sqlite3
from pathlib import Path


def _column_type(values):
    cells = [v for v in values if v != ""]
    for cast, sql_type in ((int, "INTEGER"), (float, "REAL")):
        try:
            for v in cells:
                cast(v)
            return cast, sql_type
        except ValueError:
            pass
    return str, "TEXT"


def load_db(data_dir, check_same_thread=True, max_bytes=30_000_000):
    """Build an in-memory database from the CSV files in data_dir. Empty cells become NULL.
    A file over max_bytes is left out of the database (Python can still read it)."""
    conn = sqlite3.connect(":memory:", check_same_thread=check_same_thread)
    for path in sorted(Path(data_dir).glob("*.csv")):
        if path.stat().st_size > max_bytes:
            continue
        with open(path, newline="", encoding="utf-8") as f:
            header, *body = csv.reader(f)
        types = [_column_type(col) for col in zip(*body)]
        cols = ", ".join(f'"{h}" {t}' for h, (_, t) in zip(header, types))
        conn.execute(f'CREATE TABLE "{path.stem}" ({cols})')
        marks = ", ".join("?" * len(header))
        conn.executemany(
            f'INSERT INTO "{path.stem}" VALUES ({marks})',
            ([None if v == "" else cast(v) for v, (cast, _) in zip(row, types)] for row in body),
        )
    conn.execute("PRAGMA query_only = ON")
    return conn


def run(conn, sql):
    return conn.execute(sql).fetchall()


def canon(rows, any_column_order=False, ordered=False, ndigits=6):
    """Rows in a form that compares equal when the results are the same."""
    out = [tuple(round(v, ndigits) if isinstance(v, float) else v for v in row) for row in rows]
    if any_column_order:
        out = [tuple(sorted(row, key=repr)) for row in out]
    return out if ordered else sorted(out, key=repr)


def same_rows(a, b, **flags):
    return canon(a, **flags) == canon(b, **flags)
