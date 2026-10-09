#!/usr/bin/env python3
"""
process_images.py — turn uploaded masters into web-sized versions and record
each work's true shape in content/works.json.

Runs automatically from .github/workflows/images.yml whenever a work is added
in the CMS. Safe to run by hand too:

    pip install Pillow
    python3 scripts/process_images.py

For every entry in content/works.json with an `image`:
    img/works/<ref>-1600.webp   viewer / hero version (long edge 1600px)
    img/works/<ref>-640.webp    archive + game version (long edge 640px)
and writes `width` / `height` back into the entry, so the archive puzzle can
lay works out at their real proportions without loading them first.

If `ref` is empty it is taken from the file name (IMG_1175.jpg -> IMG_1175).
Existing outputs newer than their source are skipped.
"""

import json, pathlib, re, sys
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKS = ROOT / "content" / "works.json"
OUT = ROOT / "img" / "works"
SIZES = {"1600": 1600, "640": 640}

Image.MAX_IMAGE_PIXELS = None  # masters can be very large


def source_path(image):
    p = ROOT / image.lstrip("/")
    return p if p.exists() else None


def main():
    data = json.loads(WORKS.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    changed = False

    for w in data.get("works", []):
        image = (w.get("image") or "").strip()
        if not image:
            continue
        src = source_path(image)
        if not src:
            print(f"missing file for {w.get('ref') or image}", file=sys.stderr)
            continue

        if not (w.get("ref") or "").strip():
            m = re.search(r"IMG_\d+", src.stem, re.I)
            w["ref"] = m.group(0).upper() if m else src.stem
            changed = True
        ref = w["ref"]

        im = None
        for tag, edge in SIZES.items():
            dest = OUT / f"{ref}-{tag}.webp"
            if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
                continue
            if im is None:
                im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
            out = im.copy()
            out.thumbnail((edge, edge), Image.LANCZOS)
            out.save(dest, "WEBP", quality=82 if edge > 1000 else 78, method=6)
            print(f"{ref}: {dest.name} {out.size[0]}x{out.size[1]}")

        if im is None:
            with Image.open(src) as probe:
                size = ImageOps.exif_transpose(probe).size
        else:
            size = im.size
        if w.get("width") != size[0] or w.get("height") != size[1]:
            w["width"], w["height"] = size
            changed = True

    if changed:
        WORKS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print("updated content/works.json")


if __name__ == "__main__":
    main()
