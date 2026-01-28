#!/usr/bin/env python3
"""
ЦИАН ПАРСЕР через API
Не использует браузер, берет данные напрямую через HTTP
"""

import requests
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import time

print("="*80)
print("🚀 ЦИАН ПАРСЕР - ЧЕРЕЗ API")
print("="*80)

# API ЦИАН
CIAN_API = "https://api.cian.ru/v2/search/flats/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.cian.ru/',
}

# Параметры поиска
params = {
    'deal_type': 'sale',
    'region_id': 1,  # Москва
    'price_min': 1000000,
    'price_max': 50000000,
    'apartment_only': False,
    'page': 1,
}

print("\n📝 Параметры поиска:")
print(f"  Цена: {params['price_min']} - {params['price_max']}")
print(f"  Регион: Москва")

all_offers = []
max_pages = 3  # Начнем с 3 страниц

try:
    for page in range(1, max_pages + 1):
        print(f"\n🔄 Страница {page}/{max_pages}")
        
        params['page'] = page
        
        try:
            print(f"  🌐 Запрос к API...")
            response = requests.get(CIAN_API, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data or 'offers' not in data['data']:
                print(f"  ❌ Неправильный ответ API")
                break
            
            offers = data['data']['offers']
            print(f"  📊 Получено предложений: {len(offers)}")
            
            for offer in offers:
                try:
                    item = {
                        'ID': offer.get('id', ''),
                        'Адрес': offer.get('geo', {}).get('address', ''),
                        'Цена': offer.get('price', ''),
                        'Площадь': f"{offer.get('totalSquare', '')} м²" if offer.get('totalSquare') else '',
                        'Комнаты': offer.get('roomsCount', ''),
                        'Этаж': offer.get('floorNumber', ''),
                        'Ссылка': f"https://www.cian.ru/sale/{offer.get('id', '')}/",
                    }
                    
                    if item['ID']:
                        all_offers.append(item)
                except:
                    continue
            
            print(f"  💾 Всего собрано: {len(all_offers)}")
            
            # Проверяем есть ли еще страницы
            if len(offers) == 0:
                print(f"  ℹ️  Больше предложений нет")
                break
            
            # Задержка между запросами
            if page < max_pages:
                time.sleep(2)
        
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Ошибка запроса: {e}")
            break
    
    # Сохраняем результаты
    if all_offers:
        print("\n\n" + "="*80)
        print("📝 ШАГ 2: Сохранение результатов")
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

print("\n🎉 Готово!")
