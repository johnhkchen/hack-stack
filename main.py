#!/usr/bin/env python3
"""
Hackathon-Optimized Demo Stack
Foundation: Single file that starts a web server in <30 seconds

Three-Layer Reality:
1. It Works (mock data, no config) ✅
2. It's Real (live APIs, minimal config) 
3. It's Production (monitoring, deployment)
"""

import json
import os
import random
from pathlib import Path
from typing import Dict, Any, List, Optional, Protocol
from datetime import datetime

import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# =============================================================================
# LAYER 1: IT WORKS (Mock Data, No Config)
# =============================================================================

# Simple vendor protocol - just one method!
class VendorProtocol(Protocol):
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ...

# Mock data that tells a compelling story
MOCK_BUSINESSES = [
    {
        "id": 1,
        "name": "Quantum Coffee Co.",
        "tagline": "Where physics meets caffeine",
        "type": "cafe",
        "neighborhood": "Mission",
        "founded": 2019,
        "story": "Started by two quantum physicists who left academia to perfect the science of coffee extraction. Their signature 'Heisenberg Blend' changes flavor based on observation.",
        "features": ["Molecular gastronomy", "Physics-themed drinks", "Coding meetups"],
        "status": "thriving",
        "ai_summary": "A unique cafe combining scientific precision with artisanal coffee culture."
    },
    {
        "id": 2,
        "name": "Vinyl Rebellion Records",
        "tagline": "Analog souls in a digital world",
        "type": "record_store",
        "neighborhood": "Haight",
        "founded": 1967,
        "story": "Survived the digital revolution by becoming a cultural hub. The owners curate rare finds and host intimate acoustic sessions every Friday night.",
        "features": ["Rare vinyl collection", "Live acoustic sessions", "Turntable repair"],
        "status": "legendary",
        "ai_summary": "A legendary record store that has become a cultural landmark for music lovers."
    },
    {
        "id": 3,
        "name": "Midnight Ramen Lab",
        "tagline": "Ramen perfected through 10,000 experiments",
        "type": "restaurant",
        "neighborhood": "Tenderloin",
        "founded": 2021,
        "story": "Chef Yuki spent 3 years perfecting a single ramen recipe using data science and taste testing. Open only 11PM-3AM for the true ramen experience.",
        "features": ["Data-driven recipes", "24-hour broth process", "Interactive flavor journey"],
        "status": "cult_following",
        "ai_summary": "An innovative ramen shop that uses scientific methods to create the perfect bowl."
    }
]

# Mock vendor implementations
class MockOpenAI:
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        business = random.choice(MOCK_BUSINESSES)
        return {
            "analysis": f"This business represents the evolution of {business['type']} culture in San Francisco.",
            "sentiment": "positive",
            "key_themes": ["innovation", "community", "tradition"],
            "suggested_improvements": ["expand social media presence", "host more community events"],
            "confidence": 0.92
        }

class MockAnthropic:
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "structured_data": {
                "business_category": "innovative_local",
                "community_impact": "high",
                "unique_value_proposition": "combines traditional craft with modern innovation",
                "target_demographic": "tech-savvy millennials and Gen Z"
            },
            "narrative_quality": "compelling",
            "story_completeness": 0.88
        }

class MockWeaviate:
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        similar_businesses = random.sample(MOCK_BUSINESSES, 2)
        return {
            "similar_businesses": similar_businesses,
            "similarity_scores": [0.89, 0.76],
            "search_query": data.get("query", "innovative businesses"),
            "total_results": len(MOCK_BUSINESSES)
        }

# =============================================================================
# LAYER 2: IT'S REAL (Live APIs, Minimal Config)
# =============================================================================

