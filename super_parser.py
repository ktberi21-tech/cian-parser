"""
🕵️ СУПЕР-СКРЫТНЫЙ ПАРСЕР ЦИАН
Скачивает Excel со ВСЕХ страниц БЕЗ БЛОКИРОВКИ!
"""

import asyncio
import random
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
from playwright.async_api import async_playwright
import os

DOWNLOADS_DIR = Path.home() / "Downloads" / "cian_temp"
DOWNLOADS_DIR.mkdir(exist_ok=True)

class CianMegaScraper:
    def __init__(self):
        self.page = None
        self.context = None
        self.browser = None
        
    async def setup(self):
        """🔧 Запуск браузера с МАКСИМАЛЬНОЙ маскировкой"""
        p = await async_playwright().start()
        
        # Профиль с вашей авторизацией
        profile_path = str(Path.home() / ".playwright_profile")
        
        self.context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-popup-blocking",
                "--disable-extensions",
                "--disable-sync",
                "--disable-plugins",
                "--disable-component-update",
                "--disable-default-apps",
                "--disable-preconnect",
                "--metrics-recording-only",
                "--mute-audio",
                "--no-sandbox",
                "--disable-web-resources",
            ],
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
            accept_downloads=True,
            locale="ru-RU",
            timezone_id="Europe/Moscow",
        )
        
        self.page = await self.context.new_page()
        
        # 🔒 Маскируем WebDriver
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ru-RU', 'ru', 'en-US'],
            });
            window.chrome = {
                runtime: {}
            };
        """)
        
        print("✅ Браузер запущен с максимальной маскировкой")
    
    async def human_delay(self, min_sec=1, max_sec=3):
        """⏱️ Случайная задержка как у человека"""
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)
    
    async def random_mouse_moves(self, count=3):
        """🖱️ Случайные движения мыши"""
        for _ in range(count):
            x = random.randint(100, 1820)
            y = random.randint(100, 1000)
            await self.page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))
    
    async def smooth_scroll(self):
        """📜 Плавная прокрутка как у человека"""
        # Прокрутка вниз
        for _ in range(random.randint(3, 5)):
            scroll_amount = random.randint(200, 400)
            await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(random.uniform(0.3, 0.7))
        
        # Вернуть в начало для поиска кнопки
        await self.page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
    
    async def scrape_page(self, page_num, search_url):
        """📥 Скрейпинг одной страницы"""
        try:
            print(f"\n{'█'*70}")
            print(f"📄 СТРАНИЦА #{page_num}")
            print(f"{'█'*70}")
            
            # 1️⃣ Переход на страницу
            page_url = f"{search_url}&p={page_num}"
            print(f"🔗 Переходим: {page_url[:80]}...")
            
            await self.page.goto(page_url, wait_until="networkidle", timeout=30000)
            print(f"✅ Страница загружена")
            
            # 2️⃣ Имитация чтения страницы
            await self.human_delay(2, 4)
            await self.smooth_scroll()
            await self.random_mouse_moves(4)
            
            # 3️⃣ Поиск кнопки "Сохранить файл Excel"
            print("🔍 Ищем кнопку 'Сохранить файл Excel'...")
            
            # Попробуем разные селекторы кнопки
            button_selectors = [
                'a:has-text("Сохранить файл Excel")',
                'button:has-text("Сохранить файл Excel")',
                '[class*="download"]',
                'a[href*="xlsx"]',
            ]
            
            button = None
            for selector in button_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button:
                        print(f"✅ Кнопка найдена по селектору: {selector}")
                        break
                except:
                    continue
            
            if not button:
                print("❌ Кнопка не найдена! Ищем через текст...")
                # Ищем через JS
                button = await self.page.evaluate("""
                    () => {
                        const elements = Array.from(document.querySelectorAll('a, button, div[role="button"]'));
                        return elements.find(el => el.textContent.includes('Сохранить файл Excel'));
                    }
                """)
            
            if not button:
                print("❌ Кнопка не найдена на странице!")
                return False
            
            # 4️⃣ Скролл к кнопке
            await self.page.evaluate("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
            await self.human_delay(1, 2)
            
            # 5️⃣ Движение мыши к кнопке (как человек)
            await self.random_mouse_moves(3)
            
            box = await button.bounding_box()
            if box:
                # Случайный клик по кнопке
                x = box['x'] + box['width'] / 2 + random.uniform(-3, 3)
                y = box['y'] + box['height'] / 2 + random.uniform(-2, 2)
                
                await self.page.mouse.move(x, y)
                await self.human_delay(0.2, 0.5)
                
                # 🖱️ КЛИК!
                print("🖱️ Нажимаем кнопку...")
                await self.page.mouse.click()
            
            # 6️⃣ Ожидаем загрузки файла
            print("⏳ Ожидаем загрузки файла (макс 60 сек)...")
            
            try:
                async with self.page.expect_download(timeout=60000) as download_info:
                    await self.human_delay(1, 3)
                
                download = await download_info.value
                file_path = DOWNLOADS_DIR / f"page_{page_num:04d}.xlsx"
                
                # Сохраняем файл
                await download.save_as(str(file_path))
                
                file_size = file_path.stat().st_size
                print(f"✅ ФАЙЛ СОХРАНЕН!")
                print(f"   📁 {file_path.name}")
                print(f"   📊 Размер: {file_size / 1024:.1f} KB")
                
                return True
                
            except asyncio.TimeoutError:
                print("❌ Таймаут при загрузке файла!")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка на странице {page_num}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # 7️⃣ ОБЯЗАТЕЛЬНО: Ждем перед следующей страницей
            # Случайная задержка (ОЧЕНЬ ВАЖНО!)
            delay = random.uniform(8, 20)
            print(f"⏳ Ждем {delay:.1f} сек перед следующей страницей...")
            print(f"   (чтобы Циан не понял, что это робот)")
            await self.human_delay(delay - 3, delay)
    
    async def merge_excel_files(self):
        """📊 Объединение всех Excel файлов в один"""
        print(f"\n{'='*70}")
        print("🔗 ОБЪЕДИНЯЕМ ВСЕ ФАЙЛЫ В ОДИН!")
        print(f"{'='*70}")
        
        xlsx_files = sorted(DOWNLOADS_DIR.glob("page_*.xlsx"))
        
        if not xlsx_files:
            print("❌ Файлы не найдены!")
            return None
        
        print(f"📁 Найдено файлов: {len(xlsx_files)}")
        
        all_data = []
        
        for file_path in xlsx_files:
            try:
                print(f"   📖 Читаем: {file_path.name}...", end=" ")
                df = pd.read_excel(file_path)
                all_data.append(df)
                print(f"✅ ({len(df)} строк)")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                continue
        
        if not all_data:
            print("❌ Не удалось прочитать ни один файл!")
            return None
        
        # Объединяем все
        print(f"\n🔀 Объединяем...")
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Удаляем дубликаты
        print(f"🔍 Удаляем дубликаты...")
        original_count = len(combined_df)
        combined_df = combined_df.drop_duplicates()
        duplicates_count = original_count - len(combined_df)
        
        print(f"   • Было строк: {original_count}")
        print(f"   • Дубликатов: {duplicates_count}")
        print(f"   • Осталось: {len(combined_df)}")
        
        # Сохраняем результат
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path.home() / "Desktop" / f"cian_combined_{timestamp}.xlsx"
        
        print(f"\n💾 Сохраняем: {output_file.name}...")
        combined_df.to_excel(output_file, index=False)
        
        print(f"✅ ГОТОВО!")
        print(f"   📊 {output_file}")
        print(f"   📈 Всего объявлений: {len(combined_df)}")
        print(f"   📁 Размер: {output_file.stat().st_size / (1024*1024):.1f} MB")
        
        return output_file
    
    async def run(self, search_url, max_pages):
        """🚀 Главный цикл"""
        await self.setup()
        
        successful = 0
        failed = 0
        
        for page_num in range(1, max_pages + 1):
            success = await self.scrape_page(page_num, search_url)
            
            if success:
                successful += 1
            else:
                failed += 1
                print("⚠️ Повтор через 20 сек...")
                await self.human_delay(15, 25)
        
        print(f"\n{'='*70}")
        print(f"📊 СТАТИСТИКА СКАЧИВАНИЯ")
        print(f"{'='*70}")
        print(f"✅ Успешно скачано: {successful} страниц")
        print(f"❌ Ошибок: {failed}")
        
        # Объединяем файлы
        await self.merge_excel_files()
        
        await self.context.close()

async def main():
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         🕵️  МЕГА-СКРЫТНЫЙ ПАРСЕР ЦИАН (Excel скачиватель)        ║")
    print("║         Скачиваем без блокировки через маскировку!                ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")
    
    # Ваша ссылка для поиска (без ?p=N)
    search_url = input("📌 Введите URL вашего поиска на ЦИАН (без ?p=): ").strip()
    if not search_url:
        search_url = "https://www.cian.ru/sale/flat/?bez_apartamentov=1&room1=1&room2=1&room3=1&room4=1&room5=1"
    
    max_pages = int(input("📝 Сколько страниц скрейпить? (рекомендуем 2-5 для теста): ").strip() or "3")
    
    scraper = CianMegaScraper()
    await scraper.run(search_url, max_pages)

if __name__ == "__main__":
    asyncio.run(main())
