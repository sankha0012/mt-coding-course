import csv
from pathlib import Path


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
