#!/usr/bin/env python3
"""
Открывает Chrome с вашим профилем для доступа к ЦИАН
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from pathlib import Path

print("="*80)
print("🚀 ОТКРЫТИЕ CHROME С ВАШИМ ПРОФИЛЕМ")
print("="*80)

# Путь к профилю Chrome на macOS
profile_path = str(Path.home() / "Library/Application Support/Google/Chrome")

print(f"\n📂 Профиль Chrome: {profile_path}")

# Настройки Chrome
options = Options()
options.add_argument(f"user-data-dir={profile_path}")
options.add_argument("--profile-directory=Default")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-blink-features=AutomationControlled")

print("\n⏳ Запуск Chrome с вашим профилем...")

try:
    driver = webdriver.Chrome(options=options)
    print("✅ Chrome запущен с вашим профилем!")
    
    print("\n📝 Переход на ЦИАН...")
    driver.get("https://www.cian.ru")
    time.sleep(5)
    
    print(f"✅ Открыт: {driver.current_url}")
    
    print("\n" + "="*80)
    print("✅ ГОТОВО!")
    print("="*80)
    print("\n📋 Инструкции:")
    print("  1. Браузер открыт с вашей авторизацией через Google")
    print("  2. Вы уже авторизованы на ЦИАН")
    print("  3. Перейдите на нужную страницу поиска")
    print("  4. Когда будете готовы - введите 'ok' в терминале")
    print("\n⏳ Ожидание вашей команды...\n")
    
    user_input = input("Введите 'ok' когда будете готовы продолжить: ").strip()
    
    if user_input.lower() == 'ok':
        print("\n✅ Продолжаем...")
        print(f"📍 Текущий URL: {driver.current_url}")
        
        # Здесь будет парсинг когда дадите команду
        print("\n💡 Браузер готов к парсингу")
        print("   Оставьте окно открытым для дальнейшей работы")
        
        input("\nНажмите Enter для закрытия браузера...")
    
    driver.quit()
    print("\n✅ Браузер закрыт")

except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    print("\n💡 Совет: Закройте все окна Chrome и попробуйте снова")
    import traceback
    traceback.print_exc()

print("\n🎉 Готово!")
