"""
Weaviate Integration Service for Legacy Business Registry
========================================================

Provides semantic search, data ingestion, and query capabilities with
comprehensive mock fallback for development and demo environments.

Features:
- Automatic mock/live mode detection
- Semantic search with vector similarity
- Business data listing and filtering
- Query agent stubs for future RAG implementation
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

try:
    import weaviate
    from weaviate.classes.init import Auth
    from weaviate.classes.query import MetadataQuery
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

from models.legacy_business import LegacyBusiness, LegacyBusinessSummary, LegacyBusinessSearch, NeighborhoodEnum

logger = logging.getLogger(__name__)


class SearchMode(str, Enum):
    """Search operation modes"""
    SEMANTIC = "semantic"           # Vector similarity search
    HYBRID = "hybrid"              # Vector + keyword combination  
    KEYWORD = "keyword"            # Traditional text search
    SIMILARITY = "similarity"      # Find similar to specific object


@dataclass
class SearchResult:
    """Standardized search result format"""
    business: LegacyBusinessSummary
    score: float
    distance: Optional[float] = None
    certainty: Optional[float] = None
    search_mode: Optional[str] = None
    
    @property
    def confidence(self) -> float:
        """Unified confidence score (0-1)"""
        if self.certainty is not None:
            return self.certainty
        elif self.distance is not None:
            return max(0, 1 - self.distance)
        else:
            return self.score


@dataclass
class SearchResponse:
    """Complete search response with metadata"""
    results: List[SearchResult]
    total_count: int
    query: str
    search_mode: SearchMode
    execution_time_ms: float
    used_fallback: bool = False
    
    @property
    def has_results(self) -> bool:
        return len(self.results) > 0
    
    @property
    def average_confidence(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.confidence for r in self.results) / len(self.results)


class MockWeaviateService:
    """Mock Weaviate service for development and demo environments"""
    
    def __init__(self):
        self.mock_businesses = self._load_mock_data()
        logger.info(f"MockWeaviateService initialized with {len(self.mock_businesses)} businesses")
    
    def _load_mock_data(self) -> List[Dict[str, Any]]:
        """Load realistic mock data that matches our LegacyBusiness model"""
        return [
            {
                "business_name": "The Wok Shop",
                "founding_year": 1972,
                "neighborhood": "Chinatown",
                "business_type": "Kitchen Supply Store",
                "founding_story": "Founded after Nixon's 1972 China trip when Americans became interested in authentic Chinese cooking. Started by importing traditional woks and cooking equipment directly from China.",
                "cultural_significance": "Serves as cultural ambassador teaching wok cooking to international audience. Bridge between traditional Chinese cooking techniques and American home kitchens.",
                "unique_features": ["Original 1970s pagoda neon sign", "Woks hanging from ceiling", "International shipping"],
                "demo_highlights": ["Featured on PBS cooking shows", "International customer base", "50+ years serving SF Chinatown"],
                "heritage_score": 92,
                "current_status": "active"
            },
            {
                "business_name": "Swan Oyster Depot",
                "founding_year": 1912,
                "neighborhood": "Nob Hill", 
                "business_type": "Seafood Counter",
                "founding_story": "Started by four Italian immigrant brothers who wanted to bring fresh seafood to San Francisco. Family has been serving the same recipes for over 100 years.",
                "cultural_significance": "Iconic SF institution representing old-school Italian-American seafood culture. Unchanged counter service preserves authentic dining experience.",
                "unique_features": ["Original marble counter from 1912", "No reservations policy", "Same family recipes since 1912"],
                "demo_highlights": ["Century-old family business", "Celebrity chef destination", "Unchanged since 1912"],
                "heritage_score": 98,
                "current_status": "active"
            },
            {
                "business_name": "Green Apple Books",
                "founding_year": 1967,
                "neighborhood": "Richmond",
                "business_type": "Independent Bookstore", 
                "founding_story": "Founded during the Summer of Love by a UC Berkeley graduate who wanted to create a community gathering place for book lovers and intellectuals.",
                "cultural_significance": "Cultural hub for Richmond District literary community. Survived digital disruption by emphasizing curation and community events.",
                "unique_features": ["Floor-to-ceiling rare book stacks", "Poetry reading events", "Local author showcase"],
                "demo_highlights": ["Survived digital book revolution", "Community poetry readings", "50+ years of literary culture"],
                "heritage_score": 85,
                "current_status": "active"
            },
            {
                "business_name": "Tartine Bakery",
                "founding_year": 2002,
                "neighborhood": "Mission District",
                "business_type": "Artisan Bakery",
                "founding_story": "Started by a couple who trained in French pastry techniques and wanted to bring artisanal bread culture to San Francisco's Mission District.",
                "cultural_significance": "Revolutionized SF bread culture and helped transform Mission District into culinary destination. Inspired entire generation of artisan bakers.",
                "unique_features": ["Open kitchen design", "Naturally fermented sourdough", "Seasonal ingredient focus"],
                "demo_highlights": ["James Beard Award winner", "Cookbook bestsellers", "International culinary influence"],
                "heritage_score": 78,
                "current_status": "active"
            },
            {
                "business_name": "City Lights Bookstore",
                "founding_year": 1953,
                "neighborhood": "North Beach",
                "business_type": "Independent Bookstore",
                "founding_story": "Founded by poet Lawrence Ferlinghetti as a paperback bookstore and literary meeting place. Became center of Beat Generation literary movement.",
                "cultural_significance": "Historic center of Beat poetry movement. First bookstore to sell only paperbacks. Literary landmark that shaped American counterculture.",
                "unique_features": ["Beat Generation poetry section", "Author reading events", "24/7 operation during Beat era"],
                "demo_highlights": ["Beat Generation headquarters", "National Historic Landmark", "Literary pilgrimage destination"],
                "heritage_score": 95,
                "current_status": "active"
            }
        ]
    
    async def list_all_businesses(self, limit: int = 50) -> List[LegacyBusinessSummary]:
        """List all businesses with optional limit"""
        businesses = []
        for business_data in self.mock_businesses[:limit]:
            businesses.append(LegacyBusinessSummary(**business_data))
        return businesses
    
    async def search_businesses(self, search_request: LegacyBusinessSearch) -> SearchResponse:
        """Mock semantic search with realistic scoring"""
        start_time = datetime.now()
        
        query_lower = search_request.query.lower()
        results = []
        
        for business_data in self.mock_businesses:
            # Calculate mock relevance score
            score = self._calculate_mock_relevance(business_data, query_lower)
            
            # Apply filters
            if not self._passes_filters(business_data, search_request):
                continue
            
            # Only include results above similarity threshold
            if score >= search_request.similarity_threshold:
                result = SearchResult(
                    business=LegacyBusinessSummary(**business_data),
                    score=score,
                    certainty=score,  # Mock certainty as score
                    search_mode=SearchMode.SEMANTIC.value
                )
                results.append(result)
        
        # Sort by score and limit
        results.sort(key=lambda x: x.score, reverse=True)
        results = results[:search_request.limit]
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return SearchResponse(
            results=results,
            total_count=len(results),
            query=search_request.query,
            search_mode=SearchMode.SEMANTIC,
            execution_time_ms=execution_time,
            used_fallback=True
        )
    
    def _calculate_mock_relevance(self, business_data: Dict[str, Any], query: str) -> float:
        """Calculate realistic relevance score for mock search"""
        score = 0.0
        
        # Business name match (high weight)
        if query in business_data.get("business_name", "").lower():
            score += 0.4
        
        # Business type match (medium weight)
        if query in business_data.get("business_type", "").lower():
            score += 0.3
        
        # Narrative content match (high weight for semantic)
        story = business_data.get("founding_story", "").lower()
        significance = business_data.get("cultural_significance", "").lower()
        
        if query in story:
            score += 0.35
        if query in significance:
            score += 0.35
        
        # Partial matches in unique features
        features = business_data.get("unique_features", [])
        for feature in features:
            if query in feature.lower():
                score += 0.2
                break
        
        # Keyword-based semantic similarity simulation
        semantic_keywords = {
            "traditional": ["family", "authentic", "original", "heritage"],
            "food": ["restaurant", "bakery", "seafood", "cooking"],
            "books": ["bookstore", "literary", "poetry", "reading"],
            "culture": ["cultural", "community", "heritage", "historic"],
            "chinese": ["china", "wok", "cooking", "chinatown"],
            "italian": ["italian", "family", "authentic"]
        }
        
        for main_keyword, related_words in semantic_keywords.items():
            if main_keyword in query:
                for word in related_words:
                    if any(word in text.lower() for text in [
                        business_data.get("founding_story", ""),
                        business_data.get("cultural_significance", ""),
                        business_data.get("business_type", "")
                    ]):
                        score += 0.15
                        break
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _passes_filters(self, business_data: Dict[str, Any], search_request: LegacyBusinessSearch) -> bool:
        """Check if business passes search filters"""
        # Neighborhood filter
        if search_request.neighborhood:
            if business_data.get("neighborhood") != search_request.neighborhood.value:
                return False
        
        # Business type filter
        if search_request.business_type:
            if search_request.business_type.lower() not in business_data.get("business_type", "").lower():
                return False
        
        # Founding year range
        founding_year = business_data.get("founding_year")
        if founding_year:
            if search_request.founding_year_min and founding_year < search_request.founding_year_min:
                return False
            if search_request.founding_year_max and founding_year > search_request.founding_year_max:
                return False
        
        # Heritage score minimum
        if search_request.heritage_score_min:
            heritage_score = business_data.get("heritage_score", 0)
            if heritage_score < search_request.heritage_score_min:
                return False
        
        return True
    
    async def get_business_by_name(self, name: str) -> Optional[LegacyBusinessSummary]:
        """Get business by exact name match"""
        for business_data in self.mock_businesses:
            if business_data["business_name"].lower() == name.lower():
                return LegacyBusinessSummary(**business_data)
        return None
    
    async def get_similar_businesses(self, business_name: str, limit: int = 5) -> List[SearchResult]:
        """Find businesses similar to the given business"""
        # Find target business
        target_business = None
        for business_data in self.mock_businesses:
            if business_data["business_name"].lower() == business_name.lower():
                target_business = business_data
                break
        
        if not target_business:
            return []
        
        # Calculate similarity to other businesses
        results = []
        target_type = target_business.get("business_type", "").lower()
        target_neighborhood = target_business.get("neighborhood", "")
        
        for business_data in self.mock_businesses:
            if business_data["business_name"] == target_business["business_name"]:
                continue  # Skip self
            
            # Mock similarity calculation
            similarity = 0.0
            
            # Business type similarity
            if target_type in business_data.get("business_type", "").lower():
                similarity += 0.4
            
            # Neighborhood similarity  
            if target_neighborhood == business_data.get("neighborhood"):
                similarity += 0.3
            
            # Era similarity (founding year)
            target_year = target_business.get("founding_year", 0)
            business_year = business_data.get("founding_year", 0)
            if target_year and business_year:
                year_diff = abs(target_year - business_year)
                if year_diff < 20:
                    similarity += 0.3
                elif year_diff < 50:
                    similarity += 0.2
            
            if similarity >= 0.5:  # Minimum similarity threshold
                result = SearchResult(
                    business=LegacyBusinessSummary(**business_data),
                    score=similarity,
                    certainty=similarity,
                    search_mode=SearchMode.SIMILARITY.value
                )
                results.append(result)
        
        # Sort by similarity and limit
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get mock service status"""
        return {
            "mode": "mock",
            "collection_name": "LegacyBusiness",
            "total_objects": len(self.mock_businesses),
            "vectorizer": "mock-text2vec-openai",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "features": {
                "semantic_search": True,
                "similarity_search": True,
                "filtering": True,
                "hybrid_search": False  # Not implemented in mock
            }
        }


