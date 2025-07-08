"""
Weaviate API Routes for Legacy Business Registry
===============================================

Provides RESTful endpoints for Weaviate operations:
- Business listing and search
- Semantic search with filtering
- Service status and health
- Migration utilities
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from models.legacy_business import LegacyBusinessSummary, LegacyBusinessSearch
from services.weaviate_service import get_weaviate_service, WeaviateService, MockWeaviateService, WeaviateQueryAgent, SearchMode

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/weaviate", tags=["weaviate"])


@router.get("/health", response_model=Dict[str, Any])
async def get_weaviate_health():
    """Get Weaviate service health and status"""
    try:
        service = get_weaviate_service()
        
        # For live service, test connection
        if isinstance(service, WeaviateService):
            if not service.is_connected:
                connected = await service.connect()
                if not connected:
                    return JSONResponse(
                        status_code=503,
                        content={
                            "status": "unhealthy",
                            "mode": "live",
                            "error": "Cannot connect to Weaviate",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
        
        status = await service.get_service_status()
        status["status"] = "healthy"
        status["timestamp"] = datetime.utcnow().isoformat()
        
        return status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/businesses", response_model=List[LegacyBusinessSummary])
async def list_all_businesses(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of businesses to return")
):
    """List all businesses from Weaviate with pagination"""
    try:
        service = get_weaviate_service()
        
        # For live service, ensure connection
        if isinstance(service, WeaviateService):
            if not service.is_connected:
                connected = await service.connect()
                if not connected:
                    raise HTTPException(
                        status_code=503,
                        detail="Cannot connect to Weaviate service"
                    )
        
        businesses = await service.list_all_businesses(limit=limit)
        return businesses
        
    except Exception as e:
        logger.error(f"Failed to list businesses: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve businesses: {str(e)}"
        )


@router.post("/search", response_model=Dict[str, Any])
async def search_businesses(search_request: LegacyBusinessSearch):
    """
    Perform semantic search across legacy business data.
    
    Supports:
    - Full-text semantic search
    - Neighborhood filtering
    - Business type filtering
    - Founding year range filtering
    - Heritage score filtering
    - Configurable similarity thresholds
    """
    try:
        service = get_weaviate_service()
        
        # For live service, ensure connection
        if isinstance(service, WeaviateService):
            if not service.is_connected:
                connected = await service.connect()
                if not connected:
                    raise HTTPException(
                        status_code=503,
                        detail="Cannot connect to Weaviate service"
                    )
        
        search_response = await service.search_businesses(search_request)
        
        return {
            "results": [
                {
                    "business": result.business.dict(),
                    "score": result.score,
                    "certainty": result.certainty,
                    "distance": result.distance,
                    "confidence": result.confidence,
                    "search_mode": result.search_mode
                }
                for result in search_response.results
            ],
            "query": search_response.query,
            "total_count": search_response.total_count,
            "execution_time_ms": search_response.execution_time_ms,
            "average_confidence": search_response.average_confidence,
            "search_mode": search_response.search_mode.value,
            "used_fallback": search_response.used_fallback,
            "has_results": search_response.has_results
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/businesses/{business_name}", response_model=Optional[LegacyBusinessSummary])
async def get_business_by_name(business_name: str):
    """Get a specific business by name"""
    try:
        service = get_weaviate_service()
        
        # For live service, ensure connection
        if isinstance(service, WeaviateService):
            if not service.is_connected:
                connected = await service.connect()
                if not connected:
                    raise HTTPException(
                        status_code=503,
                        detail="Cannot connect to Weaviate service"
                    )
        
        business = await service.get_business_by_name(business_name)
        
        if not business:
            raise HTTPException(
                status_code=404,
                detail=f"Business '{business_name}' not found"
            )
        
        return business
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get business: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve business: {str(e)}"
        )


@router.get("/businesses/{business_name}/similar", response_model=List[Dict[str, Any]])
async def get_similar_businesses(
    business_name: str,
    limit: int = Query(5, ge=1, le=20, description="Maximum number of similar businesses to return")
):
    """Find businesses similar to the specified business"""
    try:
        service = get_weaviate_service()
        
        # For live service, ensure connection
        if isinstance(service, WeaviateService):
            if not service.is_connected:
                connected = await service.connect()
                if not connected:
                    raise HTTPException(
                        status_code=503,
                        detail="Cannot connect to Weaviate service"
                    )
        
        similar_results = await service.get_similar_businesses(business_name, limit)
        
        return [
            {
                "business": result.business.dict(),
                "similarity_score": result.score,
                "certainty": result.certainty,
                "distance": result.distance,
                "confidence": result.confidence
            }
            for result in similar_results
        ]
        
    except Exception as e:
        logger.error(f"Similarity search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Similarity search failed: {str(e)}"
        )


@router.get("/search/quick", response_model=Dict[str, Any])
async def quick_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results to return"),
    neighborhood: Optional[str] = Query(None, description="Filter by neighborhood"),
    business_type: Optional[str] = Query(None, description="Filter by business type"),
    min_heritage_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum heritage score")
):
    """
    Quick search endpoint with URL parameters.
    Convenient for simple searches without POST body.
    """
    try:
        # Build search request from query parameters
        search_request = LegacyBusinessSearch(
            query=q,
            limit=limit,
            neighborhood=neighborhood,
            business_type=business_type,
            heritage_score_min=min_heritage_score
        )
        
        service = get_weaviate_service()
        
        # For live service, ensure connection
        if isinstance(service, WeaviateService):
            if not service.is_connected:
                connected = await service.connect()
                if not connected:
                    raise HTTPException(
                        status_code=503,
                        detail="Cannot connect to Weaviate service"
                    )
        
        search_response = await service.search_businesses(search_request)
        
        return {
            "results": [
                {
                    "business_name": result.business.business_name,
                    "business_type": result.business.business_type,
                    "neighborhood": result.business.neighborhood,
                    "founding_year": result.business.founding_year,
                    "heritage_score": result.business.heritage_score,
                    "confidence": result.confidence
                }
                for result in search_response.results
            ],
            "query": search_response.query,
            "total_count": search_response.total_count,
            "execution_time_ms": search_response.execution_time_ms,
            "used_fallback": search_response.used_fallback
        }
        
    except Exception as e:
        logger.error(f"Quick search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Quick search failed: {str(e)}"
        )


@router.get("/collections/info", response_model=Dict[str, Any])
async def get_collection_info():
    """Get information about the Weaviate collection"""
    try:
        service = get_weaviate_service()
        
        # For live service, ensure connection
        if isinstance(service, WeaviateService):
            if not service.is_connected:
                connected = await service.connect()
                if not connected:
                    raise HTTPException(
                        status_code=503,
                        detail="Cannot connect to Weaviate service"
                    )
        
        status = await service.get_service_status()
        
        return {
            "collection_name": status.get("collection_name", "LegacyBusiness"),
            "total_objects": status.get("total_objects", 0),
            "vectorizer": status.get("vectorizer", "unknown"),
            "mode": status.get("mode", "unknown"),
            "features": status.get("features", {}),
            "last_updated": status.get("last_updated"),
            "schema_version": "1.0",
            "supported_search_modes": [mode.value for mode in SearchMode]
        }
        
    except Exception as e:
        logger.error(f"Failed to get collection info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve collection info: {str(e)}"
        )


# RAG Query Agent Endpoints (Stubs for future implementation)
@router.post("/agent/question", response_model=Dict[str, Any])
async def ask_question(request: Dict[str, Any]):
    """
    Ask a question about legacy businesses using RAG.
    
    Future implementation will provide:
    - Context-aware question answering
    - Source attribution
    - Multi-step reasoning
    - Follow-up question suggestions
    """
    try:
        question = request.get("question")
        if not question:
            raise HTTPException(
                status_code=400,
                detail="Question is required"
            )
        
        service = get_weaviate_service()
        
        # For live service, ensure connection
        if isinstance(service, WeaviateService):
            if not service.is_connected:
                connected = await service.connect()
                if not connected:
                    raise HTTPException(
                        status_code=503,
                        detail="Cannot connect to Weaviate service"
                    )
        
        agent = WeaviateQueryAgent(service)
        response = await agent.answer_question(
            question=question,
            context_limit=request.get("context_limit", 5)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Question answering failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Question answering failed: {str(e)}"
        )


@router.post("/agent/recommend", response_model=List[Dict[str, Any]])
async def recommend_businesses(request: Dict[str, Any]):
    """
    Get business recommendations based on user criteria.
    
    Future implementation will provide:
    - Personalized recommendations
    - Collaborative filtering
    - Content-based matching
    - Explanation of recommendations
    """
    try:
        criteria = request.get("criteria", {})
        limit = request.get("limit", 3)
        
        service = get_weaviate_service()
        
        # For live service, ensure connection
        if isinstance(service, WeaviateService):
            if not service.is_connected:
                connected = await service.connect()
                if not connected:
                    raise HTTPException(
                        status_code=503,
                        detail="Cannot connect to Weaviate service"
                    )
        
        agent = WeaviateQueryAgent(service)
        recommendations = await agent.recommend_businesses(
            criteria=criteria,
            limit=limit
        )
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Recommendation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation failed: {str(e)}"
        )


@router.get("/agent/trends", response_model=Dict[str, Any])
async def analyze_trends(
    timeframe: str = Query("decade", description="Analysis timeframe (decade, year, century)")
):
    """
    Analyze historical trends in legacy business data.
    
    Future implementation will provide:
    - Founding trends by decade
    - Neighborhood development patterns
    - Industry evolution analysis
    - Cultural impact assessment
    """
    try:
        service = get_weaviate_service()
        
        # For live service, ensure connection
        if isinstance(service, WeaviateService):
            if not service.is_connected:
                connected = await service.connect()
                if not connected:
                    raise HTTPException(
                        status_code=503,
                        detail="Cannot connect to Weaviate service"
                    )
        
        agent = WeaviateQueryAgent(service)
        analysis = await agent.analyze_trends(timeframe=timeframe)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Trend analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Trend analysis failed: {str(e)}"
        )


# Migration and Management Endpoints
@router.post("/migrate/check", response_model=Dict[str, Any])
async def check_migration_status():
    """
    Check if Weaviate schema migration is needed.
    
    Returns information about:
    - Current schema version
    - Required migrations
    - Collection readiness
    """
    try:
        service = get_weaviate_service()
        
        if isinstance(service, MockWeaviateService):
            return {
                "migration_needed": False,
                "current_version": "mock",
                "target_version": "mock",
                "status": "mock_mode",
                "message": "Running in mock mode - no migration needed"
            }
        
        # For live service, check connection and schema
        if not service.is_connected:
            connected = await service.connect()
            if not connected:
                return {
                    "migration_needed": True,
                    "status": "connection_failed",
                    "message": "Cannot connect to Weaviate - check configuration"
                }
        
        status = await service.get_service_status()
        
        return {
            "migration_needed": False,  # Assume schema exists for now
            "current_version": "1.0",
            "target_version": "1.0", 
            "status": "ready",
            "collection_info": {
                "name": status.get("collection_name"),
                "total_objects": status.get("total_objects", 0),
                "vectorizer": status.get("vectorizer")
            },
            "message": "Schema is up to date"
        }
        
    except Exception as e:
        logger.error(f"Migration check failed: {e}")
        return {
            "migration_needed": True,
            "status": "error",
            "error": str(e),
            "message": "Migration check failed - manual intervention may be required"
        }


@router.get("/demo/sample-data", response_model=Dict[str, Any])
async def get_sample_data():
    """
    Get sample data for demo purposes.
    Shows the structure of data that would be in Weaviate.
    """
    try:
        service = get_weaviate_service()
        
        # Get a few sample businesses
        businesses = await service.list_all_businesses(limit=3)
        
        return {
            "sample_businesses": [business.dict() for business in businesses],
            "data_structure": {
                "description": "Each business contains rich narrative content optimized for semantic search",
                "key_fields": [
                    "business_name",
                    "founding_story", 
                    "cultural_significance",
                    "unique_features",
                    "demo_highlights"
                ],
                "search_optimized": [
                    "founding_story",
                    "cultural_significance", 
                    "community_impact",
                    "historical_significance"
                ]
            },
            "search_examples": [
                {
                    "query": "traditional Chinese cooking",
                    "expected_matches": ["The Wok Shop"],
                    "reason": "Matches founding story and cultural significance"
                },
                {
                    "query": "family business heritage",
                    "expected_matches": ["Swan Oyster Depot"],
                    "reason": "Multi-generational family ownership"
                },
                {
                    "query": "literary culture bookstore",
                    "expected_matches": ["City Lights Bookstore", "Green Apple Books"],
                    "reason": "Literary significance and community role"
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Sample data retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve sample data: {str(e)}"
        )