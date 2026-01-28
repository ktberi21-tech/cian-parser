import random
import time
import logging

logger = logging.getLogger(__name__)

class CianParserProtected:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        self.parsed_count = 0
        self.skipped_count = 0
        self.error_count = 0
    
    def _random_delay(self, min_sec=0.1, max_sec=0.3):
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def run(self, db_model=None, max_flats=50):
        logger.info(f"🚀 Starting parser (max_flats={max_flats}, mock={self.use_mock})")
        
        if self.use_mock:
            self._run_mock_mode(db_model, max_flats)
        else:
            self._run_real_mode(db_model, max_flats)
        
        logger.info(f"✅ DONE! Parsed: {self.parsed_count}, Skipped: {self.skipped_count}, Errors: {self.error_count}")
    
    def _run_mock_mode(self, db_model, max_flats):
        try:
            from mock_data import MOCK_FLATS
        except Exception as e:
            logger.error(f"Error importing mock_data: {e}")
            return
        
        flats_to_process = MOCK_FLATS * ((max_flats // len(MOCK_FLATS)) + 1)
        random.shuffle(flats_to_process)
        
        for flat in flats_to_process[:max_flats]:
            self._random_delay(0.1, 0.3)
            
            if db_model:
                try:
                    result = db_model.upsert_flat(flat)
                    if result in ("new", "updated"):
                        self.parsed_count += 1
                    else:
                        self.skipped_count += 1
                except Exception as e:
                    logger.error(f"Error saving: {e}")
                    self.error_count += 1
    
    def _run_real_mode(self, db_model, max_flats):
        logger.info("Real mode not implemented yet")
        self._run_mock_mode(db_model, max_flats)
