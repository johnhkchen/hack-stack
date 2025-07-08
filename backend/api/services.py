"""
Services - Business Logic and Vendor Integration
Clean separation with Protocol-based vendor abstraction
"""

import os
import json
from datetime import datetime
from typing import Protocol, Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

@dataclass
class VendorCredentials:
    """Tracks vendor credentials and their sources"""
    vendor: str
    has_key: bool
    source: str  # "env_file", "host_env", "none"
    is_secure: bool  # False if using host environment
    warning: Optional[str] = None

@dataclass
class Config:
    """Application configuration with secure credential detection"""
    mode: str = "mock"
    debug: bool = True
    available_vendors: List[str] = None
    vendor_credentials: Dict[str, VendorCredentials] = None
    
    def __post_init__(self):
        if self.available_vendors is None:
            self.available_vendors = []
        if self.vendor_credentials is None:
            self.vendor_credentials = {}
        self._detect_environment()
    
    def _detect_environment(self):
        """Secure environment detection with accurate source tracking"""
        if os.getenv('FORCE_MOCK', '').lower() in ('true', '1'):
            self.mode = "mock"
            return
        
        vendor_keys = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY', 
            'weaviate': 'WEAVIATE_API_KEY'
        }
        
        for vendor, env_var in vendor_keys.items():
            key_value = os.getenv(env_var)
            
            if key_value:
                # Actually check if the key is defined in .env file
                source, is_secure, warning = self._determine_credential_source(env_var, key_value)
                
                self.vendor_credentials[vendor] = VendorCredentials(
                    vendor=vendor,
                    has_key=True,
                    source=source,
                    is_secure=is_secure,
                    warning=warning
                )
                # Note: Credential detected but vendor still uses mock implementation
                self.available_vendors.append(vendor)
            else:
                self.vendor_credentials[vendor] = VendorCredentials(
                    vendor=vendor,
                    has_key=False,
                    source="none",
                    is_secure=True,  # No key is better than insecure key
                    warning=None
                )
        
        # All vendors currently use mock implementations
        # Set to mock until real implementations are added
        self.mode = "mock"
    
    def _determine_credential_source(self, env_var: str, key_value: str):
        """Actually determine where the credential is coming from"""
        env_file_path = Path("/app/.env")
        
        # Check if .env file exists and contains this variable with a value
        if env_file_path.exists():
            try:
                with open(env_file_path, 'r') as f:
                    env_content = f.read()
                    
                # Look for the variable in .env file with a non-empty value
                for line in env_content.splitlines():
                    line = line.strip()
                    if line.startswith(f'{env_var}='):
                        # Extract value after the equals sign
                        value = line[len(f'{env_var}='):].strip()
                        # Only consider it from env file if it has an actual value
                        if value and value != '':
                            return "env_file", True, None
                        break  # Found the variable but it's empty
                    
            except Exception:
                pass  # Fall through to host detection
        
        # If we get here, key is from host environment (insecure)
        return "host_env", False, "Using host environment key - insecure! Use .env file instead"
    
    @property
    def startup_time(self) -> str:
        return "Development mode - fast startup"

# Global config instance
_config = None

def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config

# =============================================================================
# Mock Data
# =============================================================================

DEMO_BUSINESSES = [
    {
        "id": 1,
        "name": "Quantum Coffee Co.",
        "tagline": "Where physics meets caffeine",
        "type": "cafe",
        "neighborhood": "Mission",
        "founded": 2019,
        "story": "Started by two quantum physicists who left academia to perfect the science of coffee extraction. Their signature 'Heisenberg Blend' changes flavor based on observation.",
        "features": ["Molecular gastronomy", "Physics-themed drinks", "Coding meetups"],
        "status": "thriving"
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
        "status": "legendary"
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
        "status": "cult_following"
    }
]

MOCK_AI_RESPONSES = {
    "openai": {
        "analyze": {
            "analysis": "This business represents the evolution of local culture, combining traditional craftsmanship with modern innovation.",
            "sentiment": "positive",
            "key_themes": ["innovation", "community", "tradition"],
            "confidence": 0.92,
            "suggestions": ["expand online presence", "host community events"]
        }
    },
    "anthropic": {
        "extract_structure": {
            "structured_data": {
                "business_category": "innovative_local",
                "community_impact": "high",
                "target_demographic": "tech-savvy millennials",
                "growth_potential": "high"
            },
            "narrative_quality": "compelling",
            "completeness": 0.88
        }
    },
    "weaviate": {
        "similarity_search": {
            "similar_businesses": [
                {"name": "Code & Coffee", "tagline": "Fuel for developers", "score": 0.89},
                {"name": "Analog Digital", "tagline": "Bridging old and new", "score": 0.76}
            ],
            "total_results": 8,
            "search_time_ms": 45
        }
    }
}

