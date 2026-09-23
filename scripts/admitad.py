#!/usr/bin/env python3
"""
Партнёрские ссылки iHerb через API Admitad.

Ключи — ADMITAD_CLIENT_ID и ADMITAD_CLIENT_SECRET из окружения. Они лежат
в секретах GitHub Actions, поэтому запускается скрипт workflow'ом admitad.yml,
а не локально. Токен и ключи в лог не пишем: лог Actions публичного
репозитория виден всем.

Команды:
    check  — площадки аккаунта и подключённые к Pinterest-площадке программы
    links  — диплинки для товаров из data/products.csv с пустой колонкой link

Площадка ищется по слову Pinterest в названии, программа — по iHerb в названии
среди подключённых к ней (connection_status=active).
"""

import base64
import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS = ROOT / "data" / "products.csv"
API = "https://api.admitad.com"

# Названия скоупов у Admitad менялись — пробуем по очереди, пока не выдадут токен.
SCOPES = [
    "websites advcampaigns_for_website deeplink_generator",
    "websites advcampaigns banners",
]


def token():
    cid = os.environ["ADMITAD_CLIENT_ID"]
    secret = os.environ["ADMITAD_CLIENT_SECRET"]
    basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    last = None
    for scope in SCOPES:
        body = urllib.parse.urlencode(
            {"grant_type": "client_credentials", "client_id": cid, "scope": scope}
        ).encode()
        req = urllib.request.Request(
            f"{API}/token/", data=body,
            headers={"Authorization": f"Basic {basic}",
                     "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
            print(f"token: ok, scope = {data.get('scope')}")
            return data["access_token"]
        except urllib.error.HTTPError as e:
            last = f"{e.code} {e.read()[:200]!r}"
            print(f"token: scope '{scope}' rejected: {last}")
    sys.exit(f"не удалось получить токен: {last}")


def get(tok, path, **params):
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def pinterest_space(tok):
    spaces = get(tok, "/websites/v2/", limit=100)["results"]
    for s in spaces:
        print(f"ad space {s['id']}: {s['name']} [{s.get('status')}]")
    match = [s for s in spaces if "pinterest" in s["name"].lower()]
    if not match:
        sys.exit("площадка с Pinterest в названии не найдена")
    return match[0]


def iherb_campaign(tok, w_id):
    progs = get(tok, f"/advcampaigns/website/{w_id}/", connection_status="active", limit=500)["results"]
    for p in progs:
        print(f"program {p['id']}: {p['name']}")
    match = [p for p in progs if "iherb" in p["name"].lower() and "offline" not in p["name"].lower()]
    return match[0] if match else None


def cmd_check():
    tok = token()
    space = pinterest_space(tok)
    camp = iherb_campaign(tok, space["id"])
    print("iHerb подключён:", f"{camp['id']} {camp['name']}" if camp else "нет (заявка ещё не одобрена)")


def cmd_links():
    tok = token()
    space = pinterest_space(tok)
    camp = iherb_campaign(tok, space["id"])
    if not camp:
        sys.exit("iHerb не подключён к Pinterest-площадке — диплинки делать рано")

    with open(PRODUCTS, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    fields = list(rows[0].keys())

    made = 0
    for r in rows:
        if r.get("link"):
            continue
        ulp = f"https://www.iherb.com/pr/{r['slug']}/{r['id']}"
        res = get(tok, f"/deeplink/{space['id']}/advcampaign/{camp['id']}/",
                  ulp=ulp, subid=r["id"], subid1="pinterest")
        r["link"] = res[0]["link"] if isinstance(res, list) else res["results"][0]["link"]
        made += 1
        print(f"{r['id']}: {r['link']}")

    with open(PRODUCTS, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"диплинков создано: {made}")


if __name__ == "__main__":
    {"check": cmd_check, "links": cmd_links}[sys.argv[1] if len(sys.argv) > 1 else "check"]()
