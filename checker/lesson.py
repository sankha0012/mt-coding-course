from pathlib import Path

import yaml


def load_strand(content_dir):
    """Read thoughts.yaml and every lesson-*.yaml in filename order."""
    d = Path(content_dir)
    thoughts = yaml.safe_load((d / "thoughts.yaml").read_text(encoding="utf-8"))["thoughts"]
    lessons = []
    for path in sorted(d.glob("lesson-*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        lessons.append((data["lesson"], data["steps"]))
    return thoughts, lessons


def is_course(content_dir):
    return (Path(content_dir) / "course.yaml").exists()


def load_course(content_dir):
    """Read course.yaml, which lists lessons as 'strand/lesson-NN' in the order they are played.
    Thoughts come from every strand's thoughts.yaml, and an id may be defined in one strand only."""
    d = Path(content_dir)
    manifest = yaml.safe_load((d / "course.yaml").read_text(encoding="utf-8"))["course"]
    thoughts, owner = {}, {}
    for strand in dict.fromkeys(entry.split("/")[0] for entry in manifest):
        for t, text in yaml.safe_load((d / strand / "thoughts.yaml").read_text(encoding="utf-8"))["thoughts"].items():
            if t in thoughts:
                raise ValueError(f"thought '{t}' is defined in both {owner[t]} and {strand}")
            thoughts[t], owner[t] = text, strand
    lessons = []
    for entry in manifest:
        data = yaml.safe_load((d / f"{entry}.yaml").read_text(encoding="utf-8"))
        lessons.append((data["lesson"], data["steps"]))
    return thoughts, lessons


def load_content(content_dir):
    """A course folder if it has a course.yaml, else a single strand folder."""
    return load_course(content_dir) if is_course(content_dir) else load_strand(content_dir)


def ui_path(content_dir):
    """The teacher's course-wide lines: beside course.yaml, or one folder above a single strand."""
    d = Path(content_dir)
    return d / "ui.yaml" if is_course(d) else d.parent / "ui.yaml"
