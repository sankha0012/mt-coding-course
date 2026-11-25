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


def lesson_titles(content_dir):
    """Name, title and strand of every lesson, in the order they are played."""
    d = Path(content_dir)
    if is_course(d):
        manifest = yaml.safe_load((d / "course.yaml").read_text(encoding="utf-8"))["course"]
        paths = [d / f"{entry}.yaml" for entry in manifest]
    else:
        paths = sorted(d.glob("lesson-*.yaml"))
    out = []
    for path in paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        out.append({"lesson": data["lesson"], "title": data.get("title", data["lesson"]),
                    "strand": data.get("strand", path.parent.name)})
    return out