class WeaviateService:
    """Production Weaviate service with comprehensive functionality"""
    
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        self.url = url or os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.api_key = api_key or os.getenv("WEAVIATE_API_KEY")
        self.client = None
        self.collection_name = "LegacyBusiness"
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Establish connection to Weaviate"""
        if not WEAVIATE_AVAILABLE:
            logger.warning("Weaviate client library not available")
            return False
        
        try:
            auth = Auth.api_key(self.api_key) if self.api_key else None
            self.client = weaviate.connect_to_custom(
                http_host=self.url.replace("http://", "").replace("https://", ""),
                http_port=8080,
                http_secure=self.url.startswith("https://"),
                auth=auth
            )
            
            self.is_connected = self.client.is_ready()
            if self.is_connected:
                logger.info(f"Connected to Weaviate at {self.url}")
            else:
                logger.warning(f"Weaviate not ready at {self.url}")
            
            return self.is_connected
            
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            return False
    
    async def list_all_businesses(self, limit: int = 50) -> List[LegacyBusinessSummary]:
        """List all businesses from Weaviate"""
        if not self.client:
            raise ConnectionError("Weaviate client not connected")
        
        try:
            collection = self.client.collections.get(self.collection_name)
            
            response = collection.query.fetch_objects(
                limit=limit,
                include_vector=False
            )
            
            businesses = []
            for obj in response.objects:
                # Convert Weaviate object to our model
                business_data = obj.properties
                businesses.append(LegacyBusinessSummary(**business_data))
            
            return businesses
            
        except Exception as e:
            logger.error(f"Failed to list businesses: {e}")
            raise
    
    async def search_businesses(self, search_request: LegacyBusinessSearch) -> SearchResponse:
        """Perform semantic search in Weaviate"""
        if not self.client:
            raise ConnectionError("Weaviate client not connected")
        
        start_time = datetime.now()
        
        try:
            collection = self.client.collections.get(self.collection_name)
            
            # Build search query based on search fields
            response = collection.query.near_text(
                query=search_request.query,
                limit=search_request.limit,
                offset=search_request.offset,
                return_metadata=MetadataQuery(certainty=True, distance=True),
                where=self._build_where_filter(search_request)
            )
            
            results = []
            for obj in response.objects:
                metadata = obj.metadata
                certainty = metadata.certainty if metadata else None
                distance = metadata.distance if metadata else None
                
                result = SearchResult(
                    business=LegacyBusinessSummary(**obj.properties),
                    score=certainty or (1 - distance) if distance else 0.5,
                    certainty=certainty,
                    distance=distance,
                    search_mode=SearchMode.SEMANTIC.value
                )
                results.append(result)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return SearchResponse(
                results=results,
                total_count=len(results),  # Weaviate doesn't easily provide total count
                query=search_request.query,
                search_mode=SearchMode.SEMANTIC,
                execution_time_ms=execution_time,
                used_fallback=False
            )
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def _build_where_filter(self, search_request: LegacyBusinessSearch) -> Optional[Dict]:
        """Build Weaviate where filter from search request"""
        filters = []
        
        # Neighborhood filter
        if search_request.neighborhood:
            filters.append({
                "path": ["neighborhood"],
                "operator": "Equal",
                "valueText": search_request.neighborhood.value
            })
        
        # Business type filter
        if search_request.business_type:
            filters.append({
                "path": ["business_type"],
                "operator": "Like",
                "valueText": f"*{search_request.business_type}*"
            })
        
        # Founding year range
        if search_request.founding_year_min:
            filters.append({
                "path": ["founding_year"],
                "operator": "GreaterThanEqual",
                "valueInt": search_request.founding_year_min
            })
        
        if search_request.founding_year_max:
            filters.append({
                "path": ["founding_year"],
                "operator": "LessThanEqual", 
                "valueInt": search_request.founding_year_max
            })
        
        # Heritage score minimum
        if search_request.heritage_score_min:
            filters.append({
                "path": ["heritage_score"],
                "operator": "GreaterThanEqual",
                "valueInt": search_request.heritage_score_min
            })
        
        # Status filter
        if search_request.current_status:
            filters.append({
                "path": ["current_status"],
                "operator": "Equal",
                "valueText": search_request.current_status.value
            })
        
        if not filters:
            return None
        
        if len(filters) == 1:
            return filters[0]
        
        return {
            "operator": "And",
            "operands": filters
        }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get live Weaviate service status"""
        if not self.client:
            return {"mode": "disconnected", "error": "Not connected"}
        
        try:
            collection = self.client.collections.get(self.collection_name)
            
            # Get collection stats
            total_count = collection.aggregate.over_all(total_count=True).total_count
            
            # Get collection config
            config = collection.config.get()
            
            return {
                "mode": "live",
                "collection_name": self.collection_name,
                "total_objects": total_count,
                "vectorizer": str(config.vectorizer_config.vectorizer) if config.vectorizer_config else "unknown",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "features": {
                    "semantic_search": True,
                    "similarity_search": True,
                    "filtering": True,
                    "hybrid_search": True
                }
            }
            
        except Exception as e:
            return {"mode": "error", "error": str(e)}
    
    def close(self):
        """Close Weaviate connection"""
        if self.client:
            self.client.close()
            self.is_connected = False


