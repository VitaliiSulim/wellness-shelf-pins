#!/usr/bin/env python3
"""
Рисует вертикальные пины 1000x1500 для товаров из data/products.csv.

Макет: плашка доски сверху, заголовок-крючок, фото товара на белой
карточке, звёзды и число отзывов, строка бренда, подпись профиля.

Палитра индиго + крем + золото, как у аватара. Зелёного нет намеренно:
это фирменный цвет iHerb, а условия партнёрки запрещают оформление,
похожее на рекламодателя. По той же причине на картинке нет ни логотипа,
ни слова iHerb.

Фото товаров кешируются в content/cache/, готовые пины — content/pins/<id>.jpg.

Запуск:
    python scripts/render_pins.py            # все товары со статусом draft*
    python scripts/render_pins.py 88819 4193 # только указанные id
"""

import csv
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS = ROOT / "data" / "products.csv"
CACHE = ROOT / "content" / "cache"
OUT = ROOT / "content" / "pins"

CDN = "https://cloudinary.images-iherb.com/image/upload/f_jpg,q_auto:good/"

W, H = 1000, 1500
CREAM = (250, 245, 236)
INDIGO = (44, 52, 94)
GOLD = (226, 170, 72)
GREY = (104, 108, 126)
WHITE = (255, 255, 255)

FONTS = Path("C:/Windows/Fonts")
HEADLINE = ImageFont.truetype(str(FONTS / "georgiab.ttf"), 66)
LABEL = ImageFont.truetype(str(FONTS / "seguisb.ttf"), 26)
RATING = ImageFont.truetype(str(FONTS / "seguisb.ttf"), 34)
BRAND = ImageFont.truetype(str(FONTS / "segoeui.ttf"), 30)
FOOTER = ImageFont.truetype(str(FONTS / "seguisb.ttf"), 24)


def fetch_image(path):
    """Фото товара с CDN, с локальным кешем — повторный рендер не качает заново."""
    CACHE.mkdir(parents=True, exist_ok=True)
    local = CACHE / path.replace("/", "_")
    if not local.exists():
        req = urllib.request.Request(CDN + path, headers={"User-Agent": "Mozilla/5.0"})
        # CDN изредка подвисает — три попытки, прежде чем сдаться
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    local.write_bytes(r.read())
                break
            except (TimeoutError, OSError):
                if attempt == 2:
                    raise
    return Image.open(local).convert("RGB")


def wrap(draw, text, font, width):
    """Переносит текст по словам под заданную ширину."""
    lines, line = [], ""
    for word in text.split():
        probe = f"{line} {word}".strip()
        if draw.textlength(probe, font=font) <= width:
            line = probe
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def star(draw, cx, cy, r, fill):
    """Пятиконечная звезда полигоном — не зависит от наличия глифа в шрифте."""
    import math
    pts = []
    for i in range(10):
        rad = r if i % 2 == 0 else r * 0.45
        a = math.radians(-90 + i * 36)
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    draw.polygon(pts, fill=fill)


def spaced(text, n=3):
    """Разрядка для капса: PIL не умеет letter-spacing."""
    return (" " * (n // 3 or 1)).join(text)


def render(p):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # Плашка доски
    label = p["board"].upper()
    lw = d.textlength(label, font=LABEL) + 56
    d.rounded_rectangle([(W - lw) / 2, 64, (W + lw) / 2, 112], radius=24, fill=INDIGO)
    d.text((W / 2, 88), label, font=LABEL, fill=CREAM, anchor="mm")

    # Заголовок
    y = 150
    for line in wrap(d, p["headline"], HEADLINE, 860):
        d.text((W / 2, y), line, font=HEADLINE, fill=INDIGO, anchor="ma")
        y += 80

    # Карточка с фото — растягиваем под оставшееся место
    card_top = y + 30
    card_bottom = 1235
    side = card_bottom - card_top
    x0 = (W - side) / 2
    d.rounded_rectangle([x0, card_top, x0 + side, card_bottom], radius=36, fill=WHITE)
    photo = fetch_image(p["image"])
    inner = int(side * 0.9)
    photo.thumbnail((inner, inner), Image.LANCZOS)
    img.paste(photo, (int(W / 2 - photo.width / 2), int(card_top + side / 2 - photo.height / 2)))

    # Звёзды и отзывы
    reviews = int(p["reviews"])
    shown = f"{reviews // 1000},000+" if reviews >= 1000 else str(reviews)
    text = f"{p['rating']}  ·  {shown} reviews"
    tw = d.textlength(text, font=RATING)
    stars_w = 5 * 38
    x = (W - stars_w - 16 - tw) / 2
    for i in range(5):
        star(d, x + 19 + i * 38, 1290, 16, GOLD)
    d.text((x + stars_w + 16, 1290), text, font=RATING, fill=INDIGO, anchor="lm")

    # Бренд
    d.text((W / 2, 1345), p["brand_line"], font=BRAND, fill=GREY, anchor="mm")

    # Подпись профиля
    d.line([(W / 2 - 60, 1405), (W / 2 + 60, 1405)], fill=GOLD, width=3)
    d.text((W / 2, 1440), spaced("THE WELLNESS SHELF"), font=FOOTER, fill=INDIGO, anchor="mm")

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{p['id']}.jpg"
    img.save(out, "JPEG", quality=90, optimize=True)
    return out


def main():
    ids = set(sys.argv[1:])
    with open(PRODUCTS, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for p in rows:
        if (ids and p["id"] in ids) or (not ids and p["status"].startswith("draft")):
            print(render(p))


if __name__ == "__main__":
    main()
