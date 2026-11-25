import re
from pathlib import Path

from checker import mongo
from checker.pyrun import output_key, run_python

from .sql import Result, open_database, run_sql


class PyRun:
    """A Python answer run twice: alone, to show the learner what it printed, and with the step's hidden
    check code after it, to judge it. With no check the two are one run."""

    def __init__(self, shown, judged):
        self.shown, self.judged = shown, judged
        # an error in the check, not in the learner's own code, is shown without a line number
        self.error = shown.error or (re.sub(r"^line \d+: ", "", judged.error) if judged.error else None)

    def key(self, flags):
        return output_key(self.judged.output)

    def item(self, label=None):
        out = {"type": "result", "lang": "python", "text": self.shown.output, "error": self.error}
        if label:
            out["label"] = label
        return out


class Runner:
    """Runs one sentence of a step in the step's language, on the data folder the step names.

    SQL runs read-only on an in-memory copy. Python runs in the sandbox of checker.pyrun. Neither can
    change the core data."""

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self._dbs = {}

    def path(self, dataset=""):
        return self.data_dir / dataset if dataset else self.data_dir

    def available(self, dataset="", lang="sql"):
        """Whether a step in this language can run on this machine: its data folder is here, and for MongoDB,
        so is a mongod."""
        return self.path(dataset).is_dir() and (lang != "mongo" or mongo.available())

    def _db(self, dataset):
        if dataset not in self._dbs:
            self._dbs[dataset] = open_database(self.path(dataset))
        return self._dbs[dataset]

    def run(self, step, code, check=True):
        dataset, lang = step.get("data", ""), step.get("lang", "sql")
        if not self.path(dataset).is_dir():
            return Result(f"The data folder was not found: {dataset or self.data_dir}", [], [], 0)
        if lang == "mongo":
            if not mongo.available():
                return mongo.MongoResult("MongoDB is not installed on this machine. The MongoDB lessons need it.")
            return mongo.run_mongo(mongo.server_for(self.data_dir), dataset, code, scratch=bool(step.get("scratch")))
        if lang == "python":
            shown = run_python(code, self.path(dataset))
            if check and step.get("check"):
                return PyRun(shown, run_python(code + "\n" + step["check"], self.path(dataset)))
            return PyRun(shown, shown)
        return run_sql(self._db(dataset), code)

    def play(self, lang, code, dataset=""):
        """The learner's own code in the try-it panel: shown, never judged, never logged."""
        # the try-it panel may write in MongoDB, on a scratch copy that is dropped afterwards
        return self.run({"lang": lang, "data": dataset, "scratch": True}, code, check=False).item()