class WeaviateServiceFactory:
    """Factory for creating appropriate Weaviate service based on environment"""
    
    @staticmethod
    def create() -> Union[WeaviateService, MockWeaviateService]:
        """Create Weaviate service with automatic mock fallback"""
        
        # Check if we should force mock mode
        if os.getenv('MOCK_MODE', '').lower() in ('true', '1', 'yes'):
            logger.info("Using MockWeaviateService (MOCK_MODE=true)")
            return MockWeaviateService()
        
        # Check for required credentials
        url = os.getenv("WEAVIATE_URL")
        api_key = os.getenv("WEAVIATE_API_KEY")
        
        if not url:
            logger.info("Using MockWeaviateService (no WEAVIATE_URL)")
            return MockWeaviateService()
        
        if not WEAVIATE_AVAILABLE:
            logger.info("Using MockWeaviateService (weaviate-client not installed)")
            return MockWeaviateService()
        
        # Try to create live service
        try:
            service = WeaviateService(url, api_key)
            # Note: We don't test connection here to keep factory fast
            # Connection testing happens when methods are called
            logger.info("Created WeaviateService (will test connection on first use)")
            return service
        except Exception as e:
            logger.warning(f"Failed to create WeaviateService, using mock: {e}")
            return MockWeaviateService()


