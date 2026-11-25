from pathlib import Path

import yaml


def _add_thoughts(into, owner, new, where):
    for t, text in new.items():
        if t in into:
            raise ValueError(f"thought '{t}' is defined in both {owner[t]} and {where}")
        into[t], owner[t] = text, where


def _read_thoughts(strand_dir):
    path = Path(strand_dir) / "thoughts.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))["thoughts"] if path.exists() else {}


def load_strand(content_dir):
    """Read thoughts.yaml, if there is one, and every lesson-*.yaml in filename order.
    A lesson may also define the thoughts it introduces, under `thoughts`."""
    d = Path(content_dir)
    thoughts, owner = {}, {}
    _add_thoughts(thoughts, owner, _read_thoughts(d), "thoughts.yaml")
    lessons = []
    for path in sorted(d.glob("lesson-*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        _add_thoughts(thoughts, owner, data.get("thoughts", {}), path.name)
        lessons.append((data["lesson"], data["steps"]))
    if not lessons:
        raise FileNotFoundError(f"no lesson-*.yaml files in {d}")
    return thoughts, lessons


def is_course(content_dir):
    return (Path(content_dir) / "course.yaml").exists()


def load_course(content_dir):
    """Read course.yaml, which lists lessons as 'strand/lesson-NN' in the order they are played.
    Thoughts come from every strand's thoughts.yaml and from the lessons themselves, and an id may be
    defined once only."""
    d = Path(content_dir)
    manifest = yaml.safe_load((d / "course.yaml").read_text(encoding="utf-8"))["course"]
    thoughts, owner = {}, {}
    for strand in dict.fromkeys(entry.split("/")[0] for entry in manifest):
        _add_thoughts(thoughts, owner, _read_thoughts(d / strand), strand)
    lessons = []
    for entry in manifest:
        data = yaml.safe_load((d / f"{entry}.yaml").read_text(encoding="utf-8"))
        _add_thoughts(thoughts, owner, data.get("thoughts", {}), entry)
        lessons.append((data["lesson"], data["steps"]))
    return thoughts, lessons


def load_content(content_dir):
    """A course folder if it has a course.yaml, else a single strand folder."""
    return load_course(content_dir) if is_course(content_dir) else load_strand(content_dir)


def ui_path(content_dir):
    """The teacher's course-wide lines: beside course.yaml, or one folder above a single strand."""
    d = Path(content_dir)
    return d / "ui.yaml" if is_course(d) else d.parent / "ui.yaml"


def _lesson_files(content_dir):
    """Every lesson as read from its file, in the order played."""
    d = Path(content_dir)
    if is_course(d):
        manifest = yaml.safe_load((d / "course.yaml").read_text(encoding="utf-8"))["course"]
        paths = [d / f"{entry}.yaml" for entry in manifest]
    else:
        paths = sorted(d.glob("lesson-*.yaml"))
    out = []
    for path in paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["strand"] = data.get("strand", path.parent.name)
        data["title"] = data.get("title", data["lesson"])
        out.append(data)
    return out


def lesson_titles(content_dir):
    """Name, title, strand and layer of every lesson, in the order they are played. Stage 2 is the interview layer."""
    return [{"lesson": d["lesson"], "title": d["title"], "strand": d["strand"],
             "layer": "interview" if d.get("stage") == 2 else "foundation"} for d in _lesson_files(content_dir)]


def prerequisites(content_dir):
    """Which lessons must be finished before each one opens: the lesson before it in its own strand, and the
    lessons that introduce what it requires. A thought from another strand's foundation needs that whole
    foundation. What an opening cold check borrows is not a prerequisite, since cold checks are unscored and
    the player skips the ones whose thoughts are not met yet. A cold sitting needs everything it asks."""
    lessons = _lesson_files(content_dir)
    layer = {d["lesson"]: "interview" if d.get("stage") == 2 else "foundation" for d in lessons}
    strand = {d["lesson"]: d["strand"] for d in lessons}
    foundation = {}
    for d in lessons:
        if layer[d["lesson"]] == "foundation":
            foundation.setdefault(d["strand"], set()).add(d["lesson"])
    intro = {}
    for d in lessons:
        for step in d["steps"]:
            for t in step.get("new", []):
                intro.setdefault(t, d["lesson"])
    out, last = {}, {}
    for d in lessons:
        name, need = d["lesson"], set()
        if d["strand"] in last:
            need.add(last[d["strand"]])
        for step in d["steps"]:
            if step.get("kind") == "cold-check" and d["strand"] != "cold":
                continue
            for t in step.get("requires", []):
                src = intro.get(t)
                if src is None or strand[src] == d["strand"]:
                    continue  # the chain through the strand already covers its own lessons
                need.add(src)
                if layer[src] == "foundation":
                    need |= foundation[strand[src]]
        out[name] = need - {name}
        last[d["strand"]] = name
    return out
