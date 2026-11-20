import copy

from checker.data import same_rows

from .sql import normalise, run_sql


def _teacher(text, style=None):
    item = {"type": "teacher", "text": text}
    if style:
        item["style"] = style
    return item


class Engine:
    """The sitting as a state machine. It knows neither the web nor the progress file."""

    def __init__(self, steps, conn, ui, rng):
        self.steps, self.conn, self.ui, self.rng = steps, conn, ui, rng
        self._cache = {}

    # ---- public

    def start(self):
        st = {"pos": 0, "phase": "continue", "playing": {"step": 0, "variant": "main"},
              "misses": 0, "rung": 0, "why": None, "queue": [], "returned": [],
              "last_narration": None, "last_ui": {}}
        items = []
        self._enter(st, items)
        return st, items, []

    def pending(self, st):
        phase, step = st["phase"], st["playing"]["step"]
        if phase == "run":
            return {"mode": "run", "sql": self.steps[step]["shows"][-1]}
        if phase == "answer":
            return {"mode": "answer", "step": step + 1, "variant": st["playing"]["variant"]}
        return {"mode": phase}

    def advance(self, state):
        st, items = copy.deepcopy(state), []
        cur = self.steps[st["playing"]["step"]]
        if st["phase"] == "run":
            sql = cur["shows"][-1]
            items += [{"type": "learner", "sql": sql}, run_sql(self.conn, sql).item()]
            if cur.get("after_run"):
                items.append(_teacher(cur["after_run"].strip()))
            st["phase"] = "continue"
        elif st["phase"] == "continue":
            if st["playing"]["variant"] == "main":
                st["pos"] = st["playing"]["step"] + 1
            self._enter(st, items)
        else:
            raise ValueError("nothing to continue")
        return st, items, []

    def answer(self, state, text):
        st = copy.deepcopy(state)
        if st["phase"] != "answer":
            raise ValueError("not waiting for an answer")
        cur, step, variant = self._cur(st), st["playing"]["step"], st["playing"]["variant"]
        res = run_sql(self.conn, text)
        items = [{"type": "learner", "sql": text}, res.item()]
        before = st["misses"]

        def event(outcome):
            return {"step": step + 1, "variant": variant, "typed": text, "outcome": outcome, "misses": before}

        if self._correct(cur, res):
            outcome = self._on_correct(st, cur, step, variant, text, items)
            return st, items, [event(outcome)]
        return st, items, [event("miss")]

    # ---- moving through the lesson

    def _enter(self, st, items):
        j = st["pos"]
        if j >= len(self.steps):
            st["phase"] = "done"
            return
        self._begin_step(st, items, j)

    def _begin_step(self, st, items, j):
        s = self.steps[j]
        st.update(playing={"step": j, "variant": "main"}, misses=0, rung=0, why=None)
        style = s["kind"] if s.get("kind") in ("aside", "recap") else None
        items.append(_teacher(s["text"].strip(), style))
        if "model" in s:
            st["phase"] = "answer"
        elif s.get("shows"):
            st["phase"] = "run"
        else:
            st["phase"] = "continue"

    def _cur(self, st):
        s = self.steps[st["playing"]["step"]]
        return s["return"] if st["playing"]["variant"] == "return" else s

    # ---- judging an answer

    def _rows(self, sql):
        if sql not in self._cache:
            r = run_sql(self.conn, sql)
            self._cache[sql] = None if r.error else r.full
        return self._cache[sql]

    @staticmethod
    def _flags(cur):
        return {"ordered": cur.get("ordered", False), "any_column_order": cur.get("any_column_order", False)}

    def _correct(self, cur, res):
        if res.error:
            return False
        for sql in [cur["model"], *cur.get("accepts", [])]:
            want = self._rows(sql)
            if want is not None and same_rows(res.full, want, **self._flags(cur)):
                return True
        return False

    def _on_correct(self, st, cur, step, variant, text, items):
        if st["why"]:
            items.append(_teacher(st["why"][0].upper() + st["why"][1:]))
        if normalise(text) == normalise(cur["model"]) and text.strip() != cur["model"].strip():
            items.append({"type": "compare", "yours": text.strip(), "usual": cur["model"]})
            items.append(_teacher(self._pick(st, "slip")))
            outcome = "slip"
        else:
            self._narrate(st, cur, items)
            outcome = "correct"
        st["phase"] = "continue"
        return outcome

    def _narrate(self, st, cur, items):
        pool = list(cur.get("narration", []))
        if not pool:
            return
        line = self.rng.choice([x for x in pool if x != st["last_narration"]] or pool)
        st["last_narration"] = line
        if line.strip():
            items.append(_teacher(line))

    def _pick(self, st, key):
        options = self.ui[key]
        line = self.rng.choice([x for x in options if x != st["last_ui"].get(key)] or options)
        st["last_ui"][key] = line
        return line
