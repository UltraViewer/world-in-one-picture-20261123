#!/usr/bin/env python3
"""Build the make.fun news-image entry for Monday 23 November 2026.

Front page: masthead, COP31 collapse headline, hero photo of the empty
Antalya plenary hall, two photo stories (Benghazi sea drones, Seoul chip
slide), and a dark strip with markets + briefs. Lettering is drawn with
PIL; the three photos are AI-generated editorial panels in ./panels.
Deterministic: same inputs, same bytes. Output: entry.png 1024x1024.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parent
PANELS = ROOT / "panels"

W, H = 1024, 1024
PAPER = (250, 246, 234)
INK = (18, 18, 18)
RED = (176, 30, 42)
GREY = (96, 92, 82)
PALE = (232, 228, 216)

FONT_FILES = {
    "serif_b": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "serif_i": "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_b": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

HERO = "media-generation-hero-cop31-0-ce614cd3-833a-4339-ad59-8a6251173d84.webp"
LEFT = "media-generation-panel-benghazi-0-79de66dd-e18d-42fa-a208-08bc5401c398.webp"
RIGHT = "media-generation-panel-chips-0-f49d054c-3f2c-4ea8-be29-ea3696154a09.webp"

HEADLINE = ["COP31 COLLAPSES", "NO DEAL AFTER LONGEST TALKS EVER"]
CAPTION = (
    "ANTALYA \u2014 The UN climate summit ends with no agreement on fossil "
    "fuels or finance, the first full collapse of a COP deal since "
    "Copenhagen 2009."
)
STORIES = [
    {
        "photo": LEFT,
        "kicker": "BENGHAZI, LIBYA",
        "head": "Sea drones sink Russian warship",
        "body": (
            "Zelenskyy says Ukrainian naval drones struck two Russian "
            "ships in the Libyan port; the corvette Merkury was sunk."
        ),
    },
    {
        "photo": RIGHT,
        "kicker": "SEOUL",
        "head": "Chip stocks plunge on AI doubts",
        "body": (
            "Kospi falls 5.8% at one point, closing down 3.3%; Samsung "
            "\u22123.1%, SK Hynix \u22122.5%."
        ),
    },
]
STRIP_TOP = "MARKETS  \u25bc  Kospi \u22123.3% as chip stocks slide  \u2022  Nasdaq futures rebound 3%"
STRIP_BOTTOM = (
    "POLAND \u2014 debris was Kh-101 missiles  \u2022  INDONESIA \u2014 factory-fire "
    "search continues  \u2022  BALTIC \u2014 Sparta II towed"
)


def font(kind, size):
    return ImageFont.truetype(FONT_FILES[kind], size)


def wrap(draw, text, kind, size, width):
    f = font(kind, size)
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=f) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def crop_to(img, tw, th):
    w, h = img.size
    if w / h > tw / th:
        cut = int(h * tw / th)
        left = (w - cut) // 2
        img = img.crop((left, 0, left + cut, h))
    else:
        cut = int(w * th / tw)
        top = (h - cut) // 2
        img = img.crop((0, top, w, top + cut))
    return img.resize((tw, th), Image.LANCZOS)


def photo(page, draw, name, x, y, w, h):
    img = Image.open(PANELS / name).convert("RGB")
    img = ImageEnhance.Color(crop_to(img, w, h)).enhance(1.05)
    img = ImageEnhance.Contrast(img).enhance(1.03)
    page.paste(img, (x, y))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)


def story(draw, x, y, width, s):
    draw.text((x, y), s["kicker"], font=font("sans_b", 19), fill=RED)
    draw.text((x, y + 24), s["head"], font=font("sans_b", 17), fill=INK)
    cursor = y + 48
    for line in wrap(draw, s["body"], "sans", 16, width):
        draw.text((x, cursor), line, font=font("sans", 16), fill=INK)
        cursor += 20


def headline_font(draw, text, max_size, width):
    """Largest serif-bold size at or below max_size that fits width."""
    size = max_size
    while size > 20 and draw.textlength(text, font=font("serif_b", size)) > width:
        size -= 1
    return font("serif_b", size)


def build():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)
    m, edge = 28, W - 28

    d.text((W // 2, 26), "THE WORLD IN ONE PICTURE",
           font=font("serif_b", 56), fill=INK, anchor="ma")
    d.line([(m, 96), (edge, 96)], fill=INK, width=3)
    d.line([(m, 102), (edge, 102)], fill=INK, width=1)

    d.text((m, 112), "MONDAY, 23 NOVEMBER 2026",
           font=font("sans_b", 21), fill=RED)
    d.text((edge, 113), "ONE DAY  \u2022  ONE IMAGE",
           font=font("sans", 19), fill=GREY, anchor="ra")
    d.line([(m, 146), (edge, 146)], fill=INK, width=1)

    d.text((W // 2, 158), HEADLINE[0],
           font=headline_font(d, HEADLINE[0], 44, edge - m),
           fill=INK, anchor="ma")
    d.text((W // 2, 206), HEADLINE[1],
           font=headline_font(d, HEADLINE[1], 44, edge - m),
           fill=INK, anchor="ma")

    photo(page, d, HERO, m, 268, edge - m, 292)

    cursor = 572
    for line in wrap(d, CAPTION, "serif_i", 19, edge - m):
        d.text((m, cursor), line, font=font("serif_i", 19), fill=INK)
        cursor += 26

    gap = 12
    col = (edge - m - gap) // 2
    top, ph = 640, 150
    photo(page, d, STORIES[0]["photo"], m, top, col, ph)
    photo(page, d, STORIES[1]["photo"], m + col + gap, top, col, ph)
    story(d, m, top + ph + 10, col, STORIES[0])
    story(d, m + col + gap, top + ph + 10, col, STORIES[1])

    sy, sh = 904, 76
    d.rectangle([m, sy, edge, sy + sh], fill=INK)
    d.text((m + 14, sy + 10), STRIP_TOP, font=font("sans_b", 17), fill=(250, 246, 234))
    d.text((m + 14, sy + 40), STRIP_BOTTOM, font=font("sans", 15), fill=PALE)

    d.text((W // 2, 992),
           "Illustrated summary of the world\u2019s news  \u2022  23 November 2026",
           font=font("sans", 13), fill=GREY, anchor="ma")

    out = ROOT / "entry.png"
    page.save(out, "PNG", optimize=True, compress_level=9)
    size = out.stat().st_size
    print(f"entry.png: {page.size} {size} bytes ({size / 1048576:.2f} MiB) limit 1048576")
    return 0 if size <= 1048576 else 1


if __name__ == "__main__":
    sys.exit(build())
