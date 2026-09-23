#!/usr/bin/env python3
"""
Рисует аватар профиля The Wellness Shelf в assets/avatar.png.

Аватар виден размером с ноготь, поэтому здесь силуэт без текста: полка
с тремя баночками и искра-акцент.

Цвет — глубокий индиго, а не зелёный: зелёный — фирменный цвет iHerb, а
условия партнёрки запрещают оформление, похожее на рекламодателя. Красный
и оранжевый тоже нет — сливаются с интерфейсом Pinterest.

Запуск: python scripts/make_avatar.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

OUT_PATH = Path(__file__).resolve().parent.parent / "assets" / "avatar.png"

SIZE = 800
BACKGROUND = (44, 52, 94)      # глубокий индиго
CREAM = (250, 243, 228)
ACCENT = (240, 195, 109)       # тёплое золото
SHADOW = (36, 42, 78)


def draw_sparkle(draw, cx, cy, size, color):
    """Четырёхлучевая искра с вогнутыми сторонами — читается даже мелкой."""
    w = size * 0.22
    draw.polygon(
        [(cx, cy - size), (cx + w, cy - w), (cx + size, cy), (cx + w, cy + w),
         (cx, cy + size), (cx - w, cy + w), (cx - size, cy), (cx - w, cy - w)],
        fill=color,
    )


def main():
    # Рисуем в 4x и уменьшаем — гладкие края без ручного сглаживания.
    k = 4
    img = Image.new("RGB", (SIZE * k, SIZE * k), BACKGROUND)
    d = ImageDraw.Draw(img)

    def s(v):
        return int(v * k)

    # Всё держим внутри круга радиусом ~300: Pinterest обрезает аватар в круг.

    # Высокий флакон слева
    d.rounded_rectangle([s(235), s(330), s(345), s(560)], radius=s(22), fill=CREAM)
    d.rounded_rectangle([s(258), s(290), s(322), s(338)], radius=s(10), fill=CREAM)
    d.rectangle([s(235), s(420), s(345), s(470)], fill=SHADOW)  # этикетка

    # Средняя банка
    d.rounded_rectangle([s(365), s(400), s(465), s(560)], radius=s(18), fill=CREAM)
    d.rounded_rectangle([s(360), s(375), s(470), s(410)], radius=s(8), fill=ACCENT)

    # Низкая баночка крема справа
    d.rounded_rectangle([s(485), s(470), s(575), s(560)], radius=s(14), fill=CREAM)
    d.rounded_rectangle([s(480), s(450), s(580), s(478)], radius=s(8), fill=CREAM)

    # Полка
    d.rounded_rectangle([s(200), s(565), s(610), s(595)], radius=s(12), fill=ACCENT)

    # Искры: «находка»
    draw_sparkle(d, s(545), s(335), s(62), ACCENT)
    draw_sparkle(d, s(600), s(410), s(26), ACCENT)

    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT_PATH, "PNG", optimize=True)
    print(f"Аватар: {OUT_PATH}")


if __name__ == "__main__":
    main()
