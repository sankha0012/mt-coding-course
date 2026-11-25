"""Read one MongoDB sentence of the course, as the learner types it, without running any JavaScript.

A sentence is `db.<collection>.<method>(<arguments>)`, with `.sort(...)`, `.limit(...)` and `.skip(...)` chained
after a find. Arguments are written as in the mongosh shell: bare, quoted or dotted names, numbers, words, lists,
documents, `ISODate("...")` and `/pattern/flags`. Nothing else is read, so a sentence can only ever call the
methods that checker.mongo allows."""
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from bson.regex import Regex

READ_METHODS = {"find", "findOne", "countDocuments", "estimatedDocumentCount", "distinct", "aggregate"}
WRITE_METHODS = {"insertOne", "insertMany", "updateOne", "updateMany", "deleteOne", "deleteMany"}
MODIFIERS = {"sort", "limit", "skip"}

# stages and words that write, run code of their own, or read beyond the course collections
_FORBIDDEN = {"$out", "$merge", "$where", "$function", "$accumulator", "$collStats", "$indexStats",
              "$planCacheStats", "$currentOp", "$listSessions", "$listLocalSessions", "$listSearchIndexes",
              "$search", "$searchMeta", "$changeStream"}


class ParseError(ValueError):
    """The text is not one sentence this course reads."""


@dataclass
class Call:
    collection: str
    method: str
    args: list
    mods: list = field(default_factory=list)


_NAME = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
_NUMBER = re.compile(r"-?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?")
_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "0": "\0", "\\": "\\", '"': '"', "'": "'", "/": "/"}


