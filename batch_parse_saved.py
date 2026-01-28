from pathlib import Path
import csv
from bs4 import BeautifulSoup
import re

TARGET_COLUMNS = [
    "ID",
    "Количество комнат",
    "Тип",
    "Метро",
    "Адрес",
    "Площадь, м2",
    "Дом",
    "Парковка",
    "Цена",
    "Телефоны",
    "Описание",
    "Ремонт",
    "Площадь комнат, м2",
    "Балкон",
    "Окна",
    "Санузел",
    "Есть телефон",
    "Название ЖК",
    "Серия дома",
    "Высота потолков, м",
    "Лифт",
    "Мусоропровод",
    "Ссылка на объявление",
]


def parse_card(card):
    data = {col: "" for col in TARGET_COLUMNS}

    link_tag = card.find("a", href=re.compile(r"/sale/flat/"))
    if link_tag and link_tag.get("href"):
        url = link_tag["href"]
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = "https://www.cian.ru" + url
        data["Ссылка на объявление"] = url
        m = re.search(r"/(\d+)/", url)
        if m:
            data["ID"] = m.group(1)

    title_block = card.find(attrs={"data-name": "TitleComponent"})
    title_text = title_block.get_text(" ", strip=True) if title_block else ""

    params_line = None
    for line in title_text.split(","):
        if "м²" in line and "этаж" in line:
            params_line = line.strip()
            break

    m_room_type = re.search(
        r"^(\d+)[- ]?комн?\.?\s*(квартира|апартаменты|апарт-отель)?",
        title_text,
        re.IGNORECASE,
    )
    if m_room_type:
        data["Количество комнат"] = m_room_type.group(1)
        if m_room_type.group(2):
            data["Тип"] = m_room_type.group(2).capitalize()

    if params_line:
        m_total_m = re.search(r"([\d.,]+)\s*м²", params_line)
        if m_total_m:
            data["Площадь, м2"] = m_total_m.group(1).replace(",", ".")

    geo = card.find(attrs={"data-name": "GeoLabel"})
    if geo:
        geo_text = geo.get_text(" ", strip=True)
        data["Адрес"] = geo_text
        m_metro = re.search(r"м\.\s*([^,]+)", geo_text)
        if m_metro:
            data["Метро"] = m_metro.group(1).strip()

    full_text = card.get_text(" ", strip=True)

    m_h = re.search(r"Потолки\s+([\d.,]+)", full_text)
    if m_h:
        data["Высота потолков, м"] = m_h.group(1).replace(",", ".")

    price_block = None
    for div in card.find_all(["div", "span"]):
        txt = div.get_text(" ", strip=True)
        if "₽" in txt and "м²" in txt:
            price_block = txt
            break
    if price_block:
        m_total = re.search(r"([\d\s]+)\s*₽(?!/)", price_block)
        if m_total:
            data["Цена"] = m_total.group(1).replace(" ", "")

    desc_block = card.find(attrs={"data-name": "Description"})
    if desc_block:
        data["Описание"] = desc_block.get_text(" ", strip=True)

    if "ремонт" in full_text.lower():
        m_r = re.search(r"([^.]{0,60}ремонт[^.]{0,60})", full_text, re.IGNORECASE)
        if m_r:
            data["Ремонт"] = m_r.group(1).strip()

    if "Парковка" in full_text:
        m_p = re.search(r"(Парковка[^.]{0,40})", full_text)
        if m_p:
            data["Парковка"] = m_p.group(1).strip()

    phone = None
    for span in card.find_all("span"):
        txt = span.get_text(" ", strip=True)
        if re.search(r"\+7\s?\d", txt):
            phone = txt
            break
    if phone:
        data["Телефоны"] = phone
        data["Есть телефон"] = "Да"

    return data


def parse_single_html(html_path: Path):
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("article", attrs={"data-name": "CardComponent"})
    print(f"{html_path.name}: найдено карточек {len(cards)}")
    return [parse_card(card) for card in cards]


def main():
    base_dir = Path("saved_html")
    out_csv = Path("offers_all.csv")

    all_rows = []

    for html_file in sorted(base_dir.glob("*.html")):
        rows = parse_single_html(html_file)
        all_rows.extend(rows)

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TARGET_COLUMNS)
        writer.writeheader()
        for r in all_rows:
            writer.writerow(r)

    print(f"Всего объектов: {len(all_rows)}")
    print(f"Сохранено в {out_csv}")


if __name__ == "__main__":
    main()