def detect_environment() -> Dict[str, Any]:
    """Smart environment detection - the key to progressive enhancement"""
    env_status = {
        "mode": "mock",  # default to mock
        "available_vendors": [],
        "startup_time": "< 30 seconds",
        "demo_ready": True
    }
    
    # Check for API keys
    if os.getenv("OPENAI_API_KEY"):
        env_status["available_vendors"].append("openai")
    if os.getenv("ANTHROPIC_API_KEY"):
        env_status["available_vendors"].append("anthropic")
    if os.getenv("WEAVIATE_API_KEY"):
        env_status["available_vendors"].append("weaviate")
    
    # If we have any real APIs, we're in hybrid mode
    if env_status["available_vendors"]:
        env_status["mode"] = "hybrid"
        env_status["startup_time"] = "< 45 seconds"
    
    return env_status

# Simple vendor registry - just a dictionary!
class VendorRegistry:
    def __init__(self):
        self.vendors = {
            "openai": MockOpenAI(),
            "anthropic": MockAnthropic(), 
            "weaviate": MockWeaviate()
        }
        self.env_status = detect_environment()
    
    async def process(self, vendor_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process with automatic fallback to mock"""
        if vendor_name not in self.vendors:
            raise HTTPException(404, f"Vendor {vendor_name} not found")
        
        try:
            # In real implementation, this would try live API first
            result = await self.vendors[vendor_name].process(data)
            result["_meta"] = {
                "vendor": vendor_name,
                "mode": self.env_status["mode"],
                "timestamp": datetime.now().isoformat()
            }
            return result
        except Exception as e:
            # Graceful fallback to mock
            mock_result = await self.vendors[vendor_name].process(data)
            mock_result["_meta"] = {
                "vendor": vendor_name,
                "mode": "mock_fallback",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return mock_result

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="Hack Stack Demo",
    description="Progressive Enhancement Demo Stack",
    version="1.0.0"
)

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vendor registry
vendors = VendorRegistry()

# Pydantic models
class BusinessQuery(BaseModel):
    query: str
    limit: int = 10

class VendorRequest(BaseModel):
    operation: str
    data: Dict[str, Any]

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Single-file demo with embedded frontend"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html data-theme="light">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Hack Stack Demo</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
    <style>
        .demo-indicator { 
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            text-align: center;
            margin-bottom: 2rem;
            border: none;
        }
        .business-card {
            border: 1px solid var(--pico-primary-border);
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
            background: var(--pico-card-background-color);
            transition: transform 0.2s;
        }
        .business-card:hover { transform: translateY(-2px); }
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 500;
            margin-top: 0.5rem;
        }
        .thriving { background: #d4edda; color: #155724; }
        .legendary { background: #fff3cd; color: #856404; }
        .cult_following { background: #f8d7da; color: #721c24; }
        .vendor-status {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }
        .vendor-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #28a745;
        }
        .vendor-dot.mock { background: #ffc107; }
        .vendor-dot.error { background: #dc3545; }
        .ai-controls { 
            display: grid; 
            gap: 0.5rem; 
            margin-bottom: 1rem;
        }
        @media (min-width: 768px) {
            .ai-controls { grid-template-columns: repeat(3, 1fr); }
        }
        .confidence-bar {
            background: var(--pico-border-color);
            border-radius: 0.25rem;
            height: 1rem;
            margin-top: 0.5rem;
            overflow: hidden;
            position: relative;
        }
        .confidence-fill {
            background: linear-gradient(90deg, #28a745, #20c997);
            height: 100%;
            transition: width 0.5s ease;
        }
        .confidence-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 0.75rem;
            color: white;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <main class="container">
        <div class="demo-indicator">
            <h1>🚀 Hack Stack Demo</h1>
            <p><strong>Single command:</strong> <code>just start</code> | <strong>No build steps</strong> | <strong>Works offline</strong></p>
            <div class="vendor-status">
                <div class="vendor-dot" id="status-dot"></div>
                <span>
                    Mode: <span id="env-mode">Loading...</span> | 
                    Vendors: <span id="vendor-count">0</span> | 
                    Ready: <span id="ready-status">Checking...</span>
                </span>
            </div>
        </div>

        <div class="grid">
            <div>
                <h2>🏢 Demo Businesses</h2>
                <div id="business-list">Loading compelling mock data...</div>
            </div>
            <div>
                <h2>🤖 AI Analysis</h2>
                <div class="ai-controls">
                    <button onclick="analyzeWithOpenAI()" class="secondary">🔍 OpenAI</button>
                    <button onclick="analyzeWithAnthropic()" class="secondary">📊 Anthropic</button>
                    <button onclick="searchWithWeaviate()" class="secondary">🔗 Weaviate</button>
                </div>
                <div id="ai-analysis"></div>
            </div>
        </div>

        <footer style="text-align: center; margin-top: 3rem; padding: 2rem; border-top: 1px solid var(--pico-border-color);">
            <p><em>Built for hackathons: <strong>nix develop</strong> + <strong>uv</strong> + <strong>just</strong></em></p>
            <p><small>No complexity black holes • Progressive enhancement • Portfolio worthy</small></p>
        </footer>
    </main>

    <script>
        // Status management
        let currentStatus = { mode: 'loading', available_vendors: [], demo_ready: false };
        
        // Load environment status
        fetch('/api/health')
            .then(r => r.json())
            .then(data => {
                currentStatus = data;
                updateStatusDisplay();
            })
            .catch(() => {
                currentStatus = { mode: 'error', available_vendors: [], demo_ready: false };
                updateStatusDisplay();
            });

        function updateStatusDisplay() {
            document.getElementById('env-mode').textContent = currentStatus.mode;
            document.getElementById('vendor-count').textContent = currentStatus.available_vendors.length;
            document.getElementById('ready-status').textContent = currentStatus.demo_ready ? '✅' : '❌';
            
            const dot = document.getElementById('status-dot');
            if (currentStatus.mode === 'mock') dot.className = 'vendor-dot mock';
            else if (currentStatus.mode === 'error') dot.className = 'vendor-dot error';
            else dot.className = 'vendor-dot';
        }

        // Load businesses
        fetch('/api/businesses')
            .then(r => r.json())
            .then(businesses => {
                const html = businesses.map(b => `
                    <div class="business-card">
                        <h3>${b.name}</h3>
                        <p><em>${b.tagline}</em></p>
                        <p>${b.story}</p>
                        <div style="font-size: 0.9rem; color: var(--pico-muted-color); margin: 1rem 0;">
                            <strong>Type:</strong> ${b.type} | 
                            <strong>Founded:</strong> ${b.founded} | 
                            <strong>Area:</strong> ${b.neighborhood}
                        </div>
                        <div style="margin-top: 0.5rem;">
                            ${b.features.map(f => `<span style="background: var(--pico-primary-background); color: var(--pico-primary-color); padding: 0.2rem 0.4rem; border-radius: 0.2rem; font-size: 0.8rem; margin-right: 0.3rem;">${f}</span>`).join('')}
                        </div>
                        <span class="status-badge ${b.status}">${b.status.replace('_', ' ')}</span>
                    </div>
                `).join('');
                document.getElementById('business-list').innerHTML = html;
            })
            .catch(() => {
                document.getElementById('business-list').innerHTML = '<p>Failed to load businesses. Check connection.</p>';
            });

        // AI Analysis functions
        async function callVendor(vendor, operation) {
            const analysis = document.getElementById('ai-analysis');
            analysis.innerHTML = '<p aria-busy="true">Analyzing with ' + vendor + '...</p>';
            
            try {
                const response = await fetch(`/api/vendor/${vendor}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ operation, data: {} })
                });
                const result = await response.json();
                displayResult(result, vendor);
            } catch (error) {
                analysis.innerHTML = `<div style="border: 1px solid var(--pico-del-color); padding: 1rem; border-radius: 0.5rem;">
                    <strong>Error:</strong> ${error.message}
                </div>`;
            }
        }

        function displayResult(result, vendor) {
            const analysis = document.getElementById('ai-analysis');
            let content = `<div style="border: 1px solid var(--pico-border-color); border-radius: 0.5rem; padding: 1rem; background: var(--pico-card-background-color);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--pico-border-color);">
                    <h4 style="margin: 0;">Analysis Results</h4>
                    <div style="display: flex; gap: 0.5rem;">
                        <span style="background: var(--pico-primary-background); color: var(--pico-primary-color); padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;">${vendor}</span>
                        <span style="background: var(--pico-secondary-background); color: var(--pico-secondary-color); padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;">${result._meta?.mode || 'unknown'}</span>
                    </div>
                </div>`;
            
            if (result.analysis) {
                content += `<p><strong>Analysis:</strong> ${result.analysis}</p>`;
            }
            if (result.sentiment) {
                content += `<p><strong>Sentiment:</strong> <span style="background: #d4edda; color: #155724; padding: 0.25rem 0.5rem; border-radius: 0.25rem;">${result.sentiment}</span></p>`;
            }
            if (result.key_themes) {
                content += `<p><strong>Themes:</strong> ${result.key_themes.join(', ')}</p>`;
            }
            if (result.confidence) {
                content += `<p><strong>Confidence:</strong></p>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${result.confidence * 100}%"></div>
                        <span class="confidence-text">${(result.confidence * 100).toFixed(1)}%</span>
                    </div>`;
            }
            if (result.similar_businesses) {
                content += `<p><strong>Similar Businesses:</strong></p>`;
                result.similar_businesses.forEach(b => {
                    content += `<div style="background: var(--pico-background-color); padding: 0.5rem; margin: 0.25rem 0; border-radius: 0.25rem; border: 1px solid var(--pico-border-color);">
                        <strong>${b.name}</strong> - ${b.tagline}
                    </div>`;
                });
            }
            if (result.structured_data) {
                content += `<p><strong>Structured Data:</strong></p>
                    <pre style="background: var(--pico-code-background-color); padding: 1rem; border-radius: 0.25rem; font-size: 0.8rem; overflow-x: auto;">${JSON.stringify(result.structured_data, null, 2)}</pre>`;
            }
            
            content += '</div>';
            analysis.innerHTML = content;
        }

        function analyzeWithOpenAI() { callVendor('openai', 'analyze'); }
        function analyzeWithAnthropic() { callVendor('anthropic', 'extract_structure'); }
        function searchWithWeaviate() { callVendor('weaviate', 'similarity_search'); }
    </script>
</body>
</html>
    """)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return vendors.env_status

