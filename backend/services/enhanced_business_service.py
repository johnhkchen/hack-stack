"""
Enhanced Business Service with Pydantic Schema Integration
=========================================================

Production-ready service demonstrating the full RAG system architecture:
- Schema-driven data modeling
- Semantic search foundations  
- Rich mock data for demonstration
- Vector search simulation
"""

import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from models.legacy_business import (
    LegacyBusiness, LegacyBusinessSummary, LegacyBusinessSearch,
    LocationHistory, Recognition, OwnershipHistory,
    NeighborhoodEnum, BusinessStatusEnum, RAGWeightEnum
)

class EnhancedBusinessService:
    """
    Enhanced business service showcasing RAG system capabilities.
    
    Features:
    - Schema-validated business data
    - Semantic search simulation
    - Rich narrative content for RAG
    - Vector similarity foundations
    - Advanced filtering and search
    """
    
    def __init__(self):
        self.businesses: List[LegacyBusiness] = []
        self.vector_embeddings: Dict[str, List[float]] = {}  # Simulated embeddings
        self._load_enhanced_mock_data()
        self._simulate_vector_embeddings()
    
    def _load_enhanced_mock_data(self):
        """Load rich mock data showcasing RAG system potential"""
        
        # The Wok Shop - Authentic Chinatown business
        wok_shop = LegacyBusiness(
            business_name="The Wok Shop",
            legal_name="The Wok Shop LLC",
            dba_name="The Wok Shop",
            founding_year=1972,
            years_at_current_location=51,
            current_address="718 Grant Avenue",
            neighborhood=NeighborhoodEnum.CHINATOWN,
            business_type="Kitchen Supply Store",
            business_category="Retail - Specialty Goods",
            
            founding_story="""Founded in 1972 after President Nixon's historic visit to China opened American interest in authentic Chinese cooking. Tane Chan, a Chinese-American entrepreneur, recognized the need for traditional wok cooking equipment in American kitchens. Starting with just a few dozen carbon steel woks imported directly from Guangzhou, the shop became the go-to destination for both professional chefs and home cooking enthusiasts seeking authentic Chinese cookware.""",
            
            cultural_significance="""The Wok Shop serves as more than a retail store - it's a cultural bridge connecting traditional Chinese cooking methods with American home kitchens. For over 50 years, it has educated customers about proper wok seasoning, stir-fry techniques, and the cultural significance of communal cooking in Chinese families. The shop has hosted countless cooking demonstrations and has been featured in numerous culinary publications as an authentic source for traditional Chinese cooking wisdom.""",
            
            physical_traditions="""The store's iconic pagoda-style neon sign has been a Chinatown landmark since 1974. Inside, hundreds of woks hang from the ceiling like a metallic forest, creating an immediately recognizable atmosphere. The original wooden displays and hand-painted price signs maintain the authentic feel of a traditional Chinese market. The distinctive aroma of seasoned carbon steel and the sound of woks being tested create a sensory experience unique in American retail.""",
            
            community_impact="""Beyond serving San Francisco's Chinese-American community, The Wok Shop has become an international destination for cooking enthusiasts. It ships traditional cookware worldwide and has educated thousands of customers about Chinese culinary traditions. The business has supported local Chinatown festivals and cultural events, serving as an anchor business that helps maintain the neighborhood's authentic character.""",
            
            historical_significance="""Surviving through Chinatown's transformation from the 1970s to today, The Wok Shop witnessed the neighborhood's evolution while maintaining traditional values. It operated through economic downturns, the dot-com boom, and the COVID-19 pandemic, adapting while preserving authentic Chinese cooking culture. The shop represents successful cultural preservation in an increasingly gentrified urban environment.""",
            
            location_history=[
                LocationHistory(
                    address="718 Grant Avenue",
                    start_year=1972,
                    is_current=True
                )
            ],
            
            ownership_history=[
                OwnershipHistory(
                    owner_name="Tane Chan",
                    start_year=1972,
                    end_year=1995,
                    generation=1
                ),
                OwnershipHistory(
                    owner_name="Chan Family Trust",
                    start_year=1995,
                    generation=2
                )
            ],
            
            recognition=[
                Recognition(
                    title="Featured on PBS Cooking Shows",
                    year=2019,
                    issuer="Public Broadcasting Service",
                    description="Multiple segments showcasing traditional wok cooking techniques",
                    media_type="television"
                ),
                Recognition(
                    title="Bon Appétit Best Kitchen Store",
                    year=2018,
                    issuer="Bon Appétit Magazine",
                    description="Named among America's best specialty kitchen stores",
                    media_type="magazine"
                ),
                Recognition(
                    title="Chinatown Cultural Heritage Award",
                    year=2022,
                    issuer="Chinese Historical Society of America",
                    description="Recognition for preserving traditional cooking culture"
                )
            ],
            
            unique_features=[
                "Original 1970s pagoda neon sign",
                "Woks hanging from ceiling display",
                "Hand-seasoned carbon steel woks",
                "International shipping worldwide",
                "Traditional Chinese cooking demonstrations"
            ],
            
            signature_products=[
                "Carbon steel woks (14-inch to 24-inch)",
                "Bamboo steamers",
                "Chinese cleavers",
                "Clay sand pots",
                "Traditional wok accessories"
            ],
            
            demo_highlights=[
                "50+ years serving authentic Chinese cooking community",
                "Featured on PBS and Food Network cooking shows",
                "Ships traditional cookware internationally",
                "Preserved traditional wok-making techniques",
                "Living piece of Chinatown culinary history"
            ],
            
            application_id="LBR-2016-17-064",
            heritage_score=92,
            current_status=BusinessStatusEnum.ACTIVE,
            
            source_documents=["wok_shop_application.pdf", "chinatown_heritage_study.pdf"],
            extraction_confidence=0.95
        )
        
        # Molinari Delicatessen - Historic Italian-American business
        molinari = LegacyBusiness(
            business_name="Molinari Delicatessen",
            legal_name="Molinari Delicatessen LLC",
            founding_year=1896,
            years_at_current_location=127,
            current_address="476 Broadway",
            neighborhood=NeighborhoodEnum.NORTH_BEACH,
            business_type="Delicatessen",
            business_category="Food & Beverage - Specialty",
            
            founding_story="""Established in 1896 by Domenico Molinari, an immigrant from Liguria, Italy, who brought traditional salumi-making techniques to San Francisco's growing Italian-American community. Domenico learned charcuterie from his father in the hills above Genoa and saw an opportunity to serve fellow immigrants who missed the cured meats of their homeland. Starting with just a few hanging salamis, the shop grew to become the heart of North Beach's Italian community.""",
            
            cultural_significance="""For over 125 years, Molinari Delicatessen has served as the epicenter of North Beach's Italian-American culture. The shop has maintained authentic Ligurian traditions while adapting to serve multiple generations of Italian-Americans. It has been featured in countless films depicting San Francisco's Italian heritage and continues to be a gathering place where Italian is spoken and Old World traditions are preserved.""",
            
            physical_traditions="""The shop maintains its original 1920s interior with marble counters, hanging salamis, and vintage scales. The distinctive aroma of aged prosciutto and aged cheeses greets customers, while the sound of Italian conversation and the sight of hand-sliced meats create an authentic European market atmosphere. Family recipes for salami and pancetta remain unchanged since 1896.""",
            
            community_impact="""Molinari's has fed generations of North Beach families, provided employment for countless Italian-Americans, and served as a cultural anchor during neighborhood changes. The deli supplies restaurants throughout the Bay Area with authentic Italian specialties and has educated customers about traditional Italian food culture. It has supported community events and maintained affordable prices for longtime neighborhood residents.""",
            
            historical_significance="""Surviving the 1906 earthquake, both World Wars, and decades of urban change, Molinari Delicatessen represents continuity in San Francisco's Italian-American experience. The business witnessed North Beach's transformation from working-class Italian neighborhood to tourist destination while maintaining its authentic character. It stands as one of the last original Italian businesses in what was once the largest Italian community on the West Coast.""",
            
            location_history=[
                LocationHistory(
                    address="476 Broadway",
                    start_year=1896,
                    is_current=True
                )
            ],
            
            ownership_history=[
                OwnershipHistory(
                    owner_name="Domenico Molinari",
                    start_year=1896,
                    end_year=1920,
                    generation=1
                ),
                OwnershipHistory(
                    owner_name="Giuseppe Molinari",
                    start_year=1920,
                    end_year=1955,
                    relationship="son",
                    generation=2
                ),
                OwnershipHistory(
                    owner_name="Molinari Family Partnership",
                    start_year=1955,
                    generation=3
                )
            ],
            
            recognition=[
                Recognition(
                    title="James Beard America's Classics Award",
                    year=2013,
                    issuer="James Beard Foundation",
                    description="Recognition for outstanding local significance"
                ),
                Recognition(
                    title="Featured in The Godfather Part II",
                    year=1974,
                    issuer="Paramount Pictures",
                    description="Shop featured in iconic North Beach scenes",
                    media_type="film"
                ),
                Recognition(
                    title="San Francisco Heritage Award",
                    year=1996,
                    issuer="San Francisco Heritage",
                    description="100th anniversary recognition for cultural preservation"
                )
            ],
            
            unique_features=[
                "Original 1896 family recipes",
                "Hand-sliced prosciutto di Parma",
                "Vintage marble counters from 1920s",
                "Traditional hanging salami display",
                "Italian spoken daily by staff"
            ],
            
            signature_products=[
                "House-made salami and pancetta",
                "Imported Parmigiano-Reggiano",
                "Fresh mozzarella made daily",
                "Traditional mortadella",
                "Italian sandwich combinations"
            ],
            
            demo_highlights=[
                "127 years of continuous family operation",
                "Survived 1906 earthquake and both World Wars",
                "Featured in The Godfather Part II",
                "James Beard Award winner",
                "Last authentic Italian deli in North Beach"
            ],
            
            application_id="LBR-1896-001",
            heritage_score=98,
            current_status=BusinessStatusEnum.ACTIVE,
            
            source_documents=["molinari_application.pdf", "north_beach_italian_history.pdf"],
            extraction_confidence=0.98
        )
        
        # City Lights Bookstore - Beat Generation landmark
        city_lights = LegacyBusiness(
            business_name="City Lights Booksellers & Publishers",
            legal_name="City Lights Books, Inc.",
            dba_name="City Lights",
            founding_year=1953,
            years_at_current_location=70,
            current_address="261 Columbus Avenue",
            neighborhood=NeighborhoodEnum.NORTH_BEACH,
            business_type="Bookstore & Publisher",
            business_category="Retail - Books & Publishing",
            
            founding_story="""Founded in 1953 by Lawrence Ferlinghetti and Peter Martin as America's first all-paperback bookstore. Ferlinghetti, a poet and painter, envisioned a space that would make literature accessible to everyone through affordable paperback editions. The bookstore was named after the 1931 Charlie Chaplin film and quickly became a gathering place for writers, artists, and intellectuals seeking alternative literature unavailable in mainstream bookstores.""",
            
            cultural_significance="""City Lights became the epicenter of the Beat Generation literary movement, publishing Allen Ginsberg's 'Howl' and launching the careers of countless counterculture writers. The bookstore challenged censorship laws, promoted free speech, and introduced American readers to international literature. It remains a pilgrimage site for writers and readers worldwide, maintaining its commitment to progressive literature and social justice.""",
            
            physical_traditions="""The narrow, three-story building maintains its bohemian character with hand-written shelf tags, poetry chapbooks displayed prominently, and reading nooks that encourage browsing. The famous Poetry Room upstairs features work by Beat Generation writers alongside contemporary voices. Floor-to-ceiling bookshelves create intimate reading spaces, while the basement houses rare and underground publications.""",
            
            community_impact="""Beyond selling books, City Lights has served as a community center for literary San Francisco. It has hosted countless poetry readings, book launches, and political events. The store provides a platform for emerging writers and continues Ferlinghetti's vision of making literature accessible to all economic backgrounds. Its publishing arm has introduced numerous international authors to American audiences.""",
            
            historical_significance="""City Lights played a crucial role in the landmark 1957 obscenity trial over 'Howl,' establishing important precedents for freedom of expression. The bookstore was declared a San Francisco historic landmark in 2001 and continues to champion literary freedom. It survived economic challenges, urban development pressures, and the digital revolution while maintaining its independence and literary mission.""",
            
            location_history=[
                LocationHistory(
                    address="261 Columbus Avenue",
                    start_year=1953,
                    is_current=True
                )
            ],
            
            ownership_history=[
                OwnershipHistory(
                    owner_name="Lawrence Ferlinghetti & Peter Martin",
                    start_year=1953,
                    end_year=1955,
                    generation=1
                ),
                OwnershipHistory(
                    owner_name="Lawrence Ferlinghetti",
                    start_year=1955,
                    end_year=2021,
                    generation=1
                ),
                OwnershipHistory(
                    owner_name="City Lights Foundation",
                    start_year=2021,
                    generation=2
                )
            ],
            
            recognition=[
                Recognition(
                    title="San Francisco Historic Landmark",
                    year=2001,
                    issuer="San Francisco Landmarks Preservation Board",
                    description="Official recognition for cultural significance"
                ),
                Recognition(
                    title="Literary Landmark",
                    year=2003,
                    issuer="Friends of Libraries USA",
                    description="First bookstore designated as Literary Landmark"
                ),
                Recognition(
                    title="Outstanding Achievement in Publishing",
                    year=1994,
                    issuer="Northern California Independent Booksellers Association",
                    description="Lifetime achievement for independent publishing"
                )
            ],
            
            unique_features=[
                "First all-paperback bookstore in America",
                "Beat Generation archives and manuscripts",
                "24-hour reading policy",
                "Hand-written shelf recommendations",
                "Three-story literary labyrinth"
            ],
            
            signature_products=[
                "City Lights Pocket Poets Series",
                "Beat Generation first editions",
                "International literature translations",
                "Political and social justice books",
                "Local author collections"
            ],
            
            demo_highlights=[
                "Birthplace of Beat Generation publishing",
                "First bookstore Literary Landmark",
                "Successfully defended 'Howl' in obscenity trial",
                "70 years of independent literary culture",
                "San Francisco Historic Landmark"
            ],
            
            application_id="LBR-1953-002",
            heritage_score=96,
            current_status=BusinessStatusEnum.ACTIVE,
            
            source_documents=["city_lights_application.pdf", "beat_generation_history.pdf"],
            extraction_confidence=0.94
        )
        
        self.businesses = [wok_shop, molinari, city_lights]
    
    def _simulate_vector_embeddings(self):
        """Simulate vector embeddings for semantic search demonstration"""
        
        # In a real implementation, these would be actual embeddings from OpenAI/etc.
        # For demo purposes, we simulate embeddings as random vectors with some logic
        
        for business in self.businesses:
            # Create pseudo-embeddings based on business characteristics
            embedding = []
            
            # Simulate embeddings based on content (768 dimensions like OpenAI)
            base_vector = [random.uniform(-1, 1) for _ in range(768)]
            
            # Add semantic clustering for similar businesses
            if "food" in business.business_type.lower():
                # Food businesses cluster together
                for i in range(100):
                    base_vector[i] += 0.3
            
            if business.neighborhood == NeighborhoodEnum.NORTH_BEACH:
                # North Beach businesses cluster together
                for i in range(100, 200):
                    base_vector[i] += 0.2
            
            if business.founding_year and business.founding_year < 1920:
                # Historic businesses cluster together
                for i in range(200, 300):
                    base_vector[i] += 0.4
            
            self.vector_embeddings[business.business_name] = base_vector
    
    def get_businesses(self, limit: int = 10) -> List[LegacyBusiness]:
        """Get all businesses with limit"""
        return self.businesses[:limit]
    
    def get_business_by_name(self, name: str) -> Optional[LegacyBusiness]:
        """Get business by exact name match"""
        for business in self.businesses:
            if business.business_name.lower() == name.lower():
                return business
        return None
    
    def search_businesses(self, search_query: LegacyBusinessSearch) -> Dict[str, Any]:
        """
        Advanced search using schema-defined search capabilities.
        Demonstrates RAG system foundations with semantic similarity.
        """
        
        # Start with all businesses
        candidates = self.businesses.copy()
        
        # Apply filters
        if search_query.neighborhood:
            candidates = [b for b in candidates if b.neighborhood == search_query.neighborhood]
        
        if search_query.business_type:
            candidates = [b for b in candidates if 
                         search_query.business_type.lower() in b.business_type.lower()]
        
        if search_query.founding_year_min:
            candidates = [b for b in candidates if 
                         b.founding_year and b.founding_year >= search_query.founding_year_min]
        
        if search_query.founding_year_max:
            candidates = [b for b in candidates if 
                         b.founding_year and b.founding_year <= search_query.founding_year_max]
        
        if search_query.heritage_score_min:
            candidates = [b for b in candidates if 
                         b.heritage_score and b.heritage_score >= search_query.heritage_score_min]
        
        # Simulate semantic search
        if search_query.query.strip():
            scored_candidates = []
            
            for business in candidates:
                # Calculate relevance score based on RAG weights
                score = 0.0
                query_lower = search_query.query.lower()
                
                # High weight fields (founding_story, cultural_significance)
                if business.founding_story and query_lower in business.founding_story.lower():
                    score += 3.0
                if business.cultural_significance and query_lower in business.cultural_significance.lower():
                    score += 3.0
                if business.community_impact and query_lower in business.community_impact.lower():
                    score += 3.0
                
                # Medium weight fields
                if business.physical_traditions and query_lower in business.physical_traditions.lower():
                    score += 2.0
                if business.historical_significance and query_lower in business.historical_significance.lower():
                    score += 2.0
                
                # Business name gets high weight
                if query_lower in business.business_name.lower():
                    score += 4.0
                
                # Business type gets medium weight
                if query_lower in business.business_type.lower():
                    score += 2.0
                
                # Features and highlights
                for feature in business.unique_features:
                    if query_lower in feature.lower():
                        score += 1.5
                
                for highlight in business.demo_highlights:
                    if query_lower in highlight.lower():
                        score += 1.5
                
                # Simulate vector similarity (cosine similarity)
                if business.business_name in self.vector_embeddings:
                    # In real implementation, would calculate actual cosine similarity
                    vector_similarity = random.uniform(0.1, 0.9)
                    if vector_similarity > search_query.similarity_threshold:
                        score += vector_similarity * 2.0
                
                if score > 0:
                    scored_candidates.append((business, score))
            
            # Sort by relevance score
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            candidates = [business for business, score in scored_candidates]
        
        # Apply pagination
        total_results = len(candidates)
        start_idx = search_query.offset
        end_idx = start_idx + search_query.limit
        results = candidates[start_idx:end_idx]
        
        return {
            "results": results,
            "total": total_results,
            "query": search_query.query,
            "filters_applied": {
                "neighborhood": search_query.neighborhood,
                "business_type": search_query.business_type,
                "founding_year_range": [search_query.founding_year_min, search_query.founding_year_max],
                "heritage_score_min": search_query.heritage_score_min
            },
            "search_metadata": {
                "similarity_threshold": search_query.similarity_threshold,
                "search_fields": search_query.search_fields,
                "semantic_search_enabled": bool(search_query.query.strip())
            }
        }
    
    def get_business_summaries(self, limit: int = 10) -> List[LegacyBusinessSummary]:
        """Get lightweight business summaries for list views"""
        businesses = self.get_businesses(limit)
        
        return [
            LegacyBusinessSummary(
                business_name=b.business_name,
                founding_year=b.founding_year,
                neighborhood=b.neighborhood.value if b.neighborhood else None,
                business_type=b.business_type,
                unique_features=b.unique_features[:3],  # Top 3 features
                demo_highlights=b.demo_highlights[:3],  # Top 3 highlights
                heritage_score=b.heritage_score,
                current_status=b.current_status.value
            )
            for b in businesses
        ]
    
    def get_neighborhoods_with_counts(self) -> Dict[str, int]:
        """Get neighborhood statistics"""
        neighborhood_counts = {}
        
        for business in self.businesses:
            if business.neighborhood:
                neighborhood = business.neighborhood.value
                neighborhood_counts[neighborhood] = neighborhood_counts.get(neighborhood, 0) + 1
        
        return neighborhood_counts
    
    def get_business_types_with_counts(self) -> Dict[str, int]:
        """Get business type statistics"""
        type_counts = {}
        
        for business in self.businesses:
            if business.business_type:
                type_counts[business.business_type] = type_counts.get(business.business_type, 0) + 1
        
        return type_counts
    
    def get_heritage_score_distribution(self) -> Dict[str, int]:
        """Get heritage score distribution for analytics"""
        distribution = {
            "90-100": 0,
            "80-89": 0,
            "70-79": 0,
            "60-69": 0,
            "below-60": 0
        }
        
        for business in self.businesses:
            if business.heritage_score:
                score = business.heritage_score
                if score >= 90:
                    distribution["90-100"] += 1
                elif score >= 80:
                    distribution["80-89"] += 1
                elif score >= 70:
                    distribution["70-79"] += 1
                elif score >= 60:
                    distribution["60-69"] += 1
                else:
                    distribution["below-60"] += 1
        
        return distribution
    
    def simulate_rag_query(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Simulate a RAG query showing how the system would work.
        This demonstrates the foundation for the full RAG implementation.
        """
        
        # Simulate semantic search with embeddings
        search_request = LegacyBusinessSearch(
            query=query,
            limit=max_results,
            similarity_threshold=0.6
        )
        
        search_results = self.search_businesses(search_request)
        
        # Simulate context retrieval for RAG
        contexts = []
        for business in search_results["results"]:
            # Extract relevant context based on RAG weights
            context_parts = []
            
            if business.founding_story:
                context_parts.append(f"Origin: {business.founding_story[:200]}...")
            
            if business.cultural_significance:
                context_parts.append(f"Cultural Impact: {business.cultural_significance[:200]}...")
            
            if business.unique_features:
                context_parts.append(f"Notable Features: {', '.join(business.unique_features[:3])}")
            
            contexts.append({
                "business_name": business.business_name,
                "context": " | ".join(context_parts),
                "heritage_score": business.heritage_score,
                "relevance_score": random.uniform(0.7, 0.95)  # Simulated
            })
        
        # Simulate LLM response generation
        simulated_response = self._generate_simulated_rag_response(query, contexts)
        
        return {
            "query": query,
            "response": simulated_response,
            "source_contexts": contexts,
            "total_businesses_searched": len(self.businesses),
            "relevant_businesses_found": len(search_results["results"]),
            "search_metadata": search_results["search_metadata"]
        }
    
    def _generate_simulated_rag_response(self, query: str, contexts: List[Dict]) -> str:
        """Generate a simulated RAG response for demonstration"""
        
        if not contexts:
            return f"I couldn't find specific information about '{query}' in the legacy business database."
        
        business_names = [c["business_name"] for c in contexts]
        
        if "traditional" in query.lower() or "authentic" in query.lower():
            return f"Based on the legacy business registry, several businesses exemplify traditional practices: {', '.join(business_names[:3])}. These establishments have maintained authentic cultural traditions for decades, with heritage scores ranging from {min(c['heritage_score'] for c in contexts if c['heritage_score'])} to {max(c['heritage_score'] for c in contexts if c['heritage_score'])}."
        
        elif "food" in query.lower() or "restaurant" in query.lower():
            food_businesses = [c for c in contexts if "food" in c["context"].lower() or "restaurant" in c["context"].lower()]
            if food_businesses:
                return f"The legacy food establishments in San Francisco include {', '.join([fb['business_name'] for fb in food_businesses])}. These businesses represent generations of culinary tradition and community gathering spaces."
        
        elif "history" in query.lower() or "historic" in query.lower():
            return f"Several historic businesses match your query: {', '.join(business_names)}. These establishments have witnessed San Francisco's transformation while maintaining their original character and community connections."
        
        else:
            return f"I found {len(contexts)} relevant legacy businesses: {', '.join(business_names)}. Each has unique cultural significance and contributes to San Francisco's diverse heritage landscape."

# Global service instance
_enhanced_service = None

def get_enhanced_business_service() -> EnhancedBusinessService:
    """Get or create enhanced business service instance"""
    global _enhanced_service
    
    if _enhanced_service is None:
        _enhanced_service = EnhancedBusinessService()
    
    return _enhanced_service