"""
Business Service - Domain Logic
Handles business data operations
"""

from typing import List, Dict, Any
from .mock_data import get_businesses, search_businesses

class BusinessService:
    """Service for business data operations"""
    
    def __init__(self):
        self._cache = {}
    
    def get_businesses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get businesses with caching"""
        cache_key = f"businesses_{limit}"
        
        if cache_key not in self._cache:
            # In a real implementation, this might query a database
            # For demo, we use rich mock data
            self._cache[cache_key] = get_businesses(limit)
        
        return self._cache[cache_key]
    
    def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search businesses"""
        results = search_businesses(query, limit)
        
        return {
            "query": query,
            "results": results,
            "total": len(results),
            "search_type": "mock_text_search"
        }
    
    def get_business_by_id(self, business_id: int) -> Dict[str, Any]:
        """Get single business by ID"""
        businesses = self.get_businesses(100)  # Get all for search
        
        for business in businesses:
            if business["id"] == business_id:
                return business
        
        return None