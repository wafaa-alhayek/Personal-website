#!/usr/bin/env python3
"""
dither.py — turn a folder of masters into (a) 1-bit duotone thumbnails in the
site palette and (b) optimised full-colour web exports.

    python3 dither.py ./masters ./out --ink "#1A1AFF" --paper "#F2F1EC"

Produces, per source image:
    out/duo/<name>.png    two-colour dithered plate   (usually 40-150 KB)
    out/web/<name>.webp   full-colour export, 2000px  (usually 200-600 KB)

Dither modes:  bayer (ordered, crisp, retro)  |  fs (Floyd-Steinberg, organic)
"""

import argparse, pathlib, sys
from PIL import Image, ImageOps, ImageEnhance

BAYER8 = [
    [ 0, 32,  8, 40,  2, 34, 10, 42],
    [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44,  4, 36, 14, 46,  6, 38],
    [60, 28, 52, 20, 62, 30, 54, 22],
    [ 3, 35, 11, 43,  1, 33,  9, 41],
    [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47,  7, 39, 13, 45,  5, 37],
    [63, 31, 55, 23, 61, 29, 53, 21],
]


def hex_rgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def bayer_threshold(img):
    """Ordered dither to 1-bit. Keeps a crisp, printed screen texture."""
    w, h = img.size
    src = img.load()
    out = Image.new("1", (w, h))
    dst = out.load()
    for y in range(h):
        row = BAYER8[y & 7]
        for x in range(w):
            dst[x, y] = 255 if src[x, y] > (row[x & 7] * 4 + 2) else 0
    return out


def duotone(path, dest, ink, paper, width, mode, contrast, invert):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im).convert("L")

    ratio = width / im.width
    im = im.resize((width, max(1, round(im.height * ratio))), Image.LANCZOS)

    if contrast != 1.0:
        im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageOps.autocontrast(im, cutoff=1)
    if invert:
        im = ImageOps.invert(im)

    bw = bayer_threshold(im) if mode == "bayer" else im.convert("1")  # "1" = Floyd-Steinberg

    plate = Image.new("RGB", bw.size, ink)
    plate.paste(Image.new("RGB", bw.size, paper), mask=bw)
    plate = plate.convert("P", palette=Image.ADAPTIVE, colors=2)
    plate.save(dest, "PNG", optimize=True)
    return dest.stat().st_size


def web_export(path, dest, width, quality):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dest, "WEBP", quality=quality, method=6)
    return dest.stat().st_size


def main():
    p = argparse.ArgumentParser()
    p.add_argument("src")
    p.add_argument("out")
    p.add_argument("--ink", default="#1A1AFF", help="colour the darks become")
    p.add_argument("--paper", default="#F2F1EC", help="colour the lights become")
    p.add_argument("--duo-width", type=int, default=900)
    p.add_argument("--web-width", type=int, default=2000)
    p.add_argument("--mode", choices=["bayer", "fs"], default="bayer")
    p.add_argument("--contrast", type=float, default=1.25)
    p.add_argument("--invert", action="store_true")
    p.add_argument("--quality", type=int, default=82)
    a = p.parse_args()

    src = pathlib.Path(a.src)
    duo_dir = pathlib.Path(a.out) / "duo"
    web_dir = pathlib.Path(a.out) / "web"
    duo_dir.mkdir(parents=True, exist_ok=True)
    web_dir.mkdir(parents=True, exist_ok=True)

    ink, paper = hex_rgb(a.ink), hex_rgb(a.paper)
    files = sorted(f for f in src.iterdir()
                   if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"})
    if not files:
        sys.exit(f"no images found in {src}")

    before = after = 0
    print(f"{'file':<22}{'master':>10}{'duotone':>10}{'web':>10}")
    print("-" * 52)
    for f in files:
        m = f.stat().st_size
        d = duotone(f, duo_dir / f"{f.stem}.png", ink, paper,
                    a.duo_width, a.mode, a.contrast, a.invert)
        w = web_export(f, web_dir / f"{f.stem}.webp", a.web_width, a.quality)
        before += m
        after += d + w
        print(f"{f.name:<22}{m/1e6:>9.1f}M{d/1e3:>9.0f}K{w/1e3:>9.0f}K")

    print("-" * 52)
    print(f"{'total':<22}{before/1e6:>9.1f}M{after/1e6:>19.1f}M")
    print(f"reduction: {100 * (1 - after / before):.1f}%")


if __name__ == "__main__":
    main()
