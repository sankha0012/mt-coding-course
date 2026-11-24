"""Run a learner's Python in a separate process, in a folder that holds read-only links to the data.

The core data cannot be changed from here. Each run starts in an empty temporary folder, and the CSV
files in it are links to private read-only copies, never to the originals.

A single long-lived worker process runs every program, so that pandas and scikit-learn are imported
once and not once per answer. Each program gets a fresh namespace. A program that runs too long gets
the worker killed, and the next run starts a new one."""
import atexit
import json
import os
import re
import select
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from functools import cache
from pathlib import Path

_masters = []
_lock = threading.Lock()
_worker = None

_WORKER = r'''
import contextlib, io, json, os, sys, traceback
real = sys.stdout
for name in ("numpy", "pandas", "sklearn.linear_model", "sklearn.ensemble", "sklearn.metrics", "sklearn.model_selection"):
    try:
        __import__(name)
    except Exception:
        pass
print(json.dumps({"ready": True}), file=real, flush=True)
for line in sys.stdin:
    req = json.loads(line)
    os.chdir(req["cwd"])
    out, err = io.StringIO(), None
    saved = sys.stdin
    sys.stdin = io.StringIO("")
    try:
        with contextlib.redirect_stdout(out):
            exec(compile(req["code"], "main.py", "exec"), {"__name__": "__main__"})
    except SystemExit:
        pass
    except BaseException:
        err = traceback.format_exc()
    sys.stdin = saved
    print(json.dumps({"output": out.getvalue(), "error": err}), file=real, flush=True)
'''


@dataclass
class PyResult:
    error: str | None
    output: str

    def item(self, label=None):
        out = {"type": "result", "lang": "python", "text": self.output, "error": self.error}
        if label:
            out["label"] = label
        return out


def _cleanup():
    global _worker
    if _worker is not None:
        _worker.kill()
        _worker = None
    for d in _masters:
        for f in Path(d).glob("*"):
            f.chmod(stat.S_IRUSR | stat.S_IWUSR)
        shutil.rmtree(d, ignore_errors=True)


atexit.register(_cleanup)


@cache
def _master(data_dir):
    """Private read-only copies of the CSV files directly inside data_dir, made once."""
    d = tempfile.mkdtemp(prefix="mt-data-")
    _masters.append(d)
    for f in Path(data_dir).glob("*.csv"):
        shutil.copy(f, d)
        (Path(d) / f.name).chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    return d


def _calm(traceback_text):
    """The last line of an error, with the line number of the learner's code if there is one."""
    lines = [l for l in traceback_text.strip().splitlines() if l.strip()]
    if not lines:
        return "The program stopped."
    where = re.findall(r'File "main\.py", line (\d+)', traceback_text)
    return f"line {where[-1]}: {lines[-1]}" if where else lines[-1]


def _start():
    home = tempfile.mkdtemp(prefix="mt-home-")
    env = {"PATH": os.environ.get("PATH", ""), "HOME": home, "PYTHONHASHSEED": "0", "PYTHONWARNINGS": "ignore"}
    p = subprocess.Popen([sys.executable, "-s", "-c", _WORKER], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, text=True, cwd=home, env=env)
    if not select.select([p.stdout], [], [], 60)[0] or not json.loads(p.stdout.readline()).get("ready"):
        p.kill()
        raise RuntimeError("the Python worker did not start")
    return p


def _ask(code, cwd, timeout):
    """Run code in the worker. Returns the worker's reply, or None if it ran out of time."""
    global _worker
    if _worker is None or _worker.poll() is not None:
        _worker = _start()
    _worker.stdin.write(json.dumps({"code": code, "cwd": cwd}) + "\n")
    _worker.stdin.flush()
    if not select.select([_worker.stdout], [], [], timeout)[0]:
        _worker.kill()
        _worker = None
        return None
    line = _worker.stdout.readline()
    if not line:
        _worker = None
        return {"output": "", "error": "The program stopped."}
    return json.loads(line)


def run_python(code, data_dir, timeout=10):
    if not Path(data_dir).is_dir():
        return PyResult(f"The data folder was not found: {data_dir}", "")
    master = _master(str(Path(data_dir).resolve()))
    with tempfile.TemporaryDirectory(prefix="mt-run-") as tmp:
        for f in Path(master).glob("*.csv"):
            os.symlink(f, Path(tmp) / f.name)
        with _lock:
            reply = _ask(code, tmp, timeout)
    if reply is None:
        return PyResult("That took too long, so it was stopped.", "")
    return PyResult(_calm(reply["error"]) if reply["error"] else None, reply["output"])


def _tokens(text):
    out = []
    for tok in text.split():
        try:
            out.append(repr(round(float(tok), 6)))
        except ValueError:
            out.append(tok)
    return out


def same_output(a, b):
    """Two outputs are the same if they have the same words and numbers, whatever the spacing."""
    return _tokens(a) == _tokens(b)
