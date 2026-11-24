import argparse
from collections import Counter

from checker.lesson import load_content

from .store import Store


def build_report(events, lessons):
    """One line per lesson, step and variant, with the most misses first."""
    steps_of = dict(lessons)
    groups = {}
    for e in events:
        groups.setdefault((e["lesson"], e["step"], e["variant"]), []).append(e)
    if not groups:
        return ["No answers yet."]
    rows = []
    for (lesson, step, variant), evs in groups.items():
        steps = steps_of.get(lesson, [])
        misses = [e for e in evs if e["outcome"] == "miss"]
        first_try = sum(1 for e in evs if e["outcome"] in ("correct", "slip") and e["misses"] == 0)
        common = Counter(e["typed"] for e in misses).most_common(1)
        needs = ", ".join(steps[step - 1].get("requires", [])) if step <= len(steps) else ""
        name = f"{lesson} step {step}" + (" (return)" if variant == "return" else "")
        line = f"{name}: {len(evs)} answers, {first_try} right the first time, {len(misses)} misses"
        if common:
            line += f"; most common miss: {common[0][0]}"
        if needs:
            line += f"; needs: {needs}"
        rows.append((-len(misses), lesson, step, variant, line))
    return [r[4] for r in sorted(rows)]


def build_question_report(questions):
    """The steps the learner asked about most, each with the latest question. For the writer, never a score."""
    groups = {}
    for q in questions:
        groups.setdefault((q["lesson"], q["step"]), []).append(q)
    ranked = sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    return [f"{lesson} step {step}: {len(qs)} question{'s' if len(qs) != 1 else ''}; latest: {qs[-1]['question']}"
            for (lesson, step), qs in ranked]


def main(argv=None):
    p = argparse.ArgumentParser(prog="player.report", description="Where the learner missed.")
    p.add_argument("--content", default="content")
    p.add_argument("--progress", default="progress")
    args = p.parse_args(argv)
    store = Store(args.progress)
    _, lessons = load_content(args.content)
    print("\n".join(build_report(store.events(), lessons)))
    asked = build_question_report(store.questions())
    if asked:
        print("\nQuestions asked:\n" + "\n".join(asked))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
