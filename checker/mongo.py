"""Run the MongoDB sentences of the course on a real mongod that this program starts for itself. The checker and
the player share it, as they share checker.pyrun for Python.

The server listens on 127.0.0.1 on a spare port, keeps its files in a temporary folder, and is stopped, with the
folder removed, when the program exits. The course collections are loaded from `<data folder>/*.jsonl`.
Course data is only ever read. A sentence that writes runs on a scratch copy that is made for it and dropped
afterwards, so the original data never changes."""
import atexit
import contextlib
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from itertools import islice
from pathlib import Path

from bson import json_util
from bson.regex import Regex
from pymongo import MongoClient
from pymongo.errors import ExecutionTimeout, OperationFailure, PyMongoError

from .data import canon
from .mongoparse import READ_METHODS, WRITE_METHODS, ParseError, forbidden_in, parse

TIMEOUT_MS = 5000
MOST_DOCUMENTS = 50_000
SHOWN = 20


def available():
    """Whether a mongod is installed on this machine."""
    return shutil.which("mongod") is not None


class Unavailable(Exception):
    pass


# A watcher that outlives a program that was killed without time to clean up (a stop signal, a crash): it waits for
# the program or the server to end, then stops the server and removes its folder, so nothing is left running.
_WATCHER = """
import os, shutil, signal, sys, time
parent, child, folder = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True
while alive(parent) and alive(child):
    time.sleep(0.5)
if alive(child):
    os.kill(child, signal.SIGTERM)
    for _ in range(100):
        if not alive(child):
            break
        time.sleep(0.1)
    else:
        os.kill(child, signal.SIGKILL)
shutil.rmtree(folder, ignore_errors=True)
"""


