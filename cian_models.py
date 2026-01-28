import logging
from pymongo import MongoClient
from datetime import datetime

logger = logging.getLogger(__name__)

class CianDBConnection:
    def __init__(self, mongo_uri):
        self.mongo_uri = mongo_uri
        self.client = None
        self.db = None
    
    def connect(self):
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client['cian_db']
            logger.info("✅ MongoDB connected")
            return self.db
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return None
    
    def close(self):
        if self.client:
            self.client.close()

class CianFlatModel:
    def __init__(self, db):
        self.db = db
        self.collection = db['flats'] if db is not None else None
    
    def upsert_flat(self, flat_data):
        """Insert or update flat"""
        if self.collection is None:
            return 'error'
        
        try:
            cian_id = flat_data.get('cian_id')
            if not cian_id:
                return 'error'
            
            flat_data['updated_at'] = datetime.utcnow().isoformat()
            
            result = self.collection.update_one(
                {'cian_id': cian_id},
                {'$set': flat_data},
                upsert=True
            )
            
            if result.upserted_id:
                return 'new'
            return 'updated'
        except Exception as e:
            logger.error(f"Upsert error: {e}")
            return 'error'
    
    def get_all_flats(self, limit=10):
        """Get all flats"""
        if self.collection is None:
            return []
        try:
            return list(self.collection.find({}).limit(limit))
        except Exception as e:
            logger.error(f"Get flats error: {e}")
            return []
    
    def get_stats(self):
        """Get statistics"""
        if self.collection is None:
            return {"total_flats": 0}
        try:
            total = self.collection.count_documents({})
            return {"total_flats": total}
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {"total_flats": 0, "error": str(e)}
