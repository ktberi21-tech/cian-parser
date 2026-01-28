import asyncio, random
from pathlib import Path
from datetime import datetime
import pandas as pd
from playwright.async_api import async_playwright

DOWNLOADS_DIR = Path.home() / "Downloads" / "cian_temp"
DOWNLOADS_DIR.mkdir(exist_ok=True)

SEARCH_URL = "https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&object_type%5B0%5D=1&offer_type=flat&only_flat=1&region=1&room1=1&room2=1&room3=1&room4=1&room5=1&saved_search_id=55818992"

class CianParser:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    async def setup(self):
        p = await async_playwright().start()
        self.browser = await p.chromium.launch(
            headless=False,
            args=["--disable-dev-shm-usage"],
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            accept_downloads=True,
            locale="ru-RU",
        )
        self.page = await self.context.new_page()
        print("✅ Chromium запущен")

    async def delay(self, a=1, b=3):
        await asyncio.sleep(random.uniform(a, b))

    async def manual_login(self):
        """Даём тебе залогиниться руками один раз."""
        print("\n🔐 ЭТАП 1. Ручной вход в ЦИАН")
        print("   1) Сейчас откроется страница поиска.")
        print("   2) Нажми 'Сохранить файл в Excel' → пройди SMS → выбери аккаунт.")
        print("   3) Убедись, что ты снова видишь выдачу объявлений.")
        print("   4) Вернись в терминал и нажми Enter.\n")

        await self.page.goto(SEARCH_URL, timeout=180_000)
        await self.delay(5, 7)

        input("⏸ Когда авторизация полностью закончена и ты видишь список объявлений, нажми Enter здесь... ")

    async def click_excel_on_page(self, page_num: int):
        try:
            print(f"\n📄 СТРАНИЦА #{page_num}")
            url = f"{SEARCH_URL}&p={page_num}"
            await self.page.goto(url, wait_until="domcontentloaded", timeout=180_000)
            await self.delay(3, 5)

            # Скролл вниз — там обычно появляется блок с аналитикой / Excel
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.delay(3, 5)

            print("🔍 Ищу кнопку 'Сохранить файл в Excel'...")
            btn = await self.page.get_by_text("Сохранить файл в Excel")

            await btn.scroll_into_view_if_needed()
            await self.delay(1, 2)

            print("🖱 Жму 'Сохранить файл в Excel' и жду download...")
            async with self.page.expect_download(timeout=180_000) as d_info:
                await btn.click()
                await self.delay(2, 4)

            download = await d_info.value
            target = DOWNLOADS_DIR / f"page_{page_num:04d}.xlsx"
            await download.save_as(str(target))
            print(f"✅ Файл сохранён: {target.name}")
            await self.delay(5, 8)
            return True
        except Exception as e:
            print(f"❌ Ошибка на странице {page_num}: {e}")
            return False

    async def merge_files(self):
        files = sorted(DOWNLOADS_DIR.glob("page_*.xlsx"))
        if not files:
            print("❌ Файлы для объединения не найдены")
            return

        dfs = []
        for f in files:
            try:
                df = pd.read_excel(f)
                dfs.append(df)
                print(f"✅ Прочитан {f.name}: {len(df)} строк")
            except Exception as e:
                print(f"⚠️ Не удалось прочитать {f.name}: {e}")

        if not dfs:
            print("❌ Нет валидных файлов для объединения")
            return

        combined = pd.concat(dfs, ignore_index=True).drop_duplicates()
        out = Path.home() / "Desktop" / f"cian_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        combined.to_excel(out, index=False)
        print(f"\n✅ Итоговый файл: {out} (строк: {len(combined)})")

    async def run(self, pages: int):
        await self.setup()
        await self.manual_login()

        success = errors = 0
        for i in range(1, pages + 1):
            if await self.click_excel_on_page(i):
                success += 1
            else:
                errors += 1

        print(f"\n========== РЕЗУЛЬТАТ ==========")
        print(f"✅ Успешно страниц: {success}")
        print(f"❌ Ошибок: {errors}")
        print("================================\n")

        await self.merge_files()
        await self.context.close()
        await self.browser.close()

async def main():
    pages = int(input("📝 Сколько страниц скачать? ") or "1")
    parser = CianParser()
    await parser.run(pages)

if __name__ == "__main__":
    asyncio.run(main())

