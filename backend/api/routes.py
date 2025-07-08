"""
FastAPI Routes - Clean API Layer
Modern FastAPI with proper CORS for Astro frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import time

from .services import VendorService, BusinessService, get_config
from .debug import debug_service
from .llamaindex_service import get_llamaindex_service

# Initialize FastAPI app
app = FastAPI(
    title="Hack Stack API",
    description="Modern hackathon backend with progressive enhancement",
    version="1.0.0"
)

# CORS for Astro frontend
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

# Initialize services
config = get_config()
vendor_service = VendorService()
business_service = BusinessService()
llamaindex_service = get_llamaindex_service()

# Request models
class VendorRequest(BaseModel):
    operation: str
    data: Dict[str, Any] = {}

class DocumentProcessRequest(BaseModel):
    document_url: str
    extract_images: bool = True
    
class MultiModalQueryRequest(BaseModel):
    query: str
    document_id: str = None

# =============================================================================
# API Routes
# =============================================================================

@app.get("/api/health")
async def health_check():
    """System health and configuration status"""
    return {
        "status": "healthy",
        "mode": config.mode,
        "available_vendors": vendor_service.available_vendors,
        "demo_ready": True,
        "startup_time": config.startup_time
    }

@app.get("/api/businesses")
async def get_businesses(limit: int = 10):
    """Get businesses (mock or real data)"""
    return business_service.get_businesses(limit)

@app.get("/api/businesses/{business_id}")
async def get_business(business_id: int):
    """Get single business by ID"""
    business = business_service.get_business_by_id(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@app.post("/api/vendor/{vendor_name}")
async def process_vendor_request(vendor_name: str, request: VendorRequest):
    """Process request through specific AI vendor"""
    try:
        result = await vendor_service.process(
            vendor_name, 
            request.operation, 
            request.data
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def search_businesses(q: str = "innovation", limit: int = 10):
    """Search businesses with enhanced relevance scoring"""
    results = business_service.search(q, limit)
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }

@app.get("/api/neighborhoods")
async def get_neighborhoods():
    """Get list of all neighborhoods"""
    return {
        "neighborhoods": business_service.get_neighborhoods()
    }

@app.get("/api/neighborhoods/{neighborhood}/businesses")
async def get_businesses_by_neighborhood(neighborhood: str, limit: int = 10):
    """Get businesses filtered by neighborhood"""
    results = business_service.get_businesses_by_neighborhood(neighborhood, limit)
    return {
        "neighborhood": neighborhood,
        "businesses": results,
        "total": len(results)
    }

@app.get("/api/business-types")
async def get_business_types():
    """Get list of all business types/categories"""
    return {
        "business_types": business_service.get_business_types()
    }

@app.get("/api/business-types/{business_type}/businesses")
async def get_businesses_by_type(business_type: str, limit: int = 10):
    """Get businesses filtered by type/category"""
    results = business_service.get_businesses_by_type(business_type, limit)
    return {
        "business_type": business_type,
        "businesses": results,
        "total": len(results)
    }

@app.get("/api/applications")
async def get_legacy_applications(limit: int = 10):
    """Get legacy business applications with heritage documentation"""
    businesses = business_service.get_businesses(limit)
    
    # Transform to highlight application-specific fields
    applications = []
    for business in businesses:
        app = {
            "application_number": business.get("application_number"),
            "name": business.get("name"),
            "neighborhood": business.get("neighborhood"),
            "type": business.get("type"),
            "established": business.get("established"),
            "heritage_score": business.get("heritage_score"),
            "community_impact": business.get("community_impact"),
            "cultural_significance": business.get("cultural_significance"),
            "historical_significance": business.get("historical_significance"),
            "proof_of_establishment": business.get("proof_of_establishment"),
            "supporting_evidence": business.get("supporting_evidence"),
            "approval_status": business.get("status", "APPROVED"),
            "compliance_status": business.get("compliance_status")
        }
        applications.append(app)
    
    return {
        "total_applications": len(applications),
        "data_source": "SF Legacy Business Registry",
        "applications": applications
    }

@app.get("/api/applications/{application_id}")
async def get_application_details(application_id: int):
    """Get complete legacy business application details"""
    business = business_service.get_business_by_id(application_id)
    if not business:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {
        "application": business,
        "metadata": business.get("_application_metadata", {}),
        "heritage_documentation": {
            "years_operating": 2024 - int(business.get("established", "2000")),
            "heritage_score": business.get("heritage_score"),
            "community_impact_score": business.get("community_impact_score"),
            "historical_significance_score": business.get("historical_significance_score")
        }
    }

@app.get("/api/heritage-scores")
async def get_heritage_scoring():
    """Get heritage scoring breakdown for all applications"""
    businesses = business_service.get_businesses(100)
    
    scores = []
    for business in businesses:
        if business.get("heritage_score"):
            scores.append({
                "name": business.get("name"),
                "neighborhood": business.get("neighborhood"),
                "established": business.get("established"),
                "heritage_score": business.get("heritage_score"),
                "community_impact_score": business.get("community_impact_score"),
                "years_operating": 2024 - int(business.get("established", "2000"))
            })
    
    # Sort by heritage score
    scores.sort(key=lambda x: x["heritage_score"], reverse=True)
    
    return {
        "scoring_criteria": {
            "heritage_score": "Years of operation + historical significance bonuses",
            "community_impact_score": "Based on community benefit statements and testimonials",
            "historical_significance_score": "Cultural landmarks, survived major events, etc."
        },
        "score_breakdown": scores
    }

# =============================================================================
# RAG System Simulation Endpoints
# =============================================================================

class RAGQueryRequest(BaseModel):
    query: str
    max_results: int = 5

@app.post("/api/v2/rag/query")
async def simulate_rag_query(request: RAGQueryRequest):
    """
    Simulate RAG query processing for legacy business knowledge.
    
    Demonstrates semantic search over business narratives and context retrieval.
    """
    
    query = request.query.lower()
    businesses = business_service.get_businesses(50)
    
    # Simple relevance scoring based on query terms
    relevant_businesses = []
    
    for business in businesses:
        score = 0
        context_parts = []
        
        # Search across rich narrative fields
        searchable_fields = {
            "name": business.get("name", ""),
            "founding_story": business.get("founding_story", ""),
            "cultural_impact": business.get("cultural_impact", ""),
            "unique_features": business.get("unique_features", ""),
            "story": business.get("story", ""),  # fallback for older data
            "cultural_significance": business.get("cultural_significance", ""),
            "historical_significance": business.get("historical_significance", ""),
            "features": " ".join(business.get("features", [])),
            "notable_features": " ".join(business.get("notable_features", [])),
            "keywords": " ".join(business.get("keywords", [])),
            "neighborhood": business.get("neighborhood", ""),
            "type": business.get("type", "")
        }
        
        # Calculate relevance score with enhanced weighting
        for field, content in searchable_fields.items():
            if query in content.lower():
                if field in ["name"]:
                    score += 10
                elif field in ["founding_story", "cultural_impact", "unique_features"]:
                    score += 8  # High-value narrative content
                elif field in ["cultural_significance", "historical_significance"]:
                    score += 6
                elif field in ["keywords", "notable_features"]:
                    score += 5  # Structured searchable content
                elif field in ["features", "type"]:
                    score += 4
                elif field in ["story"]:  # fallback field
                    score += 3
                else:
                    score += 2
        
        if score > 0:
            # Build context from rich narrative fields
            if business.get("founding_story"):
                context_parts.append(f"Origin: {business.get('founding_story')[:200]}...")
            elif business.get("story"):  # fallback
                context_parts.append(f"Origin: {business.get('story')[:150]}...")
            
            if business.get("cultural_impact"):
                context_parts.append(f"Cultural Impact: {business.get('cultural_impact')[:200]}...")
            elif business.get("cultural_significance"):  # fallback
                context_parts.append(f"Cultural Impact: {business.get('cultural_significance')[:150]}...")
            
            if business.get("unique_features"):
                context_parts.append(f"Unique Features: {business.get('unique_features')[:200]}...")
            elif business.get("features"):  # fallback
                context_parts.append(f"Notable Features: {', '.join(business.get('features', [])[:3])}")
            
            if business.get("keywords"):
                context_parts.append(f"Keywords: {', '.join(business.get('keywords', [])[:5])}")
            
            relevant_businesses.append({
                "business_name": business.get("name"),
                "context": " | ".join(context_parts),
                "heritage_score": business.get("heritage_score"),
                "relevance_score": score / 20.0,  # Normalize to 0-1
                "neighborhood": business.get("neighborhood"),
                "established": business.get("established")
            })
    
    # Sort by relevance
    relevant_businesses.sort(key=lambda x: x["relevance_score"], reverse=True)
    top_businesses = relevant_businesses[:request.max_results]
    
    # Generate simulated response
    if not top_businesses:
        response = f"I couldn't find specific information about '{request.query}' in the legacy business database."
    elif "traditional" in query or "authentic" in query:
        business_names = [b["business_name"] for b in top_businesses[:3]]
        response = f"Based on the legacy business registry, several businesses exemplify traditional practices: {', '.join(business_names)}. These establishments have maintained authentic cultural traditions for decades."
    elif "food" in query or "restaurant" in query:
        food_businesses = [b for b in top_businesses if "food" in b["context"].lower() or "restaurant" in b["context"].lower()]
        if food_businesses:
            response = f"The legacy food establishments include {', '.join([fb['business_name'] for fb in food_businesses[:3]])}. These businesses represent generations of culinary tradition and community gathering spaces."
        else:
            response = f"Found {len(top_businesses)} businesses related to your query about food and dining traditions."
    elif "history" in query or "historic" in query:
        business_names = [b["business_name"] for b in top_businesses[:3]]
        response = f"Several historic businesses match your query: {', '.join(business_names)}. These establishments have witnessed San Francisco's transformation while maintaining their original character."
    else:
        business_names = [b["business_name"] for b in top_businesses[:3]]
        response = f"I found {len(top_businesses)} relevant legacy businesses: {', '.join(business_names)}. Each has unique cultural significance and contributes to San Francisco's diverse heritage landscape."
    
    return {
        "success": True,
        "query": request.query,
        "response": response,
        "source_contexts": top_businesses,
        "total_businesses_searched": len(businesses),
        "relevant_businesses_found": len(relevant_businesses),
        "search_metadata": {
            "similarity_threshold": 0.1,
            "semantic_search_enabled": True,
            "processing_time_ms": 50
        }
    }

@app.get("/api/metrics")
async def get_metrics():
    """Enhanced metrics with legacy business stats"""
    stats = business_service.get_stats()
    return {
        **stats,
        "active_vendors": len(vendor_service.available_vendors),
        "mode": config.mode,
        "uptime": "Development session"
    }

@app.get("/api/debug")
async def get_debug_status():
    """Comprehensive debug and health check information"""
    return await debug_service.run_all_health_checks()

@app.get("/api/debug/test/{vendor_name}")
async def test_vendor_endpoint(vendor_name: str):
    """Test a specific vendor endpoint for debugging"""
    test_request = VendorRequest(
        operation="analyze",
        data={"content": "Debug test - checking vendor connectivity"}
    )
    
    try:
        result = await vendor_service.process(
            vendor_name,
            test_request.operation,
            test_request.data
        )
        return {
            "vendor": vendor_name,
            "status": "success",
            "result": result,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "vendor": vendor_name,
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

# =============================================================================
# LlamaIndex Multi-Modal API Routes
# =============================================================================

@app.get("/api/llamaindex/status")
async def get_llamaindex_status():
    """Get LlamaIndex service status and capabilities"""
    return llamaindex_service.get_service_status()

@app.post("/api/llamaindex/process")
async def process_document(request: DocumentProcessRequest):
    """
    Process document with multi-modal extraction
    
    Features:
    - PDF text extraction with LlamaParse
    - Image extraction and positioning
    - Relationship mapping between text and images
    - Quality scoring and validation
    """
    try:
        result = await llamaindex_service.process_document_url(request.document_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/llamaindex/query")
async def query_multimodal(request: MultiModalQueryRequest):
    """
    Perform multi-modal search across text and images
    
    Features:
    - Semantic search across document text
    - Image similarity search
    - Cross-modal relationship queries
    - Unified result ranking
    """
    try:
        result = await llamaindex_service.query_multimodal(
            query=request.query,
            document_id=request.document_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/llamaindex/documents")
async def list_processed_documents():
    """List all processed documents with metadata"""
    try:
        documents = list(llamaindex_service.processed_documents.values())
        return {
            "success": True,
            "documents": [doc.model_dump() for doc in documents],
            "total": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/llamaindex/documents/{document_id}")
async def get_processed_document(document_id: str):
    """Get specific processed document with full details"""
    try:
        if document_id not in llamaindex_service.processed_documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = llamaindex_service.processed_documents[document_id]
        return {
            "success": True,
            "document": document.model_dump()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/llamaindex/demo")
async def get_demo_capabilities():
    """
    Demonstrate LlamaIndex multi-modal capabilities
    
    Shows:
    - Processing pipeline visualization
    - Sample multi-modal queries
    - Feature showcases
    - Performance benchmarks
    """
    return {
        "success": True,
        "capabilities": {
            "document_processing": {
                "supported_formats": ["PDF", "Images", "Mixed content"],
                "text_extraction": "LlamaParse integration",
                "image_extraction": "PyMuPDF with position mapping",
                "relationship_mapping": "Cross-modal intelligence",
                "quality_scoring": "Comprehensive validation"
            },
            "search_features": {
                "semantic_search": "Vector-based text search",
                "image_search": "Visual similarity matching",
                "hybrid_queries": "Combined text + image results",
                "contextual_relevance": "Relationship-aware ranking"
            },
            "demo_scenarios": [
                {
                    "name": "Technical Documentation",
                    "description": "Process engineering docs with diagrams",
                    "sample_query": "Show me the architecture diagram and related specifications"
                },
                {
                    "name": "Research Papers",
                    "description": "Academic papers with figures and charts",
                    "sample_query": "Find methodology sections and corresponding result graphs"
                },
                {
                    "name": "Business Reports", 
                    "description": "Corporate documents with data visualizations",
                    "sample_query": "Locate financial charts and supporting narrative text"
                }
            ]
        },
        "sample_queries": [
            "Find all diagrams related to system architecture",
            "Show me text sections that reference Figure 1",
            "What images are mentioned in the conclusion?",
            "Search for flowcharts about the processing pipeline"
        ],
        "service_status": llamaindex_service.get_service_status()
    }

# Mount enhanced API routes
try:
    from .enhanced_routes import app as enhanced_app
    app.mount("/api/v2", enhanced_app)
    print("✅ Enhanced API routes mounted at /api/v2")
except ImportError as e:
    print(f"⚠️ Enhanced routes not available: {e}")

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting Hack Stack Backend...")
    print(f"📊 Mode: {config.mode}")
    print(f"🔗 Available vendors: {vendor_service.available_vendors}")
    print(f"🌐 API: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "api.routes:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )