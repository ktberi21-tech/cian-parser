#!/usr/bin/env python3
"""
ЦИАН ПАРСЕР - ОСНОВНОЙ СКРИПТ
Скачивает предложения со всех страниц поиска и сохраняет в Excel
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
import random
import sys

# ========== КОНФИГ ==========
CIAN_SEARCH_URL = "https://www.cian.ru/sale/flat/?bez_apartamentov=1&price_min=1000000&price_max=50000000"
MAX_PAGES = 5  # Начнем с 5 страниц для теста
DOWNLOAD_DIR = str(Path.home() / "Downloads" / "cian_temp")
RESULTS_DIR = str(Path.home() / "Desktop")

print("="*80)
print("🚀 ЦИАН ПАРСЕР - ЗАПУСК")
print("="*80)
print(f"🔗 URL: {CIAN_SEARCH_URL}")
print(f"📄 Макс страниц: {MAX_PAGES}")
print(f"💾 Результаты на Desktop\n")

# Создаем папки
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Настройки Chrome
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

prefs = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "profile.default_content_settings.popups": 0,
}
options.add_experimental_option("prefs", prefs)

print("⏳ Запуск браузера Chrome...")
driver = uc.Chrome(options=options, version_main=None)

def is_driver_alive():
    """Проверка живой ли браузер"""
    try:
        driver.current_url
        return True
    except:
        return False

def extract_offers():
    """Извлечь предложения со страницы"""
    offers = []
    
    try:
        # Ищем карточки предложений
        cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'OfferCard')]")
        print(f"  📊 Найдено карточек: {len(cards)}")
        
        for idx, card in enumerate(cards, 1):
            try:
                offer = {}
                
                # ID предложения
                try:
                    offer_link = card.find_element(By.XPATH, ".//a[@href]")
                    href = offer_link.get_attribute("href")
                    offer['ID'] = href.split('/')[-2] if href else ""
                except:
                    offer['ID'] = ""
                
                # Адрес
                try:
                    address = card.find_element(By.XPATH, ".//h2 | .//div[@class*='address']")
                    offer['Адрес'] = address.text
                except:
                    offer['Адрес'] = ""
                
                # Цена
                try:
                    price = card.find_element(By.XPATH, ".//span[@class*='price'] | .//div[@class*='price']")
                    offer['Цена'] = price.text
                except:
                    offer['Цена'] = ""
                
                # Площадь
                try:
                    area = card.find_element(By.XPATH, ".//span[contains(text(), 'м²')] | .//div[contains(text(), 'м²')]")
                    offer['Площадь'] = area.text
                except:
                    offer['Площадь'] = ""
                
                # Комнаты
                try:
                    rooms = card.find_element(By.XPATH, ".//span[@class*='rooms'] | .//div[contains(text(), '-комнатн')]")
                    offer['Комнаты'] = rooms.text
                except:
                    offer['Комнаты'] = ""
                
                # Метро
                try:
                    metro = card.find_element(By.XPATH, ".//span[@class*='metro'] | .//div[@class*='metro']")
                    offer['Метро'] = metro.text
                except:
                    offer['Метро'] = ""
                
                # Описание
                try:
                    desc = card.find_element(By.XPATH, ".//div[@class*='description'] | .//p")
                    offer['Описание'] = desc.text[:200]
                except:
                    offer['Описание'] = ""
                
                # Ссылка
                try:
                    link = card.find_element(By.XPATH, ".//a[@href]")
                    offer['Ссылка'] = link.get_attribute("href")
                except:
                    offer['Ссылка'] = ""
                
                if offer['ID']:
                    offers.append(offer)
                
            except Exception as e:
                continue
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
    
    return offers

try:
    print("\n📝 ШАГ 1: Переход на страницу поиска")
    driver.get(CIAN_SEARCH_URL)
    time.sleep(8)
    
    if not is_driver_alive():
        raise Exception("Браузер закрыт!")
    
    print(f"✅ Загружена страница\n")
    
    # ========== ЦИКЛ СКАЧИВАНИЯ ==========
    print("📝 ШАГ 2: Цикл скачивания предложений")
    
    all_offers = []
    
    for page in range(1, MAX_PAGES + 1):
        if not is_driver_alive():
            print(f"\n⚠️  Браузер закрыт на странице {page}")
            break
        
        print(f"\n🔄 Страница {page}/{MAX_PAGES}")
        
        # Переход на страницу
        if page > 1:
            page_url = f"{CIAN_SEARCH_URL}&p={page}"
            driver.get(page_url)
            time.sleep(5 + random.uniform(0, 3))
        
        # Извлекаем предложения
        try:
            offers = extract_offers()
            all_offers.extend(offers)
            print(f"  💾 Всего собрано: {len(all_offers)} предложений")
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            continue
        
        # Задержка
        if page < MAX_PAGES:
            delay = random.uniform(5, 8)
            print(f"  ⏳ Пауза {delay:.1f} сек...")
            time.sleep(delay)
    
    # ========== СОХРАНЕНИЕ ==========
    print("\n\n" + "="*80)
    print("📝 ШАГ 3: Сохранение результатов")
    print("="*80)
    
    if all_offers:
        df = pd.DataFrame(all_offers)
        df_unique = df.drop_duplicates(subset=['ID'], keep='first')
        
        print(f"\n📊 Статистика:")
        print(f"  Всего: {len(all_offers)}")
        print(f"  Уникальных: {len(df_unique)}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Excel
        excel_file = f"{RESULTS_DIR}/cian_offers_{timestamp}.xlsx"
        df_unique.to_excel(excel_file, index=False)
        print(f"\n✅ Excel: {excel_file}")
        
        # CSV
        csv_file = f"{RESULTS_DIR}/cian_offers_{timestamp}.csv"
        df_unique.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"✅ CSV: {csv_file}")
        
        print("\n" + "="*80)
        print("🎉 ГОТОВО!")
        print("="*80)
    else:
        print("\n❌ Не собрано ни одного предложения!")

except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n⏳ Закрытие браузера...")
    try:
        driver.quit()
        print("✅ Браузер закрыт")
    except:
        pass

print("\n🎉 Завершено!")
