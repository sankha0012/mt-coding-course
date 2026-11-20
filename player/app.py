import random
import threading
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from checker.lesson import load_strand

from .engine import Engine
from .sql import open_database
from .store import Store

WEB = Path(__file__).parent / "web"


class Conflict(Exception):
    pass


class Player:
    """Joins the engine, the database and the progress file."""

    def __init__(self, content_dir, data_dir, progress_dir, rng=None):
        content = Path(content_dir)
        self.thoughts, lessons = load_strand(content)
        self.lesson, self.steps = lessons[0]
        ui = yaml.safe_load((content.parent / "ui.yaml").read_text(encoding="utf-8"))
        self.engine = Engine(self.steps, open_database(data_dir), ui, rng or random.Random())
        self.store = Store(progress_dir)
        self.lock = threading.Lock()

    def _current(self):
        return self.store.latest(self.lesson) or self._start()

    def _start(self):
        st, items, _ = self.engine.start()
        return self.store.new_run(self.lesson, st, items, finished=st["phase"] == "done"), st

    def _view(self, run_id, st):
        return {"run_id": run_id, "items": self.store.items(run_id), "pending": self.engine.pending(st)}

    def view(self):
        with self.lock:
            return self._view(*self._current())

    def answer(self, text):
        with self.lock:
            run_id, st = self._current()
            if st["phase"] != "answer":
                raise Conflict("not waiting for an answer")
            st, items, events = self.engine.answer(st, text)
            self.store.apply(run_id, st, items, events, finished=st["phase"] == "done")
            return self._view(run_id, st)

    def next(self):
        with self.lock:
            run_id, st = self._current()
            if st["phase"] not in ("run", "continue"):
                raise Conflict("nothing to continue")
            st, items, events = self.engine.advance(st)
            self.store.apply(run_id, st, items, events, finished=st["phase"] == "done")
            return self._view(run_id, st)

    def new_run(self):
        with self.lock:
            if self._current()[1]["phase"] != "done":
                raise Conflict("the sitting is not over")
            return self._view(*self._start())


class Answer(BaseModel):
    sql: str


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

    @app.post("/api/run/new")
    def post_new():
        return player.new_run()

    @app.get("/")
    def index():
        return FileResponse(WEB / "index.html")

    app.mount("/static", StaticFiles(directory=WEB), name="static")
    return app
