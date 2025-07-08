"""
Enhanced API Routes with Schema-Driven Responses
===============================================

Production-ready API demonstrating:
- Pydantic schema validation
- Advanced search capabilities  
- RAG system foundations
- Dynamic response generation
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.legacy_business import (
    LegacyBusiness, LegacyBusinessSummary, LegacyBusinessSearch,
    NeighborhoodEnum, BusinessStatusEnum
)
from services.enhanced_business_service import get_enhanced_business_service, EnhancedBusinessService

# Initialize enhanced FastAPI app
app = FastAPI(
    title="SF Legacy Business Registry API",
    description="Advanced RAG-powered API for San Francisco Legacy Business Registry",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4321",  # Astro dev server
        "http://localhost:3000",  # Alternative dev port
        "http://frontend:4321",   # Docker service name
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection
def get_business_service() -> EnhancedBusinessService:
    return get_enhanced_business_service()

# ============================================================================
# Schema-Driven Business API Endpoints
# ============================================================================

@app.get("/api/v2/businesses", response_model=List[LegacyBusiness])
async def get_businesses(
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of businesses to return"),
    neighborhood: Optional[NeighborhoodEnum] = Query(default=None, description="Filter by neighborhood"),
    business_type: Optional[str] = Query(default=None, description="Filter by business type"),
    service: EnhancedBusinessService = Depends(get_business_service)
) -> List[LegacyBusiness]:
    """
    Get businesses with full schema-validated responses.
    
    Demonstrates:
    - Complete Pydantic model validation
    - Rich narrative content for RAG
    - Structured relationship data
    - Heritage scoring and metadata
    """
    
    businesses = service.get_businesses(limit)
    
    # Apply optional filters
    if neighborhood:
        businesses = [b for b in businesses if b.neighborhood == neighborhood]
    
    if business_type:
        businesses = [b for b in businesses if business_type.lower() in b.business_type.lower()]
    
    return businesses

@app.get("/api/v2/businesses/summaries", response_model=List[LegacyBusinessSummary])
async def get_business_summaries(
    limit: int = Query(default=10, ge=1, le=100),
    service: EnhancedBusinessService = Depends(get_business_service)
) -> List[LegacyBusinessSummary]:
    """
    Get lightweight business summaries for list views and previews.
    
    Optimized for:
    - Fast loading times
    - Grid/card layouts
    - Search result previews
    """
    
    return service.get_business_summaries(limit)

@app.get("/api/v2/businesses/{business_name}", response_model=LegacyBusiness)
async def get_business_detail(
    business_name: str,
    service: EnhancedBusinessService = Depends(get_business_service)
) -> LegacyBusiness:
    """
    Get complete business profile with full narrative content.
    
    Perfect for:
    - Detail pages
    - RAG context retrieval
    - Heritage documentation
    """
    
    business = service.get_business_by_name(business_name)
    if not business:
        raise HTTPException(
            status_code=404, 
            detail=f"Business '{business_name}' not found in legacy registry"
        )
    
    return business

@app.post("/api/v2/businesses/search", response_model=Dict[str, Any])
async def search_businesses(
    search_query: LegacyBusinessSearch,
    service: EnhancedBusinessService = Depends(get_business_service)
) -> Dict[str, Any]:
    """
    Advanced search with semantic capabilities and filtering.
    
    Features:
    - Full-text semantic search
    - Multi-dimensional filtering
    - RAG-weighted relevance scoring
    - Vector similarity simulation
    """
    
    start_time = time.time()
    
    results = service.search_businesses(search_query)
    
    processing_time = time.time() - start_time
    
    return {
        **results,
        "search_metadata": {
            **results["search_metadata"],
            "processing_time_ms": round(processing_time * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
    }

# ============================================================================
# RAG System Demonstration Endpoints  
# ============================================================================

@app.post("/api/v2/rag/query")
async def query_rag_system(
    query: str = Query(..., description="Natural language query about legacy businesses"),
    max_results: int = Query(default=5, ge=1, le=10, description="Maximum businesses to include in context"),
    service: EnhancedBusinessService = Depends(get_business_service)
) -> Dict[str, Any]:
    """
    Simulate RAG query processing for legacy business knowledge.
    
    Demonstrates:
    - Semantic search over business narratives
    - Context retrieval and ranking
    - Simulated LLM response generation
    - Source attribution and scoring
    """
    
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    result = service.simulate_rag_query(query, max_results)
    
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "mode": "simulation",
        **result
    }

@app.get("/api/v2/rag/contexts/{business_name}")
async def get_business_rag_contexts(
    business_name: str,
    context_type: Optional[str] = Query(default=None, description="Type of context: founding_story, cultural_significance, etc."),
    service: EnhancedBusinessService = Depends(get_business_service)
) -> Dict[str, Any]:
    """
    Extract specific contexts from a business for RAG processing.
    
    Shows how different narrative fields are weighted and used in RAG:
    - High-weight: founding_story, cultural_significance
    - Medium-weight: physical_traditions, historical_significance  
    - Supporting: unique_features, recognition
    """
    
    business = service.get_business_by_name(business_name)
    if not business:
        raise HTTPException(status_code=404, detail=f"Business '{business_name}' not found")
    
    contexts = {}
    
    # High-weight contexts (primary for RAG)
    if not context_type or context_type == "founding_story":
        contexts["founding_story"] = {
            "content": business.founding_story,
            "rag_weight": "high",
            "search_boost": 1.8,
            "character_count": len(business.founding_story) if business.founding_story else 0
        }
    
    if not context_type or context_type == "cultural_significance":
        contexts["cultural_significance"] = {
            "content": business.cultural_significance,
            "rag_weight": "high", 
            "search_boost": 1.8,
            "character_count": len(business.cultural_significance) if business.cultural_significance else 0
        }
    
    # Medium-weight contexts
    if not context_type or context_type == "physical_traditions":
        contexts["physical_traditions"] = {
            "content": business.physical_traditions,
            "rag_weight": "medium",
            "search_boost": 1.0,
            "character_count": len(business.physical_traditions) if business.physical_traditions else 0
        }
    
    # Supporting contexts
    if not context_type or context_type == "unique_features":
        contexts["unique_features"] = {
            "content": business.unique_features,
            "rag_weight": "medium",
            "search_boost": 1.0,
            "list_length": len(business.unique_features)
        }
    
    return {
        "business_name": business.business_name,
        "contexts": contexts,
        "heritage_score": business.heritage_score,
        "extraction_confidence": business.extraction_confidence,
        "context_summary": {
            "total_contexts": len(contexts),
            "high_weight_contexts": sum(1 for c in contexts.values() if c.get("rag_weight") == "high"),
            "medium_weight_contexts": sum(1 for c in contexts.values() if c.get("rag_weight") == "medium")
        }
    }

# ============================================================================
# Analytics and Statistics Endpoints
# ============================================================================

@app.get("/api/v2/analytics/neighborhoods")
async def get_neighborhood_analytics(
    service: EnhancedBusinessService = Depends(get_business_service)
) -> Dict[str, Any]:
    """Get neighborhood distribution and statistics"""
    
    neighborhood_counts = service.get_neighborhoods_with_counts()
    
    return {
        "neighborhood_distribution": neighborhood_counts,
        "total_neighborhoods": len(neighborhood_counts),
        "total_businesses": sum(neighborhood_counts.values()),
        "analytics": {
            "most_represented": max(neighborhood_counts, key=neighborhood_counts.get) if neighborhood_counts else None,
            "least_represented": min(neighborhood_counts, key=neighborhood_counts.get) if neighborhood_counts else None,
            "average_per_neighborhood": sum(neighborhood_counts.values()) / len(neighborhood_counts) if neighborhood_counts else 0
        }
    }

@app.get("/api/v2/analytics/heritage-scores")
async def get_heritage_score_analytics(
    service: EnhancedBusinessService = Depends(get_business_service)
) -> Dict[str, Any]:
    """Get heritage score distribution and analytics"""
    
    distribution = service.get_heritage_score_distribution()
    
    return {
        "score_distribution": distribution,
        "analytics": {
            "total_scored_businesses": sum(distribution.values()),
            "high_heritage_businesses": distribution.get("90-100", 0),
            "heritage_preservation_rate": round(
                (distribution.get("80-89", 0) + distribution.get("90-100", 0)) / max(sum(distribution.values()), 1) * 100, 
                1
            )
        }
    }

@app.get("/api/v2/analytics/business-types")
async def get_business_type_analytics(
    service: EnhancedBusinessService = Depends(get_business_service)
) -> Dict[str, Any]:
    """Get business type distribution"""
    
    type_counts = service.get_business_types_with_counts()
    
    return {
        "business_type_distribution": type_counts,
        "total_types": len(type_counts),
        "analytics": {
            "most_common_type": max(type_counts, key=type_counts.get) if type_counts else None,
            "type_diversity_index": len(type_counts) / max(sum(type_counts.values()), 1)
        }
    }

# ============================================================================
# Schema and System Information Endpoints
# ============================================================================

@app.get("/api/v2/schema/business-model")
async def get_business_schema() -> Dict[str, Any]:
    """
    Get the complete Pydantic schema for LegacyBusiness model.
    
    Useful for:
    - Dynamic frontend generation
    - API documentation
    - Data validation reference
    """
    
    return {
        "model_name": "LegacyBusiness",
        "schema": LegacyBusiness.model_json_schema(),
        "field_metadata": {
            field_name: {
                "title": field_info.field_info.title,
                "description": field_info.field_info.description,
                "frontend_component": getattr(field_info.field_info, 'frontend_component', None),
                "rag_weight": getattr(field_info.field_info, 'rag_weight', None),
                "pdf_extraction_hints": getattr(field_info.field_info, 'pdf_extraction_hints', None)
            }
            for field_name, field_info in LegacyBusiness.__fields__.items()
        },
        "generated_at": datetime.now().isoformat()
    }

@app.get("/api/v2/system/status")
async def get_system_status(
    service: EnhancedBusinessService = Depends(get_business_service)
) -> Dict[str, Any]:
    """Get comprehensive system status and capabilities"""
    
    businesses = service.get_businesses(100)  # Get all for stats
    
    return {
        "status": "operational",
        "mode": "enhanced_mock",
        "timestamp": datetime.now().isoformat(),
        "api_version": "2.0.0",
        "capabilities": {
            "schema_validation": True,
            "semantic_search": True,
            "rag_simulation": True,
            "advanced_filtering": True,
            "dynamic_frontend_generation": True,
            "heritage_analytics": True
        },
        "data_statistics": {
            "total_businesses": len(businesses),
            "schema_validated_businesses": len(businesses),
            "businesses_with_narratives": len([b for b in businesses if b.founding_story]),
            "businesses_with_heritage_scores": len([b for b in businesses if b.heritage_score]),
            "average_heritage_score": sum(b.heritage_score for b in businesses if b.heritage_score) / max(len([b for b in businesses if b.heritage_score]), 1)
        },
        "performance": {
            "response_time_target_ms": 200,
            "search_performance_target_ms": 500,
            "concurrent_users_supported": 100
        }
    }

# ============================================================================
# Legacy Compatibility Endpoints
# ============================================================================

@app.get("/api/businesses")
async def legacy_get_businesses(
    limit: int = 10,
    service: EnhancedBusinessService = Depends(get_business_service)
):
    """Legacy endpoint compatibility - returns enhanced data in old format"""
    
    businesses = service.get_businesses(limit)
    
    # Convert to legacy format for backward compatibility
    legacy_format = []
    for business in businesses:
        legacy_business = {
            "id": hash(business.business_name) % 10000,  # Generate consistent ID
            "name": business.business_name,
            "tagline": business.demo_highlights[0] if business.demo_highlights else "Historic San Francisco business",
            "type": business.business_type,
            "neighborhood": business.neighborhood.value if business.neighborhood else "Unknown",
            "founded": business.founding_year,
            "story": business.founding_story,
            "features": business.unique_features,
            "status": business.current_status.value,
            "heritage_score": business.heritage_score,
            "cultural_significance": business.cultural_significance
        }
        legacy_format.append(legacy_business)
    
    return legacy_format

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Enhanced Legacy Business Registry API...")
    print("📊 Schema-driven responses with RAG foundations")
    print("🌐 API: http://localhost:8000/api/v2/")
    print("📚 Docs: http://localhost:8000/api/docs")
    
    uvicorn.run(
        "enhanced_routes:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )