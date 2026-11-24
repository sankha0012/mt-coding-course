"""Write a lesson as YAML from Python data, so that lessons are formatted the same way every time.

A lesson is a list of step dicts. Use `emit(path, lesson, title, strand, steps, thoughts)`.
The YAML file is the source of truth. This is only a convenience for writing it."""
import json

ORDER = ["kind", "lang", "data", "new", "imports", "requires", "supplies", "friction", "ordered", "any_column_order",
         "text", "thinking_order", "check", "model", "rows", "result", "output", "accepts", "shows", "broken",
         "after_run", "narration", "narration_ahead", "wrong", "walk", "return", "note"]
RETURN_ORDER = ["text", "check", "model", "ordered", "any_column_order", "rows", "result", "output", "accepts",
                "narration", "note"]
WRONG_ORDER = ["sql", "code", "ask", "why", "tell"]
BLOCK_KEYS = {"text", "after_run", "model", "check", "thinking_order"}


def w(code, ask=None, why=None, tell=None, lang="sql"):
    """A known wrong answer. `code` is SQL if lang is 'sql' and Python if 'python'."""
    d = {("code" if lang == "python" else "sql"): code}
    for k, v in (("ask", ask), ("why", why), ("tell", tell)):
        if v:
            d[k] = v
    return d


def _scalar(value):
    return json.dumps(value, ensure_ascii=False)


def _block(key, text, ind, dash=False):
    """A multi-line string as a YAML block, so that code and paragraphs stay readable."""
    pad = " " * ind
    keep = text.endswith("\n")
    head = f"{pad}{'- ' if dash else ''}{key + ': ' if key else ''}|{'' if keep else '-'}"
    body = [(pad + "  " + line) if line else "" for line in (text[:-1] if keep else text).split("\n")]
    return [head] + body


def _can_block(text):
    return isinstance(text, str) and "\n" in text and not text.startswith((" ", "\t", "\n")) \
        and all(line == line.rstrip() or not line for line in text.split("\n"))


def _emit_value(key, value, ind, order):
    pad = " " * ind
    if isinstance(value, str) and (key in BLOCK_KEYS or "\n" in value) and _can_block(value):
        return _block(key, value, ind)
    if key in ("narration", "walk", "accepts", "shows") and isinstance(value, list):
        out = [f"{pad}{key}:"]
        for item in value:
            if _can_block(item):
                out += _block("", item, ind + 2, dash=True)
            else:
                out.append(f"{pad}  - {_scalar(item)}")
        return out
    if key == "wrong":
        out = [f"{pad}wrong:"]
        for item in value:
            first = True
            for k in WRONG_ORDER:
                if k not in item:
                    continue
                if _can_block(item[k]):
                    lines = _block(k, item[k], ind + 4)
                    lines[0] = f"{pad}  {'- ' if first else '  '}" + lines[0].lstrip()
                    out += lines
                else:
                    out.append(f"{pad}  {'- ' if first else '  '}{k}: {_scalar(item[k])}")
                first = False
        return out
    if key == "return":
        return [f"{pad}return:"] + _emit_dict(value, ind + 2, RETURN_ORDER)
    return [f"{pad}{key}: {_scalar(value)}"]


def _emit_dict(d, ind, order):
    unknown = set(d) - set(order)
    if unknown:
        raise ValueError(f"unknown step fields: {sorted(unknown)}")
    out = []
    for k in order:
        if k in d:
            out += _emit_value(k, d[k], ind, order)
    return out


def emit(path, lesson, title, strand, steps, thoughts=None, stage=1):
    lines = [f"lesson: {lesson}", f"title: {_scalar(title)}", f"strand: {strand}", f"stage: {stage}"]
    if thoughts:
        lines.append("thoughts:")
        for t, spec in thoughts.items():
            if isinstance(spec, dict):
                lines.append(f"  {t}: {{text: {_scalar(spec['text'])}, grade: {spec['grade']}}}")
            else:
                lines.append(f"  {t}: {_scalar(spec)}")
    lines.append("steps:")
    for i, s in enumerate(steps, 1):
        lines.append(f"  # {i}")
        body = _emit_dict(s, 4, ORDER)
        body[0] = "  - " + body[0].lstrip()
        lines += body
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip("\n") + "\n")