# Global service instance
_weaviate_service = None

def get_weaviate_service() -> Union[WeaviateService, MockWeaviateService]:
    """Get global Weaviate service instance"""
    global _weaviate_service
    if _weaviate_service is None:
        _weaviate_service = WeaviateServiceFactory.create()
    return _weaviate_service


# Query Agent Stubs for Future RAG Implementation
class WeaviateQueryAgent:
    """
    Query agent stubs for future RAG implementation.
    
    Provides foundation for:
    - Multi-step reasoning over business data
    - Context-aware question answering
    - Business recommendation systems
    - Historical trend analysis
    """
    
    def __init__(self, weaviate_service: Union[WeaviateService, MockWeaviateService]):
        self.service = weaviate_service
    
    async def answer_question(self, question: str, context_limit: int = 5) -> Dict[str, Any]:
        """
        Answer questions about legacy businesses using RAG.
        
        Future implementation will:
        1. Analyze question to determine search strategy
        2. Retrieve relevant business context
        3. Generate answer using LLM with context
        4. Provide source attribution
        """
        # Stub implementation - search for relevant businesses
        search_request = LegacyBusinessSearch(
            query=question,
            limit=context_limit,
            similarity_threshold=0.6
        )
        
        search_response = await self.service.search_businesses(search_request)
        
        return {
            "question": question,
            "answer": f"Found {len(search_response.results)} relevant businesses for your question. This is a stub implementation - full RAG coming soon!",
            "sources": [r.business.business_name for r in search_response.results],
            "confidence": search_response.average_confidence,
            "implementation_status": "stub"
        }
    
    async def recommend_businesses(self, criteria: Dict[str, Any], limit: int = 3) -> List[Dict[str, Any]]:
        """
        Recommend businesses based on user criteria.
        
        Future implementation will use:
        - User preference modeling
        - Collaborative filtering
        - Content-based recommendations
        - Business similarity clustering
        """
        # Stub implementation
        return [
            {
                "business": "The Wok Shop",
                "reason": "Matches your interest in authentic cultural experiences",
                "confidence": 0.85,
                "implementation_status": "stub"
            },
            {
                "business": "City Lights Bookstore", 
                "reason": "Historic literary significance aligns with cultural interests",
                "confidence": 0.82,
                "implementation_status": "stub"
            },
            {
                "business": "Swan Oyster Depot",
                "reason": "Century-old family traditions match heritage preferences",
                "confidence": 0.79,
                "implementation_status": "stub"
            }
        ]
    
    async def analyze_trends(self, timeframe: str = "decade") -> Dict[str, Any]:
        """
        Analyze historical trends in legacy business data.
        
        Future implementation will provide:
        - Business founding trends by decade
        - Neighborhood development patterns
        - Industry evolution analysis
        - Cultural impact assessment
        """
        return {
            "timeframe": timeframe,
            "analysis": "Historical trend analysis coming soon! Will include founding patterns, neighborhood evolution, and cultural impact trends.",
            "implementation_status": "stub"
        }