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
