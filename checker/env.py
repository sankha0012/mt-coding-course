import sqlite3
from pathlib import Path

from . import mongo
from .data import load_db


class Env:
    """Where a step's sentences run: an SQL database and the Python sandbox, for each data folder.

    A step names its data folder with `data`, relative to data_dir. The default is data_dir itself."""

    def __init__(self, data_dir=None, conn=None):
        self.data_dir = Path(data_dir) if data_dir is not None else None
        self._conns = {"": conn} if conn is not None else {}

    def path(self, dataset=""):
        return self.data_dir / dataset if dataset else self.data_dir

    def available(self, dataset="", lang="sql"):
        """Whether a step can run here: its data folder is present, and for MongoDB so is a mongod."""
        if lang == "mongo" and not mongo.available():
            return False
        if dataset in self._conns:
            return True
        return self.data_dir is not None and self.path(dataset).is_dir()

    def mongo(self):
        return mongo.server_for(self.data_dir)

    def sql(self, dataset=""):
        if dataset not in self._conns:
            self._conns[dataset] = load_db(self.path(dataset))
        return self._conns[dataset]


def as_env(x):
    """Accept an Env, or a bare SQLite connection, which is what the older tests pass."""
    return x if isinstance(x, Env) else Env(conn=x)
