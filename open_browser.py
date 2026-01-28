#!/usr/bin/env python3
"""
ЦИАН ПАРСЕР - ТОЛЬКО ОТКРЫТИЕ БРАУЗЕРА
Открывает браузер и ждет пока вы вручную введете данные
"""

import undetected_chromedriver as uc
import time
import os
from pathlib import Path

print("="*80)
print("🚀 ОТКРЫТИЕ БРАУЗЕРА ЦИАН")
print("="*80)

# Создаем папку для скачивания
download_dir = str(Path.home() / "Downloads" / "cian_temp")
os.makedirs(download_dir, exist_ok=True)

# Настройки Chrome
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "profile.default_content_settings.popups": 0,
}
options.add_experimental_option("prefs", prefs)

print("\n⏳ Запуск браузера...")
try:
    driver = uc.Chrome(options=options, version_main=None)
    print("✅ Браузер запущен успешно!")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    exit(1)

print("\n" + "="*80)
print("📝 ИНСТРУКЦИЯ:")
print("="*80)
print("\n1. Перейдите на https://www.cian.ru/sale/flat/")
print("2. Введите ваши фильтры:")
print("   - Цена: 1,000,000 - 50,000,000 руб")
print("   - Без апартаментов: Да")
print("   - Балкон: Да")
print("\n3. Авторизуйтесь через Google (или email)")
print("\n4. Когда будут готовы результаты поиска,")
print("   введите 'ok' в этом терминале и нажмите Enter\n")
print("="*80)

# Открываем страницу поиска
print("\n🔗 Открываю страницу поиска ЦИАН...")
driver.get("https://www.cian.ru/sale/flat/?bez_apartamentov=1&price_min=1000000&price_max=50000000")

print("✅ Страница открыта в браузере")
print("\n⏳ Ожидание ввода...\n")

# Ждем ввода пользователя
try:
    user_input = input("Когда будете готовы, введите 'ok': ").strip().lower()
    
    if user_input == "ok":
        print("\n✅ Продолжаем работу...")
        print(f"📍 Текущий URL: {driver.current_url}\n")
        
        # Проверяем авторизованы ли
        page_source = driver.page_source
        
        if "Войти" in page_source or "Войдите" in page_source:
            print("⚠️  Похоже вы не авторизованы")
        else:
            print("✅ Похоже вы авторизованы!")
        
        print("\n" + "="*80)
        print("💡 Теперь браузер готов к парсингу")
        print("="*80)
        print("\nНажмите Ctrl+C для закрытия браузера или оставьте открытым")
        print("Браузер будет ждать вашей команды...\n")
        
        # Ждем Ctrl+C
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⏸️  Получена команда на закрытие")
    else:
        print("❌ Неправильный ввод")

except KeyboardInterrupt:
    print("\n\n⏸️  Получена команда на закрытие")

print("\n⏳ Закрытие браузера...")
try:
    driver.quit()
    print("✅ Браузер закрыт")
except:
    print("⚠️  Ошибка при закрытии браузера")

print("\n🎉 Готово!")