@app.get("/api/businesses")
async def get_businesses(limit: int = 10):
    """Get mock businesses"""
    return MOCK_BUSINESSES[:limit]

@app.post("/api/vendor/{vendor_name}")
async def process_vendor(vendor_name: str, request: VendorRequest):
    """Process request through vendor"""
    return await vendors.process(vendor_name, request.data)

@app.get("/api/search")
async def search_businesses(q: str = "innovative"):
    """Search businesses"""
    results = [b for b in MOCK_BUSINESSES if q.lower() in b["name"].lower() or q.lower() in b["story"].lower()]
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }

# =============================================================================
# LAYER 3: IT'S PRODUCTION (if time permits)
# =============================================================================

@app.get("/api/metrics")
async def get_metrics():
    """Simple metrics endpoint"""
    return {
        "uptime": "< 1 minute",
        "requests_served": random.randint(10, 100),
        "mock_mode_usage": "90%",
        "demo_success_rate": "100%"
    }

# =============================================================================
# MAIN - RUNS IN < 30 SECONDS
# =============================================================================

if __name__ == "__main__":
    print("🚀 Starting Hack Stack Demo...")
    print("📊 Environment Status:")
    print(f"   Mode: {vendors.env_status['mode']}")
    print(f"   Vendors: {len(vendors.env_status['available_vendors'])}")
    print(f"   Ready: {vendors.env_status['demo_ready']}")
    print("\n🌐 Demo available at: http://localhost:8000")
    print("📡 API docs at: http://localhost:8000/docs")
    print("\n⚡ Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)