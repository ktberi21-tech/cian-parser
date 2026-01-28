import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/cian_db")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
