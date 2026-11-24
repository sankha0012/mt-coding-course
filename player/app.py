import logging
import random
import threading
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from checker.lesson import load_content, ui_path

from . import ai, llm
from .engine import Engine
from .runner import Runner
from .store import Store

WEB = Path(__file__).parent / "web"


class Conflict(Exception):
    pass


class Player:
    """Joins the engines, the database and the progress file. Plays the lessons of a folder in order."""

    def __init__(self, content_dir, data_dir, progress_dir, rng=None, chat=None):
        content = Path(content_dir)
        self.thoughts, lessons = load_content(content)
        ui = yaml.safe_load(ui_path(content).read_text(encoding="utf-8"))
        self.ui, self.chat = ui, chat or llm.chat
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

    def _met(self, name, st):
        """Ids of the thoughts introduced up to the step now playing, in course order."""
        ids = []
        for lesson, steps in self.lessons:
            upto = st["playing"]["step"] + 1 if lesson == name else len(steps)
            ids += [t for s in steps[:upto] for t in s.get("new", [])]
            if lesson == name:
                break
        return list(dict.fromkeys(ids))

    def ask(self, question, thread, provider=None):
        """A side question. The lesson is not touched: no state, no ladder, no event. Only the question
        and its reply are kept. The model sees only what the learner has already seen."""
        with self.lock:
            run_id, name, st = self._current()
            eng = self.engines[name]
            step = eng.steps[st["playing"]["step"]]
            items = self.store.items(run_id)
            teacher = [i["text"] for i in items if i["type"] == "teacher"]
            messages = ai.build_messages(
                self.ui, ai.thought_lines(self.thoughts, self._met(name, st)), teacher,
                teacher[-1] if teacher else "",
                ai.attempt_text(items) if st["phase"] == "answer" and st["misses"] else "",
                ai.schema_lines(self.runner.path(step.get("data", ""))), thread, question)
        try:  # the lock is free while the model thinks
            reply, used = self.chat(messages, provider=provider)
        except llm.Unavailable as e:
            logging.getLogger("uvicorn.error").warning("ask failed: %s", e)
            return {"reply": self.ui["ask_unavailable"], "ok": False}
        with self.lock:
            # st is the step that was asked about, even if the learner has moved on since
            guarded = any(eng.solves(st, code) for code in ai.code_candidates(reply))
            if guarded:
                reply = self.ui["ask_guarded"]
            self.store.add_question(run_id, st["playing"]["step"] + 1, question, reply, used, guarded)
        return {"reply": reply, "ok": True, "guarded": guarded}

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


class Ask(BaseModel):
    question: str
    thread: list[dict] = []
    provider: str | None = None


class NewRun(BaseModel):
    next: bool = False


class Play(BaseModel):
    lang: str
    code: str


def make_app(content_dir, data_dir, progress_dir, rng=None, chat=None, providers=None):
    player = Player(content_dir, data_dir, progress_dir, rng, chat)
    providers = providers or llm.available
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

    @app.get("/api/providers")
    def get_providers():
        return {"providers": providers()}

    @app.post("/api/ask")
    def post_ask(a: Ask):
        question = a.question.strip()
        if not question or len(question) > 2000:
            raise HTTPException(400, "empty or too long")
        if a.provider is not None and a.provider not in llm.PROVIDERS:
            raise HTTPException(400, "unknown provider")
        thread = [{"role": str(m.get("role")), "text": str(m.get("text", ""))[:2000]} for m in a.thread[-10:]]
        return player.ask(question, thread, a.provider)

    @app.post("/api/run/new")
    def post_new(body: NewRun | None = None):
        return player.new_run(go_next=bool(body and body.next))

    @app.middleware("http")
    async def revalidate(request, call_next):
        # local app: always check for a newer page, so an edit shows at once
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache"
        return response

    @app.get("/")
    def index():
        return FileResponse(WEB / "index.html")

    app.mount("/static", StaticFiles(directory=WEB), name="static")
    return app
