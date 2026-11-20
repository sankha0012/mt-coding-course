import argparse
import sys

import uvicorn

from checker.checks import check_all
from checker.data import load_db
from checker.lesson import load_strand

from .app import make_app


def preflight(content_dir, data_dir):
    """The checker's failures for the lesson folder. A lesson with any is never played."""
    thoughts, lessons = load_strand(content_dir)
    fails, *_ = check_all(load_db(data_dir), thoughts, lessons)
    return fails


def main(argv=None):
    p = argparse.ArgumentParser(prog="player", description="Play the lesson in a local web page.")
    p.add_argument("--port", type=int, default=8770)
    p.add_argument("--content", default="content/sql")
    p.add_argument("--data", default="data")
    p.add_argument("--progress", default="progress")
    args = p.parse_args(argv)
    fails = preflight(args.content, args.data)
    if fails:
        print("\n".join(fails))
        print("\nThe lesson fails the checker, so it will not be played.")
        return 1
    print(f"http://127.0.0.1:{args.port}")
    uvicorn.run(make_app(args.content, args.data, args.progress), host="127.0.0.1", port=args.port,
                log_level="warning")
    return 0


if __name__ == "__main__":
    sys.exit(main())
