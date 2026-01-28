import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/cian_db")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# CIAN Parser
CIAN_EMAIL = os.getenv("CIAN_EMAIL")
CIAN_PASSWORD = os.getenv("CIAN_PASSWORD")
CIAN_SEARCH_URL = os.getenv("CIAN_SEARCH_URL")
MAX_PAGES = int(os.getenv("MAX_PAGES", "2"))
