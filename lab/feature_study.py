"""Pokreni: python -m lab.feature_study [putanja do features.jsonl] -> ispisuje izvestaj o osobinama (kad ima dovoljno redova)."""
import sys

from . import features


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "_state/lab/features.jsonl"
    rows = features.load(path)
    if len(rows) < 30:
        print("premalo redova (%d); potrebno bar 30 sati" % len(rows))
        return 1
    print(features.report(features.study(rows), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
