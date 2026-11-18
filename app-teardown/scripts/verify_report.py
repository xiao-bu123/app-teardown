# -*- coding: utf-8 -*-
"""Check a teardown report for the mistakes that actually happen.

Usage:
  python verify_report.py <report.md> [--shots DIR]

Checks:
  - every ![](...) image exists
  - image count == page index rows == "#### Lx-yy" headings
  - page codes are unique
  - required sections exist
  - index table has no empty cells
  - report length is in the expected range

Exit code 1 when any ERROR is found.
"""
import os, re, sys, argparse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

REQUIRED = [
    "调研对象与基本盘",
    "结论",
    "页面层级树",
    "页面索引",
    "逐页拆解",
    "功能清单",
    "技术观察",
    ("调研方法与安全边界", "调研方法与边界"),
]


def _require(text, item):
    alts = item if isinstance(item, tuple) else (item,)
    return any(a in text for a in alts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--shots", default="")
    a = ap.parse_args()

    md_path = os.path.abspath(a.md)
    base = os.path.dirname(md_path)
    shots = a.shots or os.path.join(base, "shots")
    text = open(md_path, encoding="utf-8").read()

    errors, warns, infos = [], [], []

    # 1. images
    imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    missing = []
    for p in imgs:
        rel = p.replace("@", "")
        if rel.startswith(("./", "../")):
            full = os.path.normpath(os.path.join(base, rel))
        elif os.path.isabs(rel):
            full = rel
        else:
            full = os.path.normpath(os.path.join(base, rel))
        if not os.path.exists(full):
            missing.append(p)
    if missing:
        errors.append("missing images: %d -> %s" % (len(missing), ", ".join(missing[:5])))
    infos.append("images referenced: %d, files in shots/: %d" %
                 (len(imgs), len([f for f in os.listdir(shots)]) if os.path.isdir(shots) else 0))

    # 2. index rows
    rows = re.findall(r"^\|\s*(L\d-\d+)\s*\|", text, re.M)
    heads = re.findall(r"^####\s*(L\d-\d+)\s*·", text, re.M)
    infos.append("index rows: %d, page headings: %d" % (len(rows), len(heads)))
    if len(rows) != len(heads):
        errors.append("index rows (%d) != page cards (%d)" % (len(rows), len(heads)))
    if len(imgs) not in (len(rows), len(heads)):
        warns.append("images (%d) != pages (%d) — some pages may share or miss screenshots"
                     % (len(imgs), len(rows)))

    # 2b. v2 blocks
    roles = len(re.findall(r"^\*\*定位\*\*：", text, re.M))
    blocks = len(re.findall(r"^\*\*区块\*\*：", text, re.M))
    block_rows = len(re.findall(r"^\| (?:top|left|center|right|bottom|overlay) \|[^\n]*\| (?:seen|absent|inferred|unknown) \|$", text, re.M))
    absent = len(re.findall(r"\| absent \|", text))
    unknown = len(re.findall(r"\| unknown \|", text))
    if roles or blocks:
        infos.append("v2 blocks: roles=%d, block tables=%d, block rows=%d (absent=%d, unknown=%d)"
                     % (roles, blocks, block_rows, absent, unknown))
        if roles != len(heads):
            warns.append("only %d/%d pages have **定位** (v2 role missing)" % (roles, len(heads)))
        if blocks != roles:
            errors.append("block tables (%d) != roles (%d)" % (blocks, roles))
        if block_rows < len(heads) * 2:
            warns.append("block rows look thin: %d rows for %d pages" % (block_rows, len(heads)))

    # 3. duplicates
    dup = {c for c in rows if rows.count(c) > 1}
    if dup:
        errors.append("duplicate page codes: %s" % ", ".join(sorted(dup)))

    # 4. required sections
    for s in REQUIRED:
        if not _require(text, s):
            errors.append("missing section: %s" % (s if isinstance(s, str) else " / ".join(s)))

    # 5. empty index cells
    empty = 0
    for line in text.splitlines():
        if re.match(r"^\|\s*L\d-\d+\s*\|", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if any(c == "" for c in cells):
                empty += 1
    if empty:
        warns.append("%d index rows have empty cells" % empty)

    # 6. length
    n = len(text)
    infos.append("characters: %d" % n)
    if n < 8000:
        warns.append("report is short (<8k chars); page coverage may be thin")
    if n > 60000:
        warns.append("report is long (>60k chars); consider splitting appendix")

    for i in infos:
        print("INFO  " + i)
    for w in warns:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    print("\n%s — %d error(s), %d warning(s)" % ("FAIL" if errors else "PASS", len(errors), len(warns)))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
