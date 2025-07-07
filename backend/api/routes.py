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

# Request models
class VendorRequest(BaseModel):
    operation: str
    data: Dict[str, Any] = {}

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
    """Search businesses with query"""
    return business_service.search(q, limit)

@app.get("/api/metrics")
async def get_metrics():
    """Simple metrics for demo purposes"""
    return {
        "total_businesses": len(business_service.get_businesses(100)),
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