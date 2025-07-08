#!/usr/bin/env python3
"""
Weaviate Schema Migration Script for Legacy Business Registry
============================================================

Creates and configures Weaviate schema optimized for our LegacyBusiness data model.
Includes proper vectorization settings, performance optimization, and validation.

Usage:
    python scripts/setup_weaviate_schema.py [--reset] [--validate-only]
"""

import os
import sys
import time
import json
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    import weaviate
    from weaviate.classes.config import Configure, Property, DataType
    from weaviate.classes.init import Auth
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    print("⚠️  Weaviate client not available. Install with: uv add weaviate-client")

from models.legacy_business import LegacyBusiness, NeighborhoodEnum, BusinessStatusEnum


class WeaviateSchemaSetup:
    """Handles Weaviate schema creation and validation for LegacyBusiness model"""
    
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        self.url = url or os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.api_key = api_key or os.getenv("WEAVIATE_API_KEY")
        self.client = None
        self.collection_name = "LegacyBusiness"
        
    def connect(self) -> bool:
        """Establish connection to Weaviate"""
        if not WEAVIATE_AVAILABLE:
            print("❌ Weaviate client library not available")
            return False
            
        try:
            auth = Auth.api_key(self.api_key) if self.api_key else None
            self.client = weaviate.connect_to_custom(
                http_host=self.url.replace("http://", "").replace("https://", ""),
                http_port=8080,  # Default Weaviate port
                http_secure=self.url.startswith("https://"),
                auth=auth
            )
            
            # Test connection
            if self.client.is_ready():
                print(f"✅ Connected to Weaviate at {self.url}")
                return True
            else:
                print(f"❌ Weaviate not ready at {self.url}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to connect to Weaviate: {e}")
            return False
    
    def get_legacy_business_schema(self) -> Dict[str, Any]:
        """
        Generate Weaviate schema for LegacyBusiness model.
        Optimized for semantic search with proper vectorization settings.
        """
        return {
            "class": self.collection_name,
            "description": "San Francisco Legacy Business Registry with rich narrative content for semantic search",
            "vectorizer": "text2vec-openai",  # Requires OpenAI API key
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "text-embedding-3-small",  # Latest, cost-effective model
                    "dimensions": 1536,  # Standard dimension for this model
                    "type": "text",
                    "vectorizeClassName": False  # Don't vectorize class name
                }
            },
            "properties": [
                # === CORE IDENTITY === (Medium vectorization weight)
                {
                    "name": "business_name",
                    "dataType": ["text"],
                    "description": "Official business name - primary identifier",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": False, "vectorizePropertyName": False}
                    }
                },
                {
                    "name": "legal_name", 
                    "dataType": ["text"],
                    "description": "Legal entity name if different from DBA",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": True}  # Skip vectorization for legal metadata
                    }
                },
                {
                    "name": "dba_name",
                    "dataType": ["text"], 
                    "description": "Doing Business As name",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": True}
                    }
                },
                
                # === TEMPORAL DATA === (Structured, no vectorization)
                {
                    "name": "founding_year",
                    "dataType": ["int"],
                    "description": "Year the business was established",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": True}
                    }
                },
                {
                    "name": "years_at_current_location", 
                    "dataType": ["int"],
                    "description": "Years at current address",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": True}
                    }
                },
                
                # === LOCATION DATA === (Mixed vectorization)
                {
                    "name": "current_address",
                    "dataType": ["text"],
                    "description": "Current street address",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": True}  # Skip - not semantically meaningful
                    }
                },
                {
                    "name": "neighborhood",
                    "dataType": ["text"],
                    "description": "San Francisco neighborhood",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": False}  # Include - culturally significant
                    }
                },
                
                # === BUSINESS CLASSIFICATION === (Medium vectorization)
                {
                    "name": "business_type",
                    "dataType": ["text"],
                    "description": "Primary business category",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": False}
                    }
                },
                {
                    "name": "business_category",
                    "dataType": ["text"],
                    "description": "Official legacy business category",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": False}
                    }
                },
                
                # === RICH NARRATIVE CONTENT === (HIGH vectorization priority)
                {
                    "name": "founding_story",
                    "dataType": ["text"],
                    "description": "Origin story and early history - PRIMARY SEARCH CONTENT",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": False, "vectorizePropertyName": False}
                    }
                },
                {
                    "name": "cultural_significance", 
                    "dataType": ["text"],
                    "description": "Cultural contribution to neighborhood - PRIMARY SEARCH CONTENT",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": False, "vectorizePropertyName": False}
                    }
                },
                {
                    "name": "physical_traditions",
                    "dataType": ["text"],
                    "description": "Physical features and traditional practices",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": False}
                    }
                },
                {
                    "name": "community_impact",
                    "dataType": ["text"], 
                    "description": "Community benefits and social contributions",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": False}
                    }
                },
                {
                    "name": "historical_significance",
                    "dataType": ["text"],
                    "description": "Role in historical events",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": False}
                    }
                },
                
                # === DISTINCTIVE FEATURES === (Arrays for flexible search)
                {
                    "name": "unique_features",
                    "dataType": ["text[]"],
                    "description": "Distinctive and memorable characteristics",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": False}
                    }
                },
                {
                    "name": "signature_products",
                    "dataType": ["text[]"],
                    "description": "Flagship products and services",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": False}
                    }
                },
                {
                    "name": "demo_highlights",
                    "dataType": ["text[]"],
                    "description": "Key talking points for presentations",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": False}
                    }
                },
                
                # === SEARCH METADATA === (Mixed)
                {
                    "name": "search_tags",
                    "dataType": ["text[]"],
                    "description": "Generated and manual search tags",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": False}
                    }
                },
                
                # === OPERATIONAL STATUS === (Structured, no vectorization)
                {
                    "name": "current_status",
                    "dataType": ["text"],
                    "description": "Current operational status",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": True}
                    }
                },
                {
                    "name": "status_notes",
                    "dataType": ["text"],
                    "description": "Additional status information",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": True}
                    }
                },
                
                # === METADATA === (No vectorization - for filtering only)
                {
                    "name": "application_id",
                    "dataType": ["text"],
                    "description": "Legacy Business Registry application ID",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": True}
                    }
                },
                {
                    "name": "heritage_score",
                    "dataType": ["int"],
                    "description": "Calculated heritage significance score (0-100)",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": True}
                    }
                },
                {
                    "name": "extraction_confidence",
                    "dataType": ["number"],
                    "description": "PDF extraction confidence score",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": True}
                    }
                },
                
                # === TEMPORAL METADATA === (No vectorization)
                {
                    "name": "created_at",
                    "dataType": ["date"],
                    "description": "Record creation timestamp",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": True}
                    }
                },
                {
                    "name": "updated_at",
                    "dataType": ["date"],
                    "description": "Last update timestamp", 
                    "moduleConfig": {
                        "text2vec-openai": {"skip": True}
                    }
                },
                {
                    "name": "last_verified",
                    "dataType": ["date"],
                    "description": "Last verification timestamp",
                    "moduleConfig": {
                        "text2vec-openai": {"skip": True}
                    }
                }
            ]
        }
    
    def create_schema(self, reset: bool = False) -> bool:
        """Create the LegacyBusiness schema in Weaviate"""
        if not self.client:
            print("❌ No Weaviate connection")
            return False
            
        try:
            # Check if collection exists
            collections = self.client.collections.list_all()
            collection_exists = self.collection_name in [c.name for c in collections]
            
            if collection_exists:
                if reset:
                    print(f"🗑️  Deleting existing {self.collection_name} collection...")
                    self.client.collections.delete(self.collection_name)
                    time.sleep(2)  # Wait for deletion to complete
                else:
                    print(f"✅ Collection {self.collection_name} already exists (use --reset to recreate)")
                    return True
            
            # Create new collection
            print(f"🏗️  Creating {self.collection_name} collection...")
            schema = self.get_legacy_business_schema()
            
            collection = self.client.collections.create_from_dict(schema)
            
            if collection:
                print(f"✅ Successfully created {self.collection_name} collection")
                return True
            else:
                print(f"❌ Failed to create {self.collection_name} collection")
                return False
                
        except Exception as e:
            print(f"❌ Schema creation failed: {e}")
            return False
    
    def validate_schema(self) -> bool:
        """Validate the created schema matches our expectations"""
        if not self.client:
            print("❌ No Weaviate connection")
            return False
            
        try:
            collection = self.client.collections.get(self.collection_name)
            config = collection.config.get()
            
            print(f"📋 Validating {self.collection_name} schema...")
            
            # Check vectorizer configuration
            vectorizer = config.vectorizer_config
            if vectorizer and hasattr(vectorizer, 'vectorizer'):
                print(f"  ✅ Vectorizer: {vectorizer.vectorizer}")
            else:
                print("  ⚠️  No vectorizer configured")
            
            # Check properties
            properties = config.properties
            expected_props = [
                "business_name", "founding_story", "cultural_significance",
                "neighborhood", "business_type", "founding_year"
            ]
            
            existing_props = [prop.name for prop in properties]
            missing_props = [prop for prop in expected_props if prop not in existing_props]
            
            if missing_props:
                print(f"  ❌ Missing properties: {missing_props}")
                return False
            else:
                print(f"  ✅ All {len(properties)} properties configured")
            
            # Check vectorization settings for key fields
            key_vectorized_fields = ["founding_story", "cultural_significance", "business_name"]
            for prop in properties:
                if prop.name in key_vectorized_fields:
                    # Check if vectorization is enabled (not skipped)
                    vectorizer_config = getattr(prop, 'vectorizer_config', None)
                    if vectorizer_config and getattr(vectorizer_config, 'skip', False):
                        print(f"  ⚠️  {prop.name} has vectorization disabled")
                    else:
                        print(f"  ✅ {prop.name} vectorization enabled")
            
            print("✅ Schema validation completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Schema validation failed: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the collection"""
        if not self.client:
            return {"error": "No connection"}
            
        try:
            collection = self.client.collections.get(self.collection_name)
            
            # Get object count (this might be 0 if no data inserted yet)
            total_objects = collection.aggregate.over_all(total_count=True).total_count
            
            return {
                "collection_name": self.collection_name,
                "total_objects": total_objects,
                "status": "ready" if total_objects >= 0 else "error"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def insert_sample_data(self) -> bool:
        """Insert sample LegacyBusiness data for testing"""
        if not self.client:
            print("❌ No Weaviate connection")
            return False
            
        try:
            collection = self.client.collections.get(self.collection_name)
            
            # Create sample business based on our model
            sample_business = {
                "business_name": "The Wok Shop",
                "founding_year": 1972,
                "current_address": "718 Grant Avenue",
                "neighborhood": "Chinatown",
                "business_type": "Kitchen Supply Store",
                "founding_story": "Founded after Nixon's 1972 China trip when Americans became interested in authentic Chinese cooking. Started by importing traditional woks and cooking equipment directly from China.",
                "cultural_significance": "Serves as cultural ambassador teaching wok cooking to international audience. Bridge between traditional Chinese cooking techniques and American home kitchens.",
                "physical_traditions": "Original 1970s pagoda-style neon sign. Traditional woks hanging from ceiling like roasted ducks in Chinatown markets.",
                "unique_features": ["Original 1970s pagoda neon sign", "Woks hanging from ceiling", "International shipping worldwide"],
                "signature_products": ["Traditional carbon steel woks", "Bamboo steamers", "Chinese cooking utensils"],
                "demo_highlights": ["Featured on PBS cooking shows", "International customer base", "50+ years serving SF Chinatown"],
                "search_tags": ["family-owned", "chinatown-heritage", "cooking-equipment", "cultural-bridge"],
                "current_status": "active",
                "heritage_score": 92,
                "created_at": "2024-01-01T00:00:00Z"
            }
            
            print("📝 Inserting sample data...")
            result = collection.data.insert(sample_business)
            
            if result:
                print(f"✅ Sample data inserted with UUID: {result}")
                return True
            else:
                print("❌ Failed to insert sample data")
                return False
                
        except Exception as e:
            print(f"❌ Sample data insertion failed: {e}")
            return False
    
    def test_semantic_search(self) -> bool:
        """Test semantic search functionality"""
        if not self.client:
            print("❌ No Weaviate connection")
            return False
            
        try:
            collection = self.client.collections.get(self.collection_name)
            
            print("🔍 Testing semantic search...")
            
            # Test semantic search query
            results = collection.query.near_text(
                query="traditional Chinese cooking equipment",
                limit=5,
                return_metadata=["certainty", "distance"]
            )
            
            if results.objects:
                print(f"✅ Semantic search returned {len(results.objects)} results")
                for obj in results.objects:
                    certainty = obj.metadata.certainty if obj.metadata else "unknown"
                    print(f"  - {obj.properties.get('business_name', 'Unknown')} (certainty: {certainty})")
                return True
            else:
                print("⚠️  Semantic search returned no results (collection may be empty)")
                return True  # Still valid if empty
                
        except Exception as e:
            print(f"❌ Semantic search test failed: {e}")
            return False
    
    def close(self):
        """Close Weaviate connection"""
        if self.client:
            self.client.close()
            print("🔌 Weaviate connection closed")


def main():
    """Main migration script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Weaviate schema for Legacy Business Registry")
    parser.add_argument("--reset", action="store_true", help="Delete existing collection and recreate")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing schema")
    parser.add_argument("--insert-sample", action="store_true", help="Insert sample data for testing")
    parser.add_argument("--url", help="Weaviate URL (default: from WEAVIATE_URL env)")
    parser.add_argument("--api-key", help="Weaviate API key (default: from WEAVIATE_API_KEY env)")
    
    args = parser.parse_args()
    
    print("🚀 Weaviate Schema Setup for Legacy Business Registry")
    print("=" * 60)
    
    # Check environment
    url = args.url or os.getenv("WEAVIATE_URL")
    api_key = args.api_key or os.getenv("WEAVIATE_API_KEY")
    
    if not url:
        print("❌ WEAVIATE_URL not set. Please provide --url or set environment variable.")
        sys.exit(1)
    
    if not api_key:
        print("⚠️  WEAVIATE_API_KEY not set. Attempting connection without authentication.")
    
    # Initialize setup
    setup = WeaviateSchemaSetup(url, api_key)
    
    try:
        # Connect
        if not setup.connect():
            sys.exit(1)
        
        if args.validate_only:
            # Validation only
            if setup.validate_schema():
                stats = setup.get_collection_stats()
                print(f"📊 Collection stats: {stats}")
                print("✅ Validation successful")
            else:
                print("❌ Validation failed")
                sys.exit(1)
        else:
            # Full setup
            if setup.create_schema(reset=args.reset):
                if setup.validate_schema():
                    stats = setup.get_collection_stats()
                    print(f"📊 Collection stats: {stats}")
                    
                    if args.insert_sample:
                        setup.insert_sample_data()
                        setup.test_semantic_search()
                    
                    print("✅ Schema setup completed successfully")
                else:
                    print("❌ Schema validation failed after creation")
                    sys.exit(1)
            else:
                print("❌ Schema creation failed")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n⏹️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        setup.close()


if __name__ == "__main__":
    main()