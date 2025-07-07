"""
Mock Data - Compelling Sample Data for Demos
Rich, realistic data that tells a story
"""

from typing import List, Dict, Any

# Rich business stories that make demos memorable
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
    },
    {
        "id": 4,
        "name": "Binary Bookshop",
        "tagline": "Literature for the digital age",
        "type": "bookstore",
        "neighborhood": "SOMA",
        "founded": 2020,
        "story": "Founded during the pandemic by a former Google engineer who believed physical books could coexist with digital tech. Features QR codes linking to author interviews.",
        "features": ["Tech book specialization", "Author video interviews", "Programming workshops"],
        "status": "thriving",
        "ai_summary": "A modern bookstore bridging physical and digital reading experiences."
    }
]

# Mock AI responses that match real API formats
MOCK_AI_RESPONSES = {
    "openai_analysis": {
        "analysis": "This business represents the evolution of local culture in the digital age, combining traditional craftsmanship with modern innovation.",
        "sentiment": "positive",
        "key_themes": ["innovation", "community", "tradition", "technology"],
        "suggested_improvements": ["expand social media presence", "host more community events", "partner with local tech companies"],
        "confidence": 0.92
    },
    
    "anthropic_structure": {
        "structured_data": {
            "business_category": "innovative_local",
            "community_impact": "high", 
            "unique_value_proposition": "combines traditional craft with modern innovation",
            "target_demographic": "tech-savvy millennials and Gen Z",
            "competitive_advantages": ["unique positioning", "strong community ties", "innovative approach"],
            "growth_potential": "high"
        },
        "narrative_quality": "compelling",
        "story_completeness": 0.88
    },
    
    "weaviate_similarity": {
        "similar_businesses": [
            {
                "name": "Code & Coffee",
                "tagline": "Fuel for developers",
                "similarity_score": 0.89
            },
            {
                "name": "Analog Digital", 
                "tagline": "Bridging old and new",
                "similarity_score": 0.76
            }
        ],
        "total_results": 8,
        "search_time_ms": 45
    }
}

def get_businesses(limit: int = 10) -> List[Dict[str, Any]]:
    """Get mock businesses for demo"""
    return DEMO_BUSINESSES[:limit]

def search_businesses(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Mock business search"""
    query_lower = query.lower()
    results = []
    
    for business in DEMO_BUSINESSES:
        # Simple text matching
        if (query_lower in business["name"].lower() or 
            query_lower in business["story"].lower() or
            query_lower in business["tagline"].lower()):
            results.append(business)
    
    return results[:limit]

def get_mock_ai_response(vendor: str, operation: str) -> Dict[str, Any]:
    """Get mock AI response for vendor/operation"""
    if vendor == "openai" and operation == "analyze":
        return MOCK_AI_RESPONSES["openai_analysis"]
    elif vendor == "anthropic" and operation == "extract_structure":
        return MOCK_AI_RESPONSES["anthropic_structure"]
    elif vendor == "weaviate" and operation == "similarity_search":
        return MOCK_AI_RESPONSES["weaviate_similarity"]
    else:
        return {
            "message": f"Mock response from {vendor} for {operation}",
            "vendor": vendor,
            "operation": operation,
            "mock": True
        }