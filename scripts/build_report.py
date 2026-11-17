# -*- coding: utf-8 -*-
"""Build the single-file HTML report + Markdown backups from a JSON data file.

Usage (inside the research folder, next to shots/):
    python scripts/build_report.py templates/report.json
    python scripts/build_report.py my_report.json --root .

The JSON shape is documented in templates/report.json (same keys report_lib expects).
"""
import argparse
import json
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import report_lib  # noqa: E402


def load(path):
    with open(path, encoding="utf-8-sig") as f:
        obj = json.load(f)
    # Only the top level becomes attributes; nested dicts stay dicts because
    # report_lib indexes them (s["id"], p["code"], ...).
    return SimpleNamespace(**obj)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json", nargs="?", default=os.path.join("templates", "report.json"))
    ap.add_argument("--root", default=".", help="folder that contains shots/")
    args = ap.parse_args()
    report_lib.build(load(args.json), args.root)


if __name__ == "__main__":
    main()
