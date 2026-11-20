import argparse
from collections import Counter

from checker.lesson import load_strand

from .store import Store


def build_report(events, steps):
    """One line per step and variant, with the most misses first."""
    groups = {}
    for e in events:
        groups.setdefault((e["step"], e["variant"]), []).append(e)
    if not groups:
        return ["No answers yet."]
    rows = []
    for (step, variant), evs in groups.items():
        misses = [e for e in evs if e["outcome"] == "miss"]
        first_try = sum(1 for e in evs if e["outcome"] in ("correct", "slip") and e["misses"] == 0)
        common = Counter(e["typed"] for e in misses).most_common(1)
        needs = ", ".join(steps[step - 1].get("requires", [])) if step <= len(steps) else ""
        name = f"step {step}" + (" (return)" if variant == "return" else "")
        line = f"{name}: {len(evs)} answers, {first_try} right the first time, {len(misses)} misses"
        if common:
            line += f"; most common miss: {common[0][0]}"
        if needs:
            line += f"; needs: {needs}"
        rows.append((-len(misses), step, variant, line))
    return [r[3] for r in sorted(rows)]


def main(argv=None):
    p = argparse.ArgumentParser(prog="player.report", description="Where the learner missed.")
    p.add_argument("--content", default="content/sql")
    p.add_argument("--progress", default="progress")
    args = p.parse_args(argv)
    _, lessons = load_strand(args.content)
    print("\n".join(build_report(Store(args.progress).events(), lessons[0][1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
