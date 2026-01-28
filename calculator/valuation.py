import statistics
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class ValuationCalculator:
    def __init__(self, db):
        self.db = db
        self.flats_collection = db["flats"]

    def find_analogues(self, target: Dict, radius_m: int = 2500, limit: int = 20) -> List[Dict]:
        """Поиск аналогов по гео и параметрам."""
        if not target.get("location"):
            logger.warning(f"Target has no location: {target.get('url')}")
            return []
        
        min_area = target.get("total_area", 50) * 0.85
        max_area = target.get("total_area", 50) * 1.15
        min_year = target.get("year_built", 1980) - 10
        max_year = target.get("year_built", 1980) + 10
        
        query = {
            "city": target.get("city", "Москва"),
            "rooms": target.get("rooms"),
            "location": {
                "$near": {
                    "$geometry": target["location"],
                    "$maxDistance": radius_m,
                }
            },
            "total_area": {"$gte": min_area, "$lte": max_area},
            "year_built": {"$gte": min_year, "$lte": max_year},
            "url": {"$ne": target["url"]}
        }
        
        analogues = list(
            self.flats_collection.find(query).limit(limit)
        )
        
        logger.info(f"Found {len(analogues)} analogues for {target.get('url')}")
        return analogues

    def calculate(self, target: Dict, roi: float = 0.18, repair_cost_per_sqm: int = 35000, other_costs_ratio: float = 0.05) -> Dict:
        """Расчёт оценки квартиры и выкупной цены."""
        analogues = self.find_analogues(target)
        
        if not analogues:
            logger.warning("No analogues found")
            return {"error": "No analogues found"}
        
        ppms = [a.get("price_per_sqm") for a in analogues if a.get("price_per_sqm")]
        if not ppms:
            return {"error": "No price data in analogues"}
        
        ppm_est = statistics.median(ppms)
        estimated_price = ppm_est * target.get("total_area", 40)
        repair_cost = repair_cost_per_sqm * target.get("total_area", 40)
        other_costs = estimated_price * other_costs_ratio
        net_after_costs = estimated_price - repair_cost - other_costs
        
        roi_range = {}
        for roi_pct in [18, 19, 20, 21, 22, 23, 24, 25]:
            roi_decimal = roi_pct / 100
            buyout = net_after_costs / (1 + roi_decimal)
            roi_range[roi_pct] = round(buyout)
        
        listing_price = target.get("price", estimated_price)
        buyout_price = roi_range[18]
        discount = (1 - buyout_price / listing_price) * 100 if listing_price > 0 else 0
        
        return {
            "price_per_sqm_est": round(ppm_est),
            "estimated_price": round(estimated_price),
            "repair_cost": round(repair_cost),
            "other_costs": round(other_costs),
            "buyout_price": buyout_price,
            "discount_percent": round(discount, 2),
            "roi_range": roi_range,
            "analogues": [
                {
                    "address": a.get("address"),
                    "price": a.get("price"),
                    "price_per_sqm": a.get("price_per_sqm"),
                    "total_area": a.get("total_area"),
                    "url": a.get("url"),
                    "location": a.get("location"),
                }
                for a in analogues
            ],
        }
