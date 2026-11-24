import argparse
import sys

import yaml

from .checks import check_all
from .env import Env
from .lesson import load_content


def main(argv=None):
    p = argparse.ArgumentParser(prog="checker", description="Check a strand of lesson files.")
    p.add_argument("content", help="a course folder with course.yaml, or one strand folder")
    p.add_argument("--data", default="data", help="folder holding the CSV files")
    args = p.parse_args(argv)
    try:
        thoughts, lessons = load_content(args.content)
        env = Env(data_dir=args.data)
    except (OSError, KeyError, yaml.YAMLError) as e:
        print(f"ERROR cannot read the lesson files: {e!r}")
        return 2
    fails, warns, spacing, load = check_all(env, thoughts, lessons)
    for line in fails + warns:
        print(line)
    print("\nSpacing")
    for line in spacing:
        print("  " + line)
    print("\nLoad")
    for line in load:
        print("  " + line)
    print(f"\n{len(fails)} failures, {len(warns)} warnings")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
