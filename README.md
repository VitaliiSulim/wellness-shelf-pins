# The Wellness Shelf — Pinterest × iHerb (Admitad)

Партнёрский Pinterest-профиль [pinterest.com/wellnessshelfeu](https://www.pinterest.com/wellnessshelfeu/)
по программе iHerb.com INT в Admitad. Язык английский, но платят только за заказы из Европы
(UK, DE, FR, IT, ES и др.), Украины, Грузии, Казахстана, Израиля, Турции и ОАЭ; **США, Канады
и России в гео программы нет**. Поэтому тексты пишем по-британски, а расписание ставим по Лондону.

## Правила программы, которые влияют на контент

- Любая платная реклама запрещена, промо-пинов тоже нельзя делать: наказание — месяц блокировки и списание заработка.
- Промежуточные страницы запрещены, поэтому ссылка ведёт из пина сразу на товар.
- Слово «iHerb» нельзя ставить в ник, название или домен. Нельзя их логотип и похожее
  оформление, поэтому в палитре нет зелёного.
- Мобильное приложение iHerb не трекается.
- Медицинских обещаний не пишем («лечит», «укрепляет иммунитет», «от тревоги») — это
  правила Pinterest по теме здоровья. Описываем состав, формат, отзывы и для кого товар.
- Дисклеймер «Affiliate link…» ставим в начало описания.

## Структура

| Путь | Что |
|---|---|
| `data/products.csv` | Каталог: тексты, доска, картинка, ссылка, статус |
| `scripts/render_pins.py` | Рисует пины 1000×1500 в `content/pins/<id>.jpg` |
| `scripts/build_csv.py` | CSV для Pinterest Bulk create Pins |
| `scripts/make_avatar.py` | Аватар профиля |
| `content/pins/` | Картинки пинов — публичные, Pinterest качает их по raw-ссылке |

Статусы в `products.csv`:
- `draft` — готов к публикации;
- `live_direct` — опубликован с прямой ссылкой, до одобрения Admitad; ссылку нужно заменить на партнёрскую;
- `live` — опубликован с партнёрской ссылкой.

## Доски

Vitamins & Supplements · Korean Skincare Finds · Natural Skincare & Body Care ·
Healthy Snacks & Pantry · Protein & Sports Nutrition · Herbal Tea & Healthy Drinks ·
Kids & Baby Wellness · Natural Hair Care

Название доски в CSV должно совпадать с названием в Pinterest.

## Еженедельный цикл

1. Отобрать 28 новых товаров (4 в день × 7) из бестселлеров uk.iherb.com, которых ещё нет в
   `products.csv`, с рейтингом от 4.5 и тысячами отзывов, распределить по доскам.
2. Для каждого получить партнёрский диплинк Admitad (колонка `link`) и написать тексты.
   Добавить строки со статусом `draft`.
3. `python scripts/render_pins.py` → проверить картинки глазами.
4. `git add -A && git commit && git push` — без пуша Pinterest не скачает картинки.
5. `python scripts/build_csv.py --out week-YYYY-MM-DD.csv --start YYYY-MM-DD` (понедельник).
6. Загрузить CSV на `pinterest.com/settings/bulk-create-pins` из профиля The Wellness Shelf.
7. Проставить загруженным `status=live` и `posted=<дата>`.

Слоты: 07:30, 12:00, 18:00, 20:30 (Лондон).
