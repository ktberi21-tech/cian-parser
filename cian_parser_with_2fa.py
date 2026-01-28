#!/usr/bin/env python3
"""
ЦИАН ПАРСЕР С ПОДДЕРЖКОЙ SMS КОД
Заходит на главную страницу, нажимает "Войти", выбирает аккаунт
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from pathlib import Path
import sys

# Конфиг
CIAN_EMAIL = "kiruha_777@mail.ru"
CIAN_PASSWORD = "Cian459396958130191"
CIAN_SEARCH_URL = "https://www.cian.ru/sale/flat/?bez_apartamentov=1&price_min=1000000&price_max=50000000"

print("="*80)
print("🚀 ЦИАН ПАРСЕР - ЗАПУСК")
print("="*80)

# Создаем папку для скачивания
download_dir = str(Path.home() / "Downloads" / "cian_temp")
os.makedirs(download_dir, exist_ok=True)
print(f"✅ Папка для скачивания: {download_dir}\n")

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

print("⏳ Запуск браузера Chrome...")
try:
    driver = uc.Chrome(options=options, version_main=None)
except Exception as e:
    print(f"❌ Ошибка при запуске браузера: {e}")
    sys.exit(1)

try:
    # ========== ПЕРЕХОД НА ГЛАВНУЮ СТРАНИЦУ ==========
    print("\n📝 ШАГ 1: Переход на главную страницу ЦИАН")
    driver.get("https://www.cian.ru")
    time.sleep(5)
    print(f"📍 URL: {driver.current_url}")
    
    # ========== НАЖАТИЕ КНОПКИ "ВОЙТИ" ==========
    print("\n📝 ШАГ 2: Поиск кнопки 'Войти'")
    
    try:
        # Ищем кнопку "Войти" на главной странице
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Войти')]"))
        )
        print("  ✅ Кнопка 'Войти' найдена")
        login_button.click()
        print("  ✅ Кнопка нажата")
    except Exception as e:
        print(f"  ❌ Ошибка при поиске кнопки: {e}")
        driver.save_screenshot("login_button_error.png")
        raise
    
    time.sleep(3)
    
    # ========== ВЫБОР АККАУНТА ==========
    print("\n📝 ШАГ 3: Выбор аккаунта из списка")
    
    try:
        # Ищем кнопку с нашим email
        account_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{CIAN_EMAIL}')]"))
        )
        print(f"  ✅ Аккаунт '{CIAN_EMAIL}' найден")
        account_button.click()
        print(f"  ✅ Аккаунт выбран")
    except Exception as e:
        print(f"  ❌ Ошибка при выборе аккаунта: {e}")
        print("  ℹ️  Возможно нужно ввести пароль вручную")
        print("  📸 Делаю скриншот...")
        driver.save_screenshot("account_selection_error.png")
        
        # Попытаемся найти поле пароля
        try:
            password_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
            )
            print("  ℹ️  Найдено поле пароля - вводим пароль...")
            password_input.clear()
            password_input.send_keys(CIAN_PASSWORD)
            print("  ✅ Пароль введен")
            
            # Нажимаем кнопку подтверждения
            confirm_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Войти') or contains(text(), 'Подтвердить')]")
            confirm_button.click()
            print("  ✅ Пароль отправлен")
        except:
            raise Exception("Не удалось ни выбрать аккаунт, ни ввести пароль")
    
    time.sleep(5)
    
    # ========== ПРОВЕРКА 2FA ==========
    print("\n📱 ШАГ 4: Проверка требуется ли SMS код")
    
    try:
        code_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @placeholder]"))
        )
        
        # Проверяем, что это поле для SMS кода
        if "code" in code_input.get_attribute("name") or "code" in code_input.get_attribute("placeholder"):
            print("\n" + "="*80)
            print("⏸️  ТРЕБУЕТСЯ КОД ИЗ SMS!")
            print("="*80)
            print("📱 На номер вашего телефона отправлено СМС сообщение")
            print("📝 Проверьте телефон и введите 6-значный код")
            print("="*80 + "\n")
            
            code = input("🔐 Введите код из SMS: ").strip()
            
            if not code or len(code) < 4:
                print("❌ Код не введен или слишком короткий!")
                raise Exception("SMS код не введен")
            
            code_input.clear()
            code_input.send_keys(code)
            print(f"✅ Код '{code}' введен")
            
            time.sleep(2)
            
            # Нажимаем подтверждение
            try:
                confirm_btn = driver.find_element(By.XPATH, "//button[contains(., 'Подтвердить') or contains(., 'OK')]")
                confirm_btn.click()
                print("✅ Нажата кнопка подтверждения")
            except:
                print("ℹ️  Автоподтверждение кода...")
            
            time.sleep(5)
    except:
        print("✅ 2FA не требуется - авторизация успешна!")
    
    time.sleep(3)
    
    # ========== ПРОВЕРКА СТАТУСА ==========
    print("\n🔍 ШАГ 5: Проверка авторизации")
    print(f"📍 Текущый URL: {driver.current_url}")
    
    if "login" not in driver.current_url.lower():
        print("✅ АВТОРИЗАЦИЯ УСПЕШНА!")
        
        print("\n" + "="*80)
        print("✅ ПАРСЕР УСПЕШНО ЗАПУЩЕН И АВТОРИЗОВАН!")
        print("="*80)
        print(f"✅ Email: {CIAN_EMAIL}")
        print(f"✅ Текущий URL: {driver.current_url}")
        print("="*80)
        
        # Переход к поиску
        print("\n🔍 ШАГ 6: Переход к результатам поиска")
        driver.get(CIAN_SEARCH_URL)
        time.sleep(8)
        print(f"✅ Открыта страница поиска")
        
        # Проверяем что загрузились результаты
        try:
            results = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@class*='OfferCard']"))
            )
            print(f"✅ Загружено предложений: {len(results)}")
        except:
            print("ℹ️  Результаты еще загружаются...")
        
    else:
        print("❌ Все еще на странице входа - авторизация не удалась!")
        driver.save_screenshot("auth_failed.png")
        raise Exception("Authorization failed")
    
    print("\n" + "="*80)
    print("🎉 ГОТОВО!")
    print("="*80)
    print("💡 Теперь можно продолжить с парсингом или закрыть браузер")
    print("="*80 + "\n")
    
    # Оставляем браузер открытым для проверки
    input("Нажмите Enter для закрытия браузера...")
    
except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    
    try:
        driver.save_screenshot("error_screenshot.png")
        print("\n📸 Скриншот ошибки сохранен: error_screenshot.png")
    except:
        pass

finally:
    print("\n⏳ Закрытие браузера...")
    try:
        driver.quit()
        print("✅ Браузер закрыт")
    except:
        pass

print("\n🎉 Парсер завершил работу!")