class _Reader:
    def __init__(self, text):
        self.s, self.i = text, 0

    def ws(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def peek(self):
        self.ws()
        return self.s[self.i] if self.i < len(self.s) else ""

    def fail(self, what):
        near = self.s[self.i:self.i + 12].strip()
        raise ParseError(f"I could not read that as one MongoDB sentence: {what}" + (f" near `{near}`." if near else "."))

    def take(self, ch):
        if self.peek() != ch:
            self.fail(f"expected `{ch}`")
        self.i += 1

    def name(self):
        self.ws()
        m = _NAME.match(self.s, self.i)
        if not m:
            self.fail("expected a name")
        self.i = m.end()
        return m.group()

    # ---- values

    def value(self):
        c = self.peek()
        if c == "":
            self.fail("the sentence stops too soon")
        if c == "{":
            return self.document()
        if c == "[":
            return self.array()
        if c in ("\"", "'"):
            return self.string()
        if c == "/":
            return self.regex()
        if c == "-" or c.isdigit() or c == ".":
            return self.number()
        if c.isalpha() or c == "_":
            word = self.name()
            if word in ("true", "false"):
                return word == "true"
            if word == "null":
                return None
            if word == "ISODate":
                return self.isodate()
            self.fail(f"I do not know `{word}`")
        self.fail("expected a value")

    def number(self):
        m = _NUMBER.match(self.s, self.i)
        if not m:
            self.fail("expected a number")
        self.i = m.end()
        text = m.group()
        return float(text) if any(ch in text for ch in ".eE") else int(text)

    def string(self):
        quote = self.s[self.i]
        self.i += 1
        out = []
        while self.i < len(self.s):
            c = self.s[self.i]
            if c == quote:
                self.i += 1
                return "".join(out)
            if c == "\\":
                self.i += 1
                e = self.s[self.i:self.i + 1]
                if e == "u" and re.fullmatch(r"[0-9a-fA-F]{4}", self.s[self.i + 1:self.i + 5]):
                    out.append(chr(int(self.s[self.i + 1:self.i + 5], 16)))
                    self.i += 5
                    continue
                if e not in _ESCAPES:
                    self.fail("an unknown escape in a word")
                out.append(_ESCAPES[e])
            else:
                out.append(c)
            self.i += 1
        self.fail("a word was not closed")

    def regex(self):
        self.i += 1
        out = []
        while self.i < len(self.s) and self.s[self.i] != "/":
            if self.s[self.i] == "\\" and self.i + 1 < len(self.s):
                out.append(self.s[self.i:self.i + 2])
                self.i += 2
            else:
                out.append(self.s[self.i])
                self.i += 1
        if self.i >= len(self.s):
            self.fail("a pattern was not closed")
        self.i += 1
        m = re.compile(r"[gimsuy]*").match(self.s, self.i)
        self.i = m.end()
        return Regex("".join(out), m.group().replace("g", ""))

    def isodate(self):
        self.take("(")
        if self.peek() not in ("\"", "'"):
            self.fail("ISODate needs a date in quotes")
        text = self.string()
        self.take(")")
        try:
            when = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            raise ParseError(f"I could not read `{text}` as a date. Write it like ISODate(\"2026-08-01T10:30:00Z\").")
        return when if when.tzinfo else when.replace(tzinfo=timezone.utc)

    def array(self):
        self.take("[")
        out = []
        while self.peek() != "]":
            out.append(self.value())
            if self.peek() == ",":
                self.i += 1
            elif self.peek() != "]":
                self.fail("expected `,` or `]`")
        self.i += 1
        return out

    def document(self):
        self.take("{")
        out = {}
        while self.peek() != "}":
            key = self.string() if self.peek() in ("\"", "'") else self.name()
            self.take(":")
            out[key] = self.value()
            if self.peek() == ",":
                self.i += 1
            elif self.peek() != "}":
                self.fail("expected `,` or `}`")
        self.i += 1
        return out

    def arguments(self):
        self.take("(")
        out = []
        while self.peek() != ")":
            out.append(self.value())
            if self.peek() == ",":
                self.i += 1
            elif self.peek() != ")":
                self.fail("expected `,` or `)`")
        self.i += 1
        return out


def parse(text):
    """One sentence as a Call. Raises ParseError, with a calm message, for anything else."""
    r = _Reader(text)
    if r.peek() == "":
        raise ParseError("There is nothing to run yet.")
    if r.name() != "db":
        r.i = 0
        r.fail("a sentence starts with `db`")
    r.take(".")
    collection = r.name()
    r.take(".")
    method = r.name()
    args = r.arguments()
    mods = []
    while r.peek() == ".":
        r.i += 1
        word = r.name()
        if word not in MODIFIERS:
            r.fail(f"I do not know `.{word}(...)` after a sentence")
        mods.append((word, r.arguments()))
    if r.peek() == ";":
        r.i += 1
    if r.peek() != "":
        r.fail("there is more after the end of the sentence")
    return Call(collection, method, args, mods)


def is_write(call):
    return call.method in WRITE_METHODS


def forbidden_in(value):
    """The first stage or word in a document or list that this course does not run, or None."""
    if isinstance(value, dict):
        for k, v in value.items():
            if k in _FORBIDDEN:
                return k
            if k == "$lookup" and isinstance(v, dict) and isinstance(v.get("from"), dict):
                return "$lookup from another database"
            found = forbidden_in(v)
            if found:
                return found
    elif isinstance(value, list):
        for v in value:
            found = forbidden_in(v)
            if found:
                return found
    return None


def _plain(value):
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(value, Regex):
        return f"/{value.pattern}/{value.flags if isinstance(value.flags, str) else ''}"
    raise TypeError(type(value))


def normalise(text):
    """The sentence in one form that is equal when only spacing, quote style, quoted names or a final
    semicolon differ. Text that cannot be read normalises to its own words."""
    try:
        c = parse(text)
    except ParseError:
        return " ".join(text.split())
    mods = "".join(f".{n}({json.dumps(a, default=_plain, ensure_ascii=False)[1:-1]})" for n, a in c.mods)
    return f"db.{c.collection}.{c.method}({json.dumps(c.args, default=_plain, ensure_ascii=False)[1:-1]}){mods}"
