#!/usr/bin/env python3
"""Build the final front-page entry.png for news-image-20261121.

Fresh code written for this entry (2026-11-21). Layout follows the winner
template: ONE dominant story (Russian missiles in Poland) occupying >=50%
of the image area; five small supporting panels below; headline <=8 words;
text rendered programmatically with Pillow (never AI-generated text).

Input : media-generation-news-2026-11-21-collage-*.png (1920x1280)
Output: entry.png (1280 wide, target < 1 MiB)
"""
import json
from PIL import Image, ImageDraw, ImageFont

SRC = "/home/hatch/workspace/makefun/entries/news-image-20261121/media-generation-news-2026-11-21-collage-0-2d33aef4-47bb-4d55-a346-a38d9b6fea2a.png"
OUT = "/home/hatch/workspace/makefun/entries/news-image-20261121/entry.png"

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

OUT_W = 960  # keep entry.png < 1 MiB (20261117 entry was 798 KB at 1024w)
SCALE = OUT_W / 1920.0

collage = Image.open(SRC).convert("RGB")
W, H = collage.size  # 1920 x 1280

# --- detect the white gutter row separating the dominant panel from the strip
px = collage.load()
gutter_y = None
for y in range(int(H * 0.55), int(H * 0.70)):
    sample = [px[x, y] for x in range(0, W, 7)]
    near_white = sum(1 for r, g, b in sample if r > 245 and g > 245 and b > 245)
    if near_white >= 0.95 * len(sample):
        gutter_y = y
        break
assert gutter_y is not None, "gutter row not found"
dom_h = gutter_y  # dominant panel height in source px (includes top margin)

# --- layout (scaled to OUT_W)
mast_h = int(96 * SCALE)
cap_h = int(120 * SCALE)
foot_h = int(36 * SCALE)
total_h = mast_h + int(H * SCALE) + cap_h + foot_h

page = Image.new("RGB", (OUT_W, total_h), "white")
small = collage.resize((OUT_W, int(H * SCALE)), Image.LANCZOS)
page.paste(small, (0, mast_h))
d = ImageDraw.Draw(page)

def font(path, size):
    return ImageFont.truetype(path, int(size * SCALE))

# --- masthead
f_title = font(SERIF_B, 66)
f_date = font(SANS, 28)
d.text((28 * SCALE, 14 * SCALE), "THE WORLD IN ONE IMAGE", fill="black", font=f_title)
date_txt = "SATURDAY, 21 NOVEMBER 2026"
dw = d.textlength(date_txt, font=f_date)
d.text((OUT_W - 28 * SCALE - dw, 30 * SCALE), date_txt, fill="black", font=f_date)
d.line([(28 * SCALE, mast_h - 8 * SCALE), (OUT_W - 28 * SCALE, mast_h - 8 * SCALE)],
       fill="black", width=max(2, int(3 * SCALE)))

# --- headline overlay band at the bottom of the dominant panel
band_h = int(150 * SCALE)
band_y0 = mast_h + int(dom_h * SCALE) - band_h
overlay = Image.new("RGBA", (OUT_W, band_h), (0, 0, 0, 178))
page.paste(overlay, (0, band_y0), overlay)
d = ImageDraw.Draw(page)
f_head = font(SERIF_B, 58)
f_deck = font(SANS, 25)
d.text((28 * SCALE, band_y0 + 14 * SCALE), "RUSSIAN MISSILES STRIKE NATO SOIL",
       fill="white", font=f_head)
d.text((28 * SCALE, band_y0 + 88 * SCALE),
       "Two missiles and a drone crash in Poland during Russia's biggest attack on Ukraine —",
       fill="white", font=f_deck)
d.text((28 * SCALE, band_y0 + 118 * SCALE),
       "PM Tusk calls it an intentional provocation; NATO calls it a grave violation.",
       fill="white", font=f_deck)

def wrap_text(text, fnt, max_w, draw):
    """Greedy word-wrap so no line exceeds max_w px."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# --- captions under the five bottom panels
captions = [
    ("WALL STREET ROUT", "S&P 500 −3.7%, Nasdaq −5.3% — correction"),
    ("THE HAGUE", "ICJ: Myanmar committed genocide on Rohingya"),
    ("BRUSSELS", "UK and EU sign food, carbon, youth deals"),
    ("CYCLONE AKVAN", "Storm makes landfall on India's east coast"),
    ("SHENZHEN", "Trump–Xi–Putin summit ends with few results"),
]
f_cap_b = font(SANS_B, 21)
f_cap = font(SANS, 20)
strip_y0 = mast_h + int(H * SCALE)
panel_w = OUT_W / 5.0
line_h = int(26 * SCALE)
for i, (bold, rest) in enumerate(captions):
    cx = panel_w * i + panel_w / 2
    bw = d.textlength(bold, font=f_cap_b)
    d.text((cx - bw / 2, strip_y0 + 6 * SCALE), bold, fill="black", font=f_cap_b)
    lines = wrap_text(rest, f_cap, panel_w - 16 * SCALE, d)
    for j, line in enumerate(lines):
        rw = d.textlength(line, font=f_cap)
        d.text((cx - rw / 2, strip_y0 + (34 + j * 26) * SCALE), line,
               fill="#333333", font=f_cap)

# --- footer
f_foot = font(SANS, 20)
d.text((28 * SCALE, total_h - 28 * SCALE),
       "Sources: AP · Reuters · BBC · NPR · Morningstar — 21 November 2026",
       fill="#555555", font=f_foot)

page.save(OUT, optimize=True)
import os
print("saved", OUT, page.size, os.path.getsize(OUT), "bytes")
print("dominant panel fraction of final image: %.1f%%" %
      (100.0 * dom_h * SCALE / total_h))
print("headline words:", len("RUSSIAN MISSILES STRIKE NATO SOIL".split()))
