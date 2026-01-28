import logging
import asyncio
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from cian_parser import CianParser

logger = logging.getLogger(__name__)

class ParserScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.parser = CianParser()

    def run_parser_task(self):
        """Функция для запуска парсера из расписания."""
        logger.info("🚀 Starting scheduled parser run...")
        try:
            asyncio.run(self.parser.run_parser(max_flats=50))
            logger.info("✅ Parser finished successfully")
        except Exception as e:
            logger.error(f"❌ Parser failed: {e}")

    def start(self):
        """Запуск расписания."""
        trigger = CronTrigger(hour=9, minute=0, timezone="Europe/Moscow")
        
        self.scheduler.add_job(
            self.run_parser_task,
            trigger=trigger,
            id="cian_parser_job",
            name="CIAN Parser",
            replace_existing=True,
        )
        
        self.scheduler.start()
        logger.info("📅 Scheduler started. Parser will run at 09:00 Moscow time daily.")

    def stop(self):
        """Остановка расписания."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scheduler = ParserScheduler()
    scheduler.start()
    
    try:
        asyncio.run(asyncio.sleep(3600))
    except KeyboardInterrupt:
        scheduler.stop()
