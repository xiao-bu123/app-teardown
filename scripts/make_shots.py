# -*- coding: utf-8 -*-
"""PNG screenshots -> report-ready JPEGs + pages.json.

Usage (inside the research folder):
    python scripts/make_shots.py                     # scan *.png, name 01_, 02_, ...
    python scripts/make_shots.py manifest.json       # explicit [{"src","name","caption"}]
    python scripts/make_shots.py --width 900 --quality 84
"""
import argparse
import glob
import json
import os

from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", nargs="?", default=None)
    ap.add_argument("--width", type=int, default=1000)
    ap.add_argument("--quality", type=int, default=84)
    ap.add_argument("--out", default="shots")
    args = ap.parse_args()

    root = os.path.abspath(".")
    if args.manifest and os.path.exists(os.path.join(root, args.manifest)):
        items = json.load(open(os.path.join(root, args.manifest), encoding="utf-8-sig"))
    else:
        pngs = sorted(glob.glob(os.path.join(root, "*.png")))
        items = [{"src": os.path.basename(p),
                  "name": f"{i:02d}_{os.path.splitext(os.path.basename(p))[0]}",
                  "caption": os.path.splitext(os.path.basename(p))[0]}
                 for i, p in enumerate(pngs, 1)]
        print(f"no manifest -> scanning {len(items)} png files")

    os.makedirs(os.path.join(root, args.out), exist_ok=True)
    meta = []
    for it in items:
        src = os.path.join(root, it["src"])
        if not os.path.exists(src):
            print("MISSING", it["src"])
            continue
        im = Image.open(src).convert("RGB")
        w, h = im.size
        nh = int(h * args.width / w)
        im = im.resize((args.width, nh), Image.LANCZOS)
        dst = os.path.join(root, args.out, it["name"] + ".jpg")
        im.save(dst, "JPEG", quality=args.quality, optimize=True, progressive=True)
        meta.append({"name": it["name"], "caption": it.get("caption", it["name"]),
                     "src": it["src"], "w": args.width, "h": nh, "bytes": os.path.getsize(dst)})

    with open(os.path.join(root, "pages.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print(f"images: {len(meta)}  total MB: {sum(m['bytes'] for m in meta)/1048576:.2f}")


if __name__ == "__main__":
    main()