# =============================================================================
# Vendor Protocol and Implementations
# =============================================================================

class VendorProtocol(Protocol):
    """Protocol for all vendor integrations"""
    async def process(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        ...

class MockVendor:
    """Mock vendor implementation with realistic responses"""
    
    def __init__(self, vendor_name: str):
        self.vendor_name = vendor_name
    
    async def process(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Return realistic mock responses"""
        responses = MOCK_AI_RESPONSES.get(self.vendor_name, {})
        return responses.get(operation, {
            "message": f"Mock response from {self.vendor_name}",
            "operation": operation,
            "mock": True
        })

class VendorService:
    """Service for managing AI vendor integrations"""
    
    def __init__(self):
        self.config = get_config()
        self.available_vendors = self.config.available_vendors
        self._vendors = {}
        self._initialize_vendors()
    
    def _initialize_vendors(self):
        """Initialize available vendors"""
        # All vendors currently use mock implementations
        # Real vendor clients would be initialized here when implemented
        for vendor in ["openai", "anthropic", "weaviate"]:
            self._vendors[vendor] = MockVendor(vendor)
    
    async def process(self, vendor_name: str, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request through vendor with automatic fallback"""
        if vendor_name not in ["openai", "anthropic", "weaviate"]:
            raise ValueError(f"Unknown vendor: {vendor_name}")
        
        try:
            vendor = self._vendors[vendor_name]
            result = await vendor.process(operation, data)
            
            # Add metadata
            result["_meta"] = {
                "vendor": vendor_name,
                "operation": operation,
                "mode": "mock",  # All vendors currently use mock implementations
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            # Graceful fallback
            fallback = MockVendor(vendor_name)
            result = await fallback.process(operation, data)
            result["_meta"] = {
                "vendor": vendor_name,
                "operation": operation,
                "mode": "mock_fallback",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return result

class BusinessService:
    """Service for business data operations with legacy business registry data"""
    
    def __init__(self):
        self._cache = {}
        self._legacy_businesses = []
        self._load_legacy_businesses()
    
    def _load_legacy_businesses(self):
        """Load legacy business applications dataset from JSON file"""
        try:
            # Try enhanced dataset with rich narratives first
            enhanced_data_path = Path(__file__).parent.parent / "data" / "enhanced_legacy_businesses.json"
            if enhanced_data_path.exists():
                with open(enhanced_data_path, 'r') as f:
                    data = json.load(f)
                    self._legacy_businesses = data.get("applications", [])
                    print(f"✅ Loaded {len(self._legacy_businesses)} enhanced legacy businesses with rich narratives")
                    return
            
            # Try standard application-based dataset
            app_data_path = Path(__file__).parent.parent / "data" / "legacy_business_applications.json"
            if app_data_path.exists():
                with open(app_data_path, 'r') as f:
                    data = json.load(f)
                    self._legacy_businesses = data.get("applications", [])
                    print(f"✅ Loaded {len(self._legacy_businesses)} legacy business applications from registry")
                    return
            
            # Fallback to old dataset
            data_path = Path(__file__).parent.parent / "data" / "legacy_businesses.json"
            if data_path.exists():
                with open(data_path, 'r') as f:
                    data = json.load(f)
                    self._legacy_businesses = data.get("businesses", [])
                    print(f"✅ Loaded {len(self._legacy_businesses)} legacy businesses from dataset")
            else:
                print("⚠️ Legacy businesses dataset not found, using demo data")
                self._legacy_businesses = DEMO_BUSINESSES
        except Exception as e:
            print(f"❌ Error loading legacy businesses: {e}")
            self._legacy_businesses = DEMO_BUSINESSES
    
    def get_businesses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get businesses with caching and legacy data support"""
        cache_key = f"businesses_{limit}"
        
        if cache_key not in self._cache:
            # Use legacy businesses if available, otherwise fall back to demo data
            businesses = self._legacy_businesses if self._legacy_businesses else DEMO_BUSINESSES
            self._cache[cache_key] = businesses[:limit]
        
        return self._cache[cache_key]
    
    def get_business_by_id(self, business_id: int) -> Dict[str, Any] | None:
        """Get single business by ID from legacy dataset"""
        businesses = self._legacy_businesses if self._legacy_businesses else DEMO_BUSINESSES
        
        for business in businesses:
            if business.get("id") == business_id:
                return business
        return None
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Enhanced search with legacy business data"""
        query_lower = query.lower()
        results = []
        businesses = self._legacy_businesses if self._legacy_businesses else DEMO_BUSINESSES
        
        for business in businesses:
            # Search across multiple fields including rich narratives
            searchable_fields = [
                business.get("name", ""),
                business.get("tagline", ""),
                business.get("founding_story", ""),
                business.get("cultural_impact", ""),
                business.get("unique_features", ""),
                business.get("story", ""),  # fallback
                business.get("type", ""),
                business.get("neighborhood", ""),
                " ".join(business.get("features", [])),
                " ".join(business.get("notable_features", [])),
                " ".join(business.get("keywords", [])),
                " ".join(business.get("amenities", []))
            ]
            
            searchable_text = " ".join(searchable_fields).lower()
            
            if query_lower in searchable_text:
                # Add relevance score based on where the match was found
                score = 0
                if query_lower in business.get("name", "").lower():
                    score += 10
                if query_lower in business.get("tagline", "").lower():
                    score += 5
                if query_lower in business.get("founding_story", "").lower():
                    score += 8  # High-value narrative content
                if query_lower in business.get("cultural_impact", "").lower():
                    score += 8  # High-value narrative content
                if query_lower in business.get("unique_features", "").lower():
                    score += 7  # High-value narrative content
                if query_lower in business.get("type", "").lower():
                    score += 8
                if query_lower in business.get("neighborhood", "").lower():
                    score += 6
                if query_lower in " ".join(business.get("keywords", [])).lower():
                    score += 5  # Structured searchable content
                if query_lower in business.get("story", "").lower():
                    score += 3  # fallback field
                
                business_with_score = business.copy()
                business_with_score["_search_score"] = score
                results.append(business_with_score)
        
        # Sort by relevance score
        results.sort(key=lambda x: x.get("_search_score", 0), reverse=True)
        
        # Remove search score from final results
        for result in results:
            result.pop("_search_score", None)
        
        return results[:limit]
    
    def get_businesses_by_neighborhood(self, neighborhood: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get businesses filtered by neighborhood"""
        businesses = self._legacy_businesses if self._legacy_businesses else DEMO_BUSINESSES
        
        results = [
            business for business in businesses 
            if business.get("neighborhood", "").lower() == neighborhood.lower()
        ]
        
        return results[:limit]
    
    def get_businesses_by_type(self, business_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get businesses filtered by type/category"""
        businesses = self._legacy_businesses if self._legacy_businesses else DEMO_BUSINESSES
        
        results = [
            business for business in businesses 
            if business.get("type", "").lower() == business_type.lower()
        ]
        
        return results[:limit]
    
    def get_neighborhoods(self) -> List[str]:
        """Get list of all unique neighborhoods"""
        businesses = self._legacy_businesses if self._legacy_businesses else DEMO_BUSINESSES
        neighborhoods = set()
        
        for business in businesses:
            if business.get("neighborhood"):
                neighborhoods.add(business["neighborhood"])
        
        return sorted(list(neighborhoods))
    
    def get_business_types(self) -> List[str]:
        """Get list of all unique business types"""
        businesses = self._legacy_businesses if self._legacy_businesses else DEMO_BUSINESSES
        types = set()
        
        for business in businesses:
            if business.get("type"):
                types.add(business["type"])
        
        return sorted(list(types))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get business statistics"""
        businesses = self._legacy_businesses if self._legacy_businesses else DEMO_BUSINESSES
        
        total = len(businesses)
        active = len([b for b in businesses if b.get("status") == "active"])
        neighborhoods = len(self.get_neighborhoods())
        types = len(self.get_business_types())
        
        # Calculate average rating
        ratings = [b.get("rating", 0) for b in businesses if b.get("rating")]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            "total_businesses": total,
            "active_businesses": active,
            "total_neighborhoods": neighborhoods,
            "total_types": types,
            "average_rating": round(avg_rating, 1) if avg_rating else None,
            "data_source": "legacy_registry" if self._legacy_businesses else "demo_data"
        }