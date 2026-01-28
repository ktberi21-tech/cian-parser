import sys
from config import CIAN_EMAIL, CIAN_PASSWORD, CIAN_SEARCH_URL, MAX_PAGES
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from pathlib import Path

print("🚀 ЗАПУСК ПАРСЕРА ЦИАН")
print(f"📧 Email: {CIAN_EMAIL}")
print(f"🔗 URL: {CIAN_SEARCH_URL}")
print(f"📄 Страниц: {MAX_PAGES}")

# Создаем папку для скачивания
download_dir = str(Path.home() / "Downloads" / "cian_temp")
os.makedirs(download_dir, exist_ok=True)

# Настройки Chrome
options = uc.ChromeOptions()
options.add_argument(f"--user-data-dir={download_dir}")
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
}
options.add_experimental_option("prefs", prefs)

print("\n✅ Инициализация браузера...")
driver = uc.Chrome(options=options)

try:
    # Вход в аккаунт
    print("✅ Переход на ЦИАН...")
    driver.get("https://www.cian.ru/login")
    time.sleep(5)
    
    # Поиск полей для ввода
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    email_input.send_keys(CIAN_EMAIL)
    
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(CIAN_PASSWORD)
    
    # Нажимаем кнопку "Войти"
    login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Войти')]")
    login_btn.click()
    
    print("✅ Авторизация...")
    time.sleep(10)
    
    # Переходим к поиску
    print("✅ Переход к фильтрам...")
    driver.get(CIAN_SEARCH_URL)
    time.sleep(5)
    
    print("✅ Скачивание Excel файлов...")
    
    # TODO: Добавить логику скачивания
    print(f"✅ Готово! Файлы в {download_dir}")

except Exception as e:
    print(f"❌ Ошибка: {e}")

finally:
    driver.quit()