class Server:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.folder = self.port = self.client = self._proc = self._watcher = None
        self._loaded = set()
        self._lock = threading.RLock()

    @property
    def running(self):
        return self._proc is not None and self._proc.poll() is None

    def start(self):
        with self._lock:
            if self.running:
                return
            exe = shutil.which("mongod")
            if exe is None:
                raise Unavailable("MongoDB is not installed on this machine.")
            self.folder = tempfile.mkdtemp(prefix="mt-course-mongo-")
            with socket.socket() as s:
                s.bind(("127.0.0.1", 0))
                self.port = s.getsockname()[1]
            self._proc = subprocess.Popen(
                [exe, "--dbpath", self.folder, "--port", str(self.port), "--bind_ip", "127.0.0.1", "--nounixsocket",
                 "--wiredTigerCacheSizeGB", "0.25"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._watcher = subprocess.Popen(
                [sys.executable, "-c", _WATCHER, str(os.getpid()), str(self._proc.pid), self.folder],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            atexit.register(self.stop)
            client = MongoClient("127.0.0.1", self.port, serverSelectionTimeoutMS=500, connectTimeoutMS=500)
            deadline = time.monotonic() + 40
            while True:
                if self._proc.poll() is not None:
                    self.stop()
                    raise Unavailable("MongoDB did not start.")
                try:
                    client.admin.command("ping")
                    break
                except PyMongoError:
                    if time.monotonic() > deadline:
                        self.stop()
                        raise Unavailable("MongoDB did not start in time.")
                    time.sleep(0.1)
            client.close()
            self.client = MongoClient("127.0.0.1", self.port, socketTimeoutMS=30_000, tz_aware=True)
            self._loaded = set()

    def stop(self):
        with self._lock:
            if self.client is not None:
                self.client.close()
                self.client = None
            if self._proc is not None:
                if self._proc.poll() is None:
                    self._proc.terminate()
                    try:
                        self._proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        self._proc.kill()
                        self._proc.wait()
            if self._watcher is not None:
                self._watcher.terminate()
                self._watcher = None
            if self.folder:
                shutil.rmtree(self.folder, ignore_errors=True)
                self.folder = None
            self._loaded = set()

    @staticmethod
    def _name(dataset):
        return "course_" + (re.sub(r"\W", "_", dataset) or "root")

    def db(self, dataset):
        """The database of a data folder, loaded on first use from its .jsonl files."""
        with self._lock:
            self.start()
            db = self.client[self._name(dataset)]
            if dataset not in self._loaded:
                for f in sorted((self.data_dir / dataset).glob("*.jsonl")):
                    with open(f, encoding="utf-8") as h:
                        docs = [json_util.loads(line) for line in h if line.strip()]
                    if docs:
                        db[f.stem].insert_many(docs)
                self._loaded.add(dataset)
            return db

    @contextlib.contextmanager
    def scratch(self, dataset):
        """A copy of the dataset's collections that lives for one sentence."""
        src = self.db(dataset)
        name = "scratch_" + uuid.uuid4().hex[:10]
        try:
            for coll in src.list_collection_names():
                list(src[coll].aggregate([{"$out": {"db": name, "coll": coll}}]))
            yield self.client[name]
        finally:
            self.client.drop_database(name)


_servers = {}


def server_for(data_dir):
    """One server for each data folder of this program, shared by the player and the checker."""
    key = str(Path(data_dir).resolve())
    if key not in _servers:
        _servers[key] = Server(data_dir)
    return _servers[key]


# ---- results

def _cv(v):
    """A value in a form that compares equal when the results are the same."""
    if isinstance(v, bool) or v is None or isinstance(v, (int, str)):
        return v
    if isinstance(v, float):
        return round(v, 6)
    if isinstance(v, datetime):
        return v.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if v.tzinfo else v.strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(v, dict):
        return tuple(sorted(((k, _cv(x)) for k, x in v.items()), key=lambda kv: kv[0]))
    if isinstance(v, (list, tuple)):
        return tuple(_cv(x) for x in v)
    if isinstance(v, Regex):
        return f"/{v.pattern}/"
    try:
        return float(v.to_decimal())  # Decimal128
    except AttributeError:
        return str(v)


def to_rows(value):
    """What a sentence gave, as rows of values. A document is a row, and its field names are not kept: a
    computed field may be called anything. Names inside a nested document are kept."""
    if value is None:
        return []
    if isinstance(value, dict):
        return [tuple(_cv(v) for v in value.values())]
    if isinstance(value, list):
        return [tuple(_cv(v) for v in x.values()) if isinstance(x, dict) else (_cv(x),) for x in value]
    return [(_cv(value),)]


def plain(v):
    """A value as the screen shows it: dates as text, ids as text."""
    if isinstance(v, dict):
        return {k: plain(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [plain(x) for x in v]
    if isinstance(v, datetime):
        return _cv(v)
    if isinstance(v, (bool, int, float, str)) or v is None:
        return v
    return str(v)


class MongoResult:
    def __init__(self, error, rows=None, docs=None):
        self.error, self.full, self.docs = error, rows or [], docs or []

    @property
    def total(self):
        return len(self.full)

    def key(self, flags):
        """What two results are compared by: the values, in the row order the step cares about."""
        return canon(self.full, any_column_order=True, ordered=bool(flags.get("ordered")))

    def item(self, label=None):
        out = {"type": "result", "lang": "mongo", "docs": [plain(d) for d in self.docs[:SHOWN]],
               "total": self.total, "error": self.error}
        if label:
            out["label"] = label
        return out


# ---- running a sentence

def _arg(args, i, kind, default=None):
    if len(args) <= i:
        return default
    if not isinstance(args[i], kind):
        raise ParseError(f"Argument {i + 1} of this call has the wrong shape.")
    return args[i]


def _find(coll, call):
    cur = coll.find(_arg(call.args, 0, dict, {}), _arg(call.args, 1, dict), max_time_ms=TIMEOUT_MS,
                    batch_size=MOST_DOCUMENTS)
    for name, a in call.mods:
        if name == "sort":
            cur = cur.sort(list(_arg(a, 0, dict, {}).items()))
        elif name == "limit":
            cur = cur.limit(_arg(a, 0, int, 0))
        elif name == "skip":
            cur = cur.skip(_arg(a, 0, int, 0))
    docs = list(islice(cur, MOST_DOCUMENTS + 1))
    if len(docs) > MOST_DOCUMENTS:
        raise ParseError(f"That gives more than {MOST_DOCUMENTS:,} documents. Narrow it down, or add .limit().")
    return docs


def _write(coll, call):
    m, a = call.method, call.args
    if m == "insertOne":
        return {"acknowledged": True, "insertedId": coll.insert_one(_arg(a, 0, dict)).inserted_id}
    if m == "insertMany":
        return {"acknowledged": True, "insertedIds": coll.insert_many(_arg(a, 0, list)).inserted_ids}
    if m in ("updateOne", "updateMany"):
        upsert = bool(_arg(a, 2, dict, {}).get("upsert"))
        fn = coll.update_one if m == "updateOne" else coll.update_many
        r = fn(_arg(a, 0, dict), _arg(a, 1, (dict, list)), upsert=upsert)
        return {"acknowledged": True, "matchedCount": r.matched_count, "modifiedCount": r.modified_count,
                "upsertedCount": 1 if r.upserted_id is not None else 0}
    fn = coll.delete_one if m == "deleteOne" else coll.delete_many
    return {"acknowledged": True, "deletedCount": fn(_arg(a, 0, dict)).deleted_count}


def _execute(db, call):
    coll, m, a = db[call.collection], call.method, call.args
    if m == "find":
        return _find(coll, call)
    if m == "findOne":
        return coll.find_one(_arg(a, 0, dict, {}), _arg(a, 1, dict), max_time_ms=TIMEOUT_MS)
    if m == "countDocuments":
        return coll.count_documents(_arg(a, 0, dict, {}), maxTimeMS=TIMEOUT_MS)
    if m == "estimatedDocumentCount":
        return coll.estimated_document_count(maxTimeMS=TIMEOUT_MS)
    if m == "distinct":
        return coll.distinct(_arg(a, 0, str), _arg(a, 1, dict, {}), maxTimeMS=TIMEOUT_MS)
    if m == "aggregate":
        # one big first batch, so that the time limit covers all the work and not only the first hundred documents
        return list(coll.aggregate(_arg(a, 0, list), maxTimeMS=TIMEOUT_MS, batchSize=MOST_DOCUMENTS))
    return _write(coll, call)


def run_mongo(server, dataset, text, scratch=False):
    """One sentence. Returns a MongoResult, with an error message if it could not be run: the server's own
    words for a server error, and a calm line for anything else."""
    try:
        call = parse(text)
        bad = forbidden_in(call.args)
        if bad:
            return MongoResult(f"`{bad}` is not part of this course, so it is not run.")
        if call.method not in READ_METHODS | WRITE_METHODS:
            return MongoResult(f"`{call.method}` is not one of the methods of this course.")
        if call.mods and call.method != "find":
            return MongoResult("`.sort()`, `.limit()` and `.skip()` go after `find`.")
        writes = call.method in WRITE_METHODS
        if writes and not scratch:
            return MongoResult("That would change data. The course data is never changed, "
                               "so a sentence like this can run only on a scratch copy.")
        if writes:
            with server.scratch(dataset) as db:
                value = _execute(db, call)
        else:
            value = _execute(server.db(dataset), call)
    except ParseError as e:
        return MongoResult(str(e))
    except Unavailable as e:
        return MongoResult(f"{e} The MongoDB lessons need it.")
    except ExecutionTimeout:
        return MongoResult("That took too long, so it was stopped.")
    except OperationFailure as e:
        msg = (e.details or {}).get("errmsg") or str(e)
        return MongoResult("That took too long, so it was stopped." if "time limit" in msg else msg)
    except (PyMongoError, ValueError, TypeError) as e:  # the driver's own words, e.g. an update without a $ operator
        return MongoResult(str(e))
    docs = value if isinstance(value, list) else ([] if value is None else [value])
    return MongoResult(None, to_rows(value), docs)
