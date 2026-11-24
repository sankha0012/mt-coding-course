import random
import threading
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from checker.lesson import load_content, ui_path

from .engine import Engine
from .runner import Runner
from .store import Store

WEB = Path(__file__).parent / "web"


class Conflict(Exception):
    pass


class Player:
    """Joins the engines, the database and the progress file. Plays the lessons of a folder in order."""

    def __init__(self, content_dir, data_dir, progress_dir, rng=None):
        content = Path(content_dir)
        self.thoughts, lessons = load_content(content)
        ui = yaml.safe_load(ui_path(content).read_text(encoding="utf-8"))
        self.runner, rng = Runner(data_dir), rng or random.Random()
        # a lesson whose data folder is not on this machine is left out, and said so at start up
        self.lessons = [(n, s) for n, s in lessons if all(self.runner.available(x.get("data", "")) for x in s)]
        self.skipped = [n for n, _ in lessons if n not in {m for m, _ in self.lessons}]
        self.names = [name for name, _ in self.lessons]
        self.engines = {name: Engine(steps, self.runner, ui, rng) for name, steps in self.lessons}
        self.store = Store(progress_dir)
        self.lock = threading.Lock()

    def _current(self):
        """(run id, lesson name, state) of the newest run, starting the first lesson if there is none."""
        return self.store.latest_any() or self._start(self.names[0])

    def _start(self, name):
        st, items, _ = self.engines[name].start()
        return self.store.new_run(name, st, items, finished=st["phase"] == "done"), name, st

    def _view(self, run_id, name, st):
        pending = self.engines[name].pending(st)
        if pending["mode"] == "done":
            pending["next"] = self.names.index(name) + 1 < len(self.names)
        return {"run_id": run_id, "lesson": name, "items": self.store.items(run_id), "pending": pending}

    def view(self):
        with self.lock:
            return self._view(*self._current())

    def answer(self, text):
        with self.lock:
            run_id, name, st = self._current()
            if st["phase"] != "answer":
                raise Conflict("not waiting for an answer")
            st, items, events = self.engines[name].answer(st, text)
            self.store.apply(run_id, st, items, events, finished=st["phase"] == "done")
            return self._view(run_id, name, st)

    def next(self):
        with self.lock:
            run_id, name, st = self._current()
            if st["phase"] not in ("run", "continue"):
                raise Conflict("nothing to continue")
            st, items, events = self.engines[name].advance(st)
            self.store.apply(run_id, st, items, events, finished=st["phase"] == "done")
            return self._view(run_id, name, st)

    def play(self, lang, code):
        """The try-it panel: the learner's own code on the data of the step being played. Not logged."""
        with self.lock:
            _, name, st = self._current()
            step = self.engines[name].steps[st["playing"]["step"]]
            return self.runner.play(lang, code, step.get("data", ""))

    def new_run(self, go_next=False):
        """After a finished lesson: sit it again, or start the next one."""
        with self.lock:
            _, name, st = self._current()
            if st["phase"] != "done":
                raise Conflict("the sitting is not over")
            if go_next:
                i = self.names.index(name) + 1
                if i >= len(self.names):
                    raise Conflict("there is no next lesson")
                name = self.names[i]
            return self._view(*self._start(name))


class Answer(BaseModel):
    sql: str


class NewRun(BaseModel):
    next: bool = False


class Play(BaseModel):
    lang: str
    code: str


def make_app(content_dir, data_dir, progress_dir, rng=None):
    player = Player(content_dir, data_dir, progress_dir, rng)
    app = FastAPI()

    @app.exception_handler(Conflict)
    def conflict(_, exc):
        return JSONResponse({"detail": str(exc)}, status_code=409)

    @app.get("/api/run")
    def get_run():
        return player.view()

    @app.post("/api/answer")
    def post_answer(a: Answer):
        if not a.sql.strip():
            raise HTTPException(400, "empty answer")
        return player.answer(a.sql)

    @app.post("/api/next")
    def post_next():
        return player.next()

    @app.post("/api/play")
    def post_play(p: Play):
        if p.lang not in ("sql", "python"):
            raise HTTPException(400, "unknown language")
        if not p.code.strip():
            raise HTTPException(400, "empty code")
        return player.play(p.lang, p.code)

    @app.post("/api/run/new")
    def post_new(body: NewRun | None = None):
        return player.new_run(go_next=bool(body and body.next))

    @app.get("/")
    def index():
        return FileResponse(WEB / "index.html")

    app.mount("/static", StaticFiles(directory=WEB), name="static")
    return app
