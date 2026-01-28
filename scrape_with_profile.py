#!/usr/bin/env python3
"""
Парсер ЦИАН с использованием профиля Chrome
Использует вашу существующую авторизацию через Google
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import random

# Путь к профилю Chrome (где сохранена ваша авторизация)
PROFILE_PATH = str(Path.home() / "Library/Application Support/Google/Chrome/Default")

CIAN_SEARCH_URL = "https://www.cian.ru/sale/flat/?bez_apartamentov=1&price_min=1000000&price_max=50000000"
MAX_PAGES = 3  # Начнем с 3 страниц

print("="*80)
print("🚀 ЦИАН ПАРСЕР - С ПРОФИЛЕМ CHROME")
print("="*80)

# Настройки обычного Chrome с вашим профилем
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={PROFILE_PATH}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

print("\n⏳ Запуск Chrome с вашим профилем...")
try:
    driver = webdriver.Chrome(options=options)
    print("✅ Chrome запущен")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    exit(1)

def extract_offers():
    """Извлечь предложения со страницы"""
    offers = []
    
    try:
        # Ищем карточки предложений
        cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'OfferCard')]")
        print(f"  📊 Найдено карточек: {len(cards)}")
        
        for card in cards:
            try:
                offer = {}
                
                # Адрес
                try:
                    address = card.find_element(By.XPATH, ".//h2 | .//a[contains(@href, '/sale/')]")
                    offer['Адрес'] = address.text
                except:
                    offer['Адрес'] = ""
                
                # Цена
                try:
                    price = card.find_element(By.XPATH, ".//span[contains(., '₽')] | .//div[contains(@class, 'price')]")
                    offer['Цена'] = price.text
                except:
                    offer['Цена'] = ""
                
                # Площадь
                try:
                    area = card.find_element(By.XPATH, ".//span[contains(text(), 'м²')]")
                    offer['Площадь'] = area.text
                except:
                    offer['Площадь'] = ""
                
                # Метро
                try:
                    metro = card.find_element(By.XPATH, ".//span[contains(@class, 'metro')] | .//div[contains(text(), 'м')]")
                    offer['Метро'] = metro.text
                except:
                    offer['Метро'] = ""
                
                # Ссылка
                try:
                    link = card.find_element(By.XPATH, ".//a[contains(@href, '/sale/')]")
                    offer['Ссылка'] = link.get_attribute("href")
                    offer['ID'] = link.get_attribute("href").split('/')[-2]
                except:
                    offer['ID'] = ""
                
                if offer['ID'] and offer['Адрес']:
                    offers.append(offer)
                
            except:
                continue
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
    
    return offers

try:
    print("\n📝 ШАГ 1: Переход на страницу поиска")
    driver.get(CIAN_SEARCH_URL)
    time.sleep(8)
    
    print(f"✅ Загружена: {driver.current_url}\n")
    
    # Проверяем что не 404
    if "404" in driver.page_source or "не найдена" in driver.page_source:
        print("❌ Получена ошибка 404! ЦИАН блокирует парсер")
        print("💡 Совет: Откройте https://www.cian.ru в обычном браузере")
        print("   и убедитесь что вы авторизованы через Google")
        driver.save_screenshot("error_404.png")
    else:
        print("✅ Страница загружена без ошибок")
        
        # Проверяем авторизацию
        if "Войти" in driver.page_source:
            print("⚠️  Похоже вы не авторизованы")
        else:
            print("✅ Похоже вы авторизованы!")
        
        # Начинаем парсить
        print("\n📝 ШАГ 2: Парсинг предложений")
        
        all_offers = []
        
        for page in range(1, MAX_PAGES + 1):
            print(f"\n🔄 Страница {page}/{MAX_PAGES}")
            
            if page > 1:
                page_url = f"{CIAN_SEARCH_URL}&p={page}"
                driver.get(page_url)
                time.sleep(5 + random.uniform(0, 3))
            
            try:
                offers = extract_offers()
                all_offers.extend(offers)
                print(f"  💾 Всего: {len(all_offers)}")
            except Exception as e:
                print(f"  ❌ Ошибка: {e}")
            
            if page < MAX_PAGES:
                time.sleep(random.uniform(5, 8))
        
        # Сохраняем результаты
        if all_offers:
            print("\n\n" + "="*80)
            print("📝 ШАГ 3: Сохранение результатов")
            print("="*80)
            
            df = pd.DataFrame(all_offers)
            df_unique = df.drop_duplicates(subset=['ID'], keep='first')
            
            print(f"\n📊 Статистика:")
            print(f"  Собрано: {len(all_offers)}")
            print(f"  Уникальных: {len(df_unique)}")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            desktop = str(Path.home() / "Desktop")
            
            # Excel
            excel_file = f"{desktop}/cian_offers_{timestamp}.xlsx"
            df_unique.to_excel(excel_file, index=False)
            print(f"\n✅ Excel: {excel_file}")
            
            # CSV
            csv_file = f"{desktop}/cian_offers_{timestamp}.csv"
            df_unique.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"✅ CSV: {csv_file}")
            
            print("\n" + "="*80)
            print("🎉 УСПЕШНО!")
            print("="*80)
        else:
            print("\n❌ Не собрано предложений")

except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n⏳ Закрытие браузера...")
    try:
        driver.quit()
        print("✅ Готово!")
    except:
        pass
