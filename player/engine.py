import copy

from .sql import normalise


def _teacher(text, style=None):
    item = {"type": "teacher", "text": text}
    if style:
        item["style"] = style
    return item


class Engine:
    """The sitting as a state machine. It knows neither the web nor the progress file."""

    def __init__(self, steps, runner, ui, rng):
        self.steps, self.runner, self.ui, self.rng = steps, runner, ui, rng
        self._cache = {}

    # ---- public

    def start(self):
        st = {"pos": 0, "phase": "continue", "playing": {"step": 0, "variant": "main"},
              "misses": 0, "rung": 0, "why": None, "queue": [], "returned": [],
              "last_narration": None, "last_ui": {}}
        items = []
        self._enter(st, items)
        return st, self._tag(st, items), []

    def _tag(self, st, items):
        """Teacher text in a Python step says so, so the screen colours its inline code as Python."""
        if st["phase"] != "done" and self._lang(self.steps[st["playing"]["step"]]) == "python":
            for item in items:
                if item["type"] == "teacher":
                    item["lang"] = "python"
        return items

    def pending(self, st):
        phase, step = st["phase"], st["playing"]["step"]
        if phase == "run":
            out = {"mode": "run", "sql": self.steps[step]["shows"][-1]}
        elif phase == "answer":
            out = {"mode": "answer", "step": step + 1, "variant": st["playing"]["variant"]}
        else:
            return {"mode": phase}
        if self._lang(self.steps[step]) == "python":
            out["lang"] = "python"
        return out

    def advance(self, state):
        st, items = copy.deepcopy(state), []
        cur = self.steps[st["playing"]["step"]]
        if st["phase"] == "run":
            code = cur["shows"][-1]
            items += [self._learner(cur, code), self.runner.run(cur, code, check=False).item()]
            if cur.get("after_run"):
                items.append(_teacher(cur["after_run"].strip()))
            st["phase"] = "continue"
        elif st["phase"] == "continue":
            if st["playing"]["variant"] == "main":
                st["pos"] = st["playing"]["step"] + 1
            self._enter(st, items)
        else:
            raise ValueError("nothing to continue")
        return st, self._tag(st, items), []

    def answer(self, state, text):
        st = copy.deepcopy(state)
        if st["phase"] != "answer":
            raise ValueError("not waiting for an answer")
        cur, step, variant = self._cur(st), st["playing"]["step"], st["playing"]["variant"]
        res = self.runner.run(cur, text)
        items = [self._learner(cur, text), res.item()]
        before = st["misses"]

        def event(outcome):
            return {"step": step + 1, "variant": variant, "typed": text, "outcome": outcome, "misses": before}

        if variant == "main" and self.steps[step].get("kind") == "cold-check":
            items = [self._learner(cur, text), res.item("Yours"), self.runner.run(cur, cur["model"]).item("Model")]
            if cur.get("after_run"):
                items.append(_teacher(cur["after_run"].strip()))
            st["phase"] = "continue"
            return st, self._tag(st, items), [event("shown")]
        if self._correct(cur, res):
            outcome = self._on_correct(st, cur, step, variant, text, items)
            return st, self._tag(st, items), [event(outcome)]
        self._on_miss(st, cur, text, res, items)
        return st, self._tag(st, items), [event("miss")]

    def solves(self, st, code):
        """Would this code be taken as the answer to the step now waiting? Read-only. The guard on side
        questions uses it, so a reply that gives the answer away can be replaced."""
        if st["phase"] != "answer":
            return False
        cur = self._cur(st)
        return self._correct(cur, self.runner.run(cur, code))

    # ---- moving through the lesson

    def _enter(self, st, items):
        j = st["pos"]
        if j >= len(self.steps):
            if st["queue"]:
                return self._begin_return(st, items, st["queue"].pop(0)["step"])
            st["phase"] = "done"
            return
        cold = self.steps[j].get("kind") == "cold-check"
        due = [q for q in st["queue"] if q["due"] <= j or cold]
        if due:
            st["queue"].remove(due[0])
            return self._begin_return(st, items, due[0]["step"])
        self._begin_step(st, items, j)

    def _begin_return(self, st, items, i):
        st["returned"].append(i)
        st.update(playing={"step": i, "variant": "return"}, misses=0, rung=0, why=None)
        items.append(_teacher(self.steps[i]["return"]["text"].strip()))
        st["phase"] = "answer"

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
        if st["playing"]["variant"] != "return":
            return s
        # a return is played in its step's language and on its step's data
        return {**{k: s[k] for k in ("lang", "data") if k in s}, **s["return"]}

    @staticmethod
    def _lang(step):
        return step.get("lang", "sql")

    def _learner(self, cur, text):
        item = {"type": "learner", "sql": text}
        if self._lang(cur) == "python":
            item["lang"] = "python"
        return item

    def _norm(self, cur, text):
        """Text in a form that is equal when only trivial things differ."""
        return " ".join(text.split()) if self._lang(cur) == "python" else normalise(text)

    # ---- judging an answer

    def _run(self, cur, code):
        """A model, accepted or wrong answer, run once and kept. None if it does not run."""
        key = (self._lang(cur), cur.get("data", ""), cur.get("check"), code)
        if key not in self._cache:
            r = self.runner.run(cur, code)
            self._cache[key] = None if r.error else r
        return self._cache[key]

    @staticmethod
    def _flags(cur):
        return {"ordered": cur.get("ordered", False), "any_column_order": cur.get("any_column_order", False)}

    def _correct(self, cur, res):
        if res.error:
            return False
        for sql in [cur["model"], *cur.get("accepts", [])]:
            want = self._run(cur, sql)
            if want is not None and res.key(self._flags(cur)) == want.key(self._flags(cur)):
                return True
        return False

    def _on_correct(self, st, cur, step, variant, text, items):
        if st["why"]:
            items.append(_teacher(st["why"][0].upper() + st["why"][1:]))
        if (self._lang(cur) == "sql" and normalise(text) == normalise(cur["model"])
                and text.strip() != cur["model"].strip()):
            items.append({"type": "compare", "yours": text.strip(), "usual": cur["model"]})
            items.append(_teacher(self._pick(st, "slip")))
            outcome = "slip"
        else:
            self._narrate(st, cur, items)
            outcome = "correct"
        queued = {q["step"] for q in st["queue"]}
        if (variant == "main" and st["misses"] >= 1 and "return" in self.steps[step]
                and step not in st["returned"] and step not in queued):
            st["queue"].append({"step": step, "due": step + 3})
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

    # ---- the correction ladder

    def _match_wrong(self, cur, text, res):
        mine = self._norm(cur, text)
        for w in cur.get("wrong", []):
            code = w.get("sql") or w.get("code")
            if self._norm(cur, code) == mine:
                return w
            if res.error is None:
                want = self._run(cur, code)
                if want is not None and res.key(self._flags(cur)) == want.key(self._flags(cur)):
                    return w
        return None

    def _next_rung(self, st, cur, text, res):
        r = st["rung"]
        if r == 0:
            return 1
        if r == 1 and self._match_wrong(cur, text, res):
            return 2
        if r <= 2 and cur.get("walk"):
            return 3
        return 4

    def _on_miss(self, st, cur, text, res, items):
        st["misses"] += 1
        rung = st["rung"] = self._next_rung(st, cur, text, res)
        if rung == 1:
            items.append(_teacher(self._pick(st, "again")))
            if cur.get("thinking_order"):
                items.append(_teacher(cur["thinking_order"]))
        elif rung == 2:
            w = self._match_wrong(cur, text, res)
            items.append(_teacher(w.get("ask") or w["tell"]))
            st["why"] = w.get("why")
        elif rung == 3:
            steps = "\n".join(f"{i}. {w}" for i, w in enumerate(cur["walk"], 1))
            items.append(_teacher(f"{self._pick(st, 'walk_intro')}\n\n{steps}"))
        else:
            items.append(_teacher(f"{self._pick(st, 'show_answer')}\n\n```{self._lang(cur)}\n{cur['model']}\n```"))
