#!/usr/bin/env python3
"""
Собирает CSV для Pinterest Bulk create Pins из data/products.csv.

Картинка пина берётся из публичного репозитория на GitHub (raw-ссылка), поэтому
перед импортом content/pins/ должен быть запушен.

Ссылка: партнёрская из колонки `link`, если она заполнена, иначе прямая на
товар — так было с первыми пинами до одобрения программы в Admitad.

Расписание: 4 слота в день по Лондону. Pinterest читает время в CSV как UTC,
поэтому слоты переводим из Europe/London в UTC — с учётом перехода BST/GMT.
На Windows для zoneinfo нужен пакет tzdata (requirements.txt).

Запуск:
    python scripts/build_csv.py --out first8.csv --now          # опубликовать сразу
    python scripts/build_csv.py --out week-2026-10-05.csv --start 2026-10-05
"""

import argparse
import csv
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS = ROOT / "data" / "products.csv"
OUT_DIR = ROOT / "content" / "csv"

RAW = "https://raw.githubusercontent.com/VitaliiSulim/wellness-shelf-pins/main/content/pins/"
SLOTS = [time(7, 30), time(12, 0), time(18, 0), time(20, 30)]
LONDON = ZoneInfo("Europe/London")

# Порядок колонок официальный, из шаблона Pinterest.
COLUMNS = ["Title", "Media URL", "Pinterest board", "Thumbnail",
           "Description", "Link", "Publish date", "Keywords"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", help="первый день расписания, YYYY-MM-DD")
    ap.add_argument("--now", action="store_true", help="без даты — Pinterest публикует сразу")
    ap.add_argument("--status", default="draft", help="какие товары брать")
    args = ap.parse_args()

    with open(PRODUCTS, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["status"] == args.status]

    start = date.fromisoformat(args.start) if args.start else None
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / args.out
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for i, p in enumerate(rows):
            when = ""
            if not args.now and start:
                day = start + timedelta(days=i // len(SLOTS))
                local = datetime.combine(day, SLOTS[i % len(SLOTS)], tzinfo=LONDON)
                when = local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            w.writerow({
                "Title": p["title"],
                "Media URL": RAW + f"{p['id']}.jpg",
                "Pinterest board": p["board"],
                "Thumbnail": "",
                "Description": p["description"],
                "Link": p.get("link") or f"https://www.iherb.com/pr/{p['slug']}/{p['id']}",
                "Publish date": when,
                "Keywords": p["keywords"],
            })
    print(f"{out}  ({len(rows)} pins)")


if __name__ == "__main__":
    main()
