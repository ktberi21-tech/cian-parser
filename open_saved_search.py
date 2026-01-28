#!/usr/bin/env python3
"""
Открывает Chrome с вашим профилем и переходит на сохраненный поиск
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from pathlib import Path

print("="*80)
print("🚀 ОТКРЫТИЕ СОХРАНЕННОГО ПОИСКА ЦИАН")
print("="*80)

# URL вашего сохраненного поиска
SAVED_SEARCH_URL = "https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&object_type%5B0%5D=1&offer_type=flat&only_flat=1&region=1&room1=1&room2=1&room3=1&room4=1&room5=1&saved_search_id=55818992"

# Путь к профилю Chrome на macOS
profile_path = str(Path.home() / "Library/Application Support/Google/Chrome")

print(f"\n📂 Профиль Chrome: {profile_path}")
print(f"🔗 URL: {SAVED_SEARCH_URL[:80]}...")

# Настройки Chrome
options = Options()
options.add_argument(f"user-data-dir={profile_path}")
options.add_argument("--profile-directory=Default")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-blink-features=AutomationControlled")

print("\n⚠️  ВАЖНО: Закройте все окна Chrome перед продолжением!")
input("Нажмите Enter когда закроете Chrome...")

print("\n⏳ Запуск Chrome с вашим профилем...")

try:
    driver = webdriver.Chrome(options=options)
    print("✅ Chrome запущен с вашим профилем!")
    
    print("\n📝 Переход на сохраненный поиск...")
    driver.get(SAVED_SEARCH_URL)
    
    print("⏳ Ожидание загрузки страницы...")
    time.sleep(8)
    
    print(f"\n✅ Загружен URL: {driver.current_url}")
    
    # Проверяем на ошибки
    page_content = driver.page_source.lower()
    
    if "404" in page_content or "не найдена" in page_content:
        print("❌ Ошибка 404 - страница не найдена")
        driver.save_screenshot(str(Path.home() / "Desktop/cian_error.png"))
        print("📸 Скриншот сохранен на Desktop")
    elif "войти" in page_content and "kiruha_777" not in page_content:
        print("⚠️  Возможно требуется авторизация")
        print("💡 Авторизуйтесь вручную в браузере")
    else:
        print("✅ Страница загружена успешно!")
        
        # Проверяем наличие объявлений
        if "найдено" in page_content or "объявлен" in page_content:
            print("✅ Объявления найдены на странице!")
        else:
            print("⚠️  Не удалось определить наличие объявлений")
    
    print("\n" + "="*80)
    print("✅ БРАУЗЕР ОТКРЫТ")
    print("="*80)
    print("\n📋 Что делать дальше:")
    print("  1. Проверьте что страница загрузилась правильно")
    print("  2. Проверьте что вы авторизованы")
    print("  3. Посмотрите на объявления")
    print("  4. Когда будете готовы - введите 'ok' для продолжения")
    print("\n⏳ Браузер остается открытым...\n")
    
    user_input = input("Введите 'ok' когда все проверите: ").strip().lower()
    
    if user_input == 'ok':
        print("\n✅ Отлично!")
        print(f"📍 Финальный URL: {driver.current_url}")
        
        print("\n💡 Браузер готов к парсингу")
        print("   Дайте указания что делать дальше")
        
        input("\nНажмите Enter для закрытия браузера...")
    
    print("\n⏳ Закрытие браузера...")
    driver.quit()
    print("✅ Браузер закрыт")

except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    print("\n💡 Возможные причины:")
    print("  • Chrome еще не закрыт полностью")
    print("  • Неправильный путь к профилю")
    print("  • Проблемы с ChromeDriver")
    
    import traceback
    traceback.print_exc()

print("\n🎉 Готово!")
