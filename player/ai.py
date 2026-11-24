"""What the teacher tells the model, and the pieces of the guard. Nothing here ever receives a step's
model answer, wrong answers, walk or return: the caller passes only what the learner has already seen."""
import csv
import re
from pathlib import Path

FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.S)
INLINE = re.compile(r"`([^`\n]+)`")


def thought_lines(thoughts, ids):
    out = []
    for i in ids:
        t = thoughts.get(i)
        text = t.get("text") if isinstance(t, dict) else t
        if text:
            out.append(text)
    return out


def schema_lines(folder):
    lines = []
    for f in sorted(Path(folder).glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as h:
            header = next(csv.reader(h), [])
        lines.append(f"{f.stem}: {', '.join(header)}")
    return lines


def attempt_text(items):
    """The last thing the learner typed, and what it gave."""
    at = next((i for i in range(len(items) - 1, -1, -1) if items[i]["type"] == "learner"), None)
    if at is None:
        return ""
    out = f"Typed:\n{items[at]['sql']}"
    res = items[at + 1] if at + 1 < len(items) and items[at + 1]["type"] == "result" else None
    if res is None:
        return out
    if res.get("error"):
        return out + f"\nGave an error: {res['error']}"
    if res.get("lang") == "python":
        return out + f"\nPrinted:\n{res.get('text') or '(nothing)'}"
    rows = "\n".join(", ".join(str(v) for v in r) for r in res["rows"][:5])
    return out + f"\nGave columns {', '.join(res['columns'])} and rows:\n{rows}"


def build_messages(ui, thoughts, teacher_lines, prompt, attempt, schema, thread, question):
    parts = [ui["ask_persona"].strip(),
             "Thoughts the learner has met, in order:\n" + "\n".join("- " + t for t in thoughts),
             "The lesson so far:\n" + "\n".join(line[:1500] for line in teacher_lines[-12:]),
             "The step now waiting:\n" + prompt[:1500],
             "Tables and columns:\n" + "\n".join(schema)]
    if attempt:
        parts.append("The learner's last attempt at this step:\n" + attempt[:1500])
    earlier = [{"role": "user" if m["role"] == "user" else "assistant", "content": m["text"]}
               for m in thread[-10:]]
    return [{"role": "system", "content": "\n\n".join(parts)}, *earlier,
            {"role": "user", "content": question}]


def code_candidates(reply, limit=10):
    blocks = [b.strip() for b in FENCE.findall(reply)]
    spans = [s.strip() for s in INLINE.findall(FENCE.sub(" ", reply))]
    return [c for c in blocks + spans if c][:limit]
