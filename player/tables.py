import csv
from pathlib import Path

from bson import json_util

from checker.mongo import plain


def sample(folder, ext=False, limit=10):
    """The tables of a folder: name, columns, the first rows and the true row count. Empty cells are None."""
    out = []
    for f in sorted(Path(folder).glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as h:
            reader = csv.reader(h)
            columns = next(reader, [])
            rows, total = [], 0
            for r in reader:
                if not r:
                    continue
                total += 1
                if total <= limit:
                    rows.append([v if v != "" else None for v in r])
        out.append({"name": f.name if ext else f.stem, "columns": columns, "rows": rows, "total": total})
    return out


def documents(folder, limit=3):
    """The collections of a folder, each a .jsonl file with one document to a line: its name, how many documents,
    and the first few as the screen shows them."""
    out = []
    for f in sorted(Path(folder).glob("*.jsonl")):
        docs, total = [], 0
        with open(f, encoding="utf-8") as h:
            for line in h:
                if not line.strip():
                    continue
                total += 1
                if total <= limit:
                    docs.append(plain(json_util.loads(line)))
        out.append({"name": f.stem, "columns": [], "rows": [], "total": total, "docs": docs})
    return out
