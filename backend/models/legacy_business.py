"""
Core Pydantic Models for Legacy Business Registry RAG System
===========================================================

Production-ready data models designed for:
- PDF parsing and extraction
- Semantic search and RAG
- Dynamic frontend generation
- Type-safe API responses
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
from enum import Enum

class NeighborhoodEnum(str, Enum):
    """SF neighborhoods with legacy business concentrations"""
    CHINATOWN = "Chinatown"
    MISSION = "Mission District" 
    NORTH_BEACH = "North Beach"
    CASTRO = "Castro"
    HAIGHT_ASHBURY = "Haight-Ashbury"
    SOMA = "SoMa"
    FINANCIAL = "Financial District"
    NOB_HILL = "Nob Hill"
    RICHMOND = "Richmond"
    SUNSET = "Sunset"
    MARINA = "Marina"
    PACIFIC_HEIGHTS = "Pacific Heights"

class ComponentTypeEnum(str, Enum):
    """Frontend component types for dynamic form generation"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    SELECT = "select"
    TAGS = "tags"
    DYNAMIC_LIST = "dynamic_list"
    DATE = "date"
    RICH_TEXT = "rich_text"

class RAGWeightEnum(str, Enum):
    """Importance weights for semantic search ranking"""
    HIGH = "high"      # Primary search fields (founding_story, cultural_significance)
    MEDIUM = "medium"  # Supporting fields (physical_traditions, recognition)
    LOW = "low"        # Metadata fields (addresses, contact info)

class BusinessStatusEnum(str, Enum):
    """Current operational status"""
    ACTIVE = "active"
    CLOSED = "closed"
    RELOCATED = "relocated"
    PENDING_REVIEW = "pending_review"

class LocationHistory(BaseModel):
    """Historical address information"""
    address: str = Field(..., description="Full street address")
    start_year: int = Field(..., ge=1850, le=2024, description="Year business moved to this location")
    end_year: Optional[int] = Field(None, ge=1850, le=2024, description="Year business left this location")
    is_current: bool = Field(default=True, description="Is this the current location")
    
    @validator('end_year')
    def end_after_start(cls, v, values):
        if v and 'start_year' in values and v < values['start_year']:
            raise ValueError('End year must be after start year')
        return v
    
    @property
    def years_display(self) -> str:
        """Human-readable year range"""
        if self.end_year:
            return f"{self.start_year}-{self.end_year}"
        return f"{self.start_year}-present"

class Recognition(BaseModel):
    """Awards, media coverage, and formal recognition"""
    title: str = Field(..., description="Award or recognition name")
    year: Optional[int] = Field(None, ge=1850, le=2024, description="Year received")
    issuer: str = Field(..., description="Organization that granted recognition")
    description: Optional[str] = Field(None, description="Additional details")
    media_type: Optional[str] = Field(None, description="Type of media coverage")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Featured on PBS Cooking Show",
                "year": 2019,
                "issuer": "Public Broadcasting Service",
                "description": "International cooking demonstration",
                "media_type": "television"
            }
        }

class OwnershipHistory(BaseModel):
    """Business ownership and succession information"""
    owner_name: str = Field(..., description="Owner or family name")
    start_year: Optional[int] = Field(None, ge=1850, le=2024)
    end_year: Optional[int] = Field(None, ge=1850, le=2024)
    relationship: Optional[str] = Field(None, description="Relationship to previous owner")
    generation: Optional[int] = Field(None, ge=1, le=10, description="Generation number for family businesses")

class LegacyBusiness(BaseModel):
    """
    Core data model for Legacy Business Registry RAG system.
    
    Designed for comprehensive PDF parsing, semantic search,
    and dynamic frontend generation based on field metadata.
    """
    
    # === CORE IDENTITY ===
    business_name: str = Field(
        ..., 
        title="Business Name",
        description="Official registered business name",
        pdf_extraction_hints=["Business Name:", "THE WOK SHOP", "Application No.:", "business name"],
        frontend_component=ComponentTypeEnum.TEXT,
        rag_weight=RAGWeightEnum.HIGH,
        search_boost=2.0
    )
    
    legal_name: Optional[str] = Field(
        None,
        title="Legal Business Name", 
        description="Legal entity name if different from DBA",
        pdf_extraction_hints=["legal name", "LLC", "Corporation", "incorporated"]
    )
    
    dba_name: Optional[str] = Field(
        None,
        title="DBA Name",
        description="Doing Business As name",
        pdf_extraction_hints=["DBA", "doing business as", "trade name"]
    )
    
    # === TEMPORAL DATA ===
    founding_year: Optional[int] = Field(
        None,
        title="Year Founded",
        description="Year the business was originally established",
        pdf_extraction_hints=["founded", "established", "opened", "START DATE", "since"],
        frontend_component=ComponentTypeEnum.NUMBER,
        ge=1850,
        le=2024,
        rag_weight=RAGWeightEnum.MEDIUM
    )
    
    years_at_current_location: Optional[int] = Field(
        None,
        title="Years at Current Location",
        description="How long at the current address",
        pdf_extraction_hints=["current location", "moved to", "years at"],
        ge=0,
        le=200
    )
    
    # === LOCATION DATA ===
    current_address: Optional[str] = Field(
        None,
        title="Current Address",
        description="Primary business location street address",
        pdf_extraction_hints=["Business Address:", "located at", "Grant Avenue", "address"],
        frontend_component=ComponentTypeEnum.TEXT,
        rag_weight=RAGWeightEnum.LOW
    )
    
    neighborhood: Optional[NeighborhoodEnum] = Field(
        None,
        title="Neighborhood",
        description="San Francisco neighborhood or district",
        pdf_extraction_hints=["District", "neighborhood", "Chinatown", "Mission", "Castro"],
        frontend_component=ComponentTypeEnum.SELECT,
        rag_weight=RAGWeightEnum.MEDIUM
    )
    
    location_history: List[LocationHistory] = Field(
        default_factory=list,
        title="Location History",
        description="Complete history of business addresses",
        pdf_extraction_hints=["moved from", "originally located", "previous location"],
        frontend_component=ComponentTypeEnum.DYNAMIC_LIST
    )
    
    # === BUSINESS CLASSIFICATION ===
    business_type: Optional[str] = Field(
        None,
        title="Business Type",
        description="Primary business category or industry",
        pdf_extraction_hints=["business type", "category", "restaurant", "bookstore", "BUSINESS DESCRIPTION"],
        frontend_component=ComponentTypeEnum.TEXT,
        rag_weight=RAGWeightEnum.MEDIUM,
        examples=["Kitchen Supply Store", "Family Restaurant", "Independent Bookstore", "Traditional Bakery"]
    )
    
    business_category: Optional[str] = Field(
        None,
        title="Legacy Business Category",
        description="Official legacy business registry category",
        pdf_extraction_hints=["category", "classification", "sector"]
    )
    
    # === RICH NARRATIVE CONTENT (High RAG value) ===
    founding_story: Optional[str] = Field(
        None,
        title="Founding Story",
        description="Origin story and early business history",
        pdf_extraction_hints=["CRITERION 1", "founded by", "history", "started", "began"],
        frontend_component=ComponentTypeEnum.TEXTAREA,
        rag_weight=RAGWeightEnum.HIGH,
        search_boost=1.8
    )
    
    cultural_significance: Optional[str] = Field(
        None,
        title="Cultural Significance",
        description="How the business contributes to neighborhood culture and identity",
        pdf_extraction_hints=["CRITERION 2", "cultural", "community", "tradition", "heritage"],
        frontend_component=ComponentTypeEnum.TEXTAREA,
        rag_weight=RAGWeightEnum.HIGH,
        search_boost=1.8
    )
    
    physical_traditions: Optional[str] = Field(
        None,
        title="Physical Features & Traditions",
        description="Unique physical characteristics and traditional practices",
        pdf_extraction_hints=["CRITERION 3", "physical features", "traditions", "decor", "atmosphere"],
        frontend_component=ComponentTypeEnum.TEXTAREA,
        rag_weight=RAGWeightEnum.MEDIUM
    )
    
    community_impact: Optional[str] = Field(
        None,
        title="Community Impact",
        description="Documented community benefits and social contributions",
        pdf_extraction_hints=["community benefit", "serves", "impact", "contributes"],
        frontend_component=ComponentTypeEnum.TEXTAREA,
        rag_weight=RAGWeightEnum.HIGH
    )
    
    historical_significance: Optional[str] = Field(
        None,
        title="Historical Significance", 
        description="Role in historical events or periods",
        pdf_extraction_hints=["historical", "earthquake", "war", "survived", "witnessed"],
        frontend_component=ComponentTypeEnum.TEXTAREA,
        rag_weight=RAGWeightEnum.HIGH
    )
    
    # === STRUCTURED RELATIONSHIP DATA ===
    ownership_history: List[OwnershipHistory] = Field(
        default_factory=list,
        title="Ownership History",
        description="Succession of owners and family generations",
        pdf_extraction_hints=["founded by", "family", "generation", "son", "daughter", "inherited"]
    )
    
    recognition: List[Recognition] = Field(
        default_factory=list,
        title="Awards & Recognition",
        description="Media coverage, awards, and formal recognition",
        pdf_extraction_hints=["featured", "award", "recognition", "certificate", "media"],
        frontend_component=ComponentTypeEnum.DYNAMIC_LIST,
        rag_weight=RAGWeightEnum.MEDIUM
    )
    
    # === DISTINCTIVE FEATURES ===
    unique_features: List[str] = Field(
        default_factory=list,
        title="Unique Features",
        description="What makes this business distinctive and memorable",
        pdf_extraction_hints=["unique", "special", "original", "distinctive", "notable"],
        frontend_component=ComponentTypeEnum.TAGS,
        rag_weight=RAGWeightEnum.MEDIUM,
        examples=["Original 1970s neon sign", "Woks hanging from ceiling", "Hand-painted murals"]
    )
    
    signature_products: List[str] = Field(
        default_factory=list,
        title="Signature Products/Services",
        description="Flagship offerings that define the business",
        pdf_extraction_hints=["specialty", "famous for", "signature", "known for"],
        frontend_component=ComponentTypeEnum.TAGS
    )
    
    # === SEARCH & DISCOVERY ===
    search_tags: List[str] = Field(
        default_factory=list,
        title="Search Tags",
        description="Auto-generated and manual tags for enhanced discoverability",
        auto_generate=True,
        examples=["family-owned", "third-generation", "celebrity-featured", "earthquake-survivor"]
    )
    
    demo_highlights: List[str] = Field(
        default_factory=list,
        title="Demo Talking Points",
        description="Key points for presentations, tours, and media",
        pdf_extraction_hints=["featured on", "internationally known", "famous", "celebrity"],
        frontend_component=ComponentTypeEnum.TAGS,
        max_items=5,
        rag_weight=RAGWeightEnum.MEDIUM
    )
    
    # === OPERATIONAL STATUS ===
    current_status: BusinessStatusEnum = Field(
        default=BusinessStatusEnum.ACTIVE,
        title="Current Status",
        description="Current operational status"
    )
    
    status_notes: Optional[str] = Field(
        None,
        title="Status Notes",
        description="Additional information about current status"
    )
    
    # === APPLICATION METADATA ===
    application_id: Optional[str] = Field(
        None,
        title="Application ID",
        description="Legacy Business Registry application number",
        pdf_extraction_hints=["Application No.:", "LBR-", "Case No.:", "application"],
        example="LBR-2016-17-064"
    )
    
    heritage_score: Optional[int] = Field(
        None,
        title="Heritage Score",
        description="Calculated heritage significance score",
        ge=0,
        le=100
    )
    
    # === TEMPORAL METADATA ===
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_verified: Optional[datetime] = Field(
        None,
        description="When the information was last verified"
    )
    
    # === SOURCE TRACKING ===
    source_documents: List[str] = Field(
        default_factory=list,
        title="Source Documents",
        description="List of source PDFs and documents used for extraction"
    )
    
    extraction_confidence: Optional[float] = Field(
        None,
        title="Extraction Confidence",
        description="Confidence score for automated extraction",
        ge=0.0,
        le=1.0
    )
    
    class Config:
        use_enum_values = True
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "business_name": "The Wok Shop",
                "founding_year": 1972,
                "current_address": "718 Grant Avenue",
                "neighborhood": "Chinatown",
                "business_type": "Kitchen Supply Store",
                "founding_story": "Founded after Nixon's 1972 China trip when Americans became interested in authentic Chinese cooking. Started by importing traditional woks and cooking equipment directly from China.",
                "cultural_significance": "Serves as cultural ambassador teaching wok cooking to international audience. Bridge between traditional Chinese cooking techniques and American home kitchens.",
                "unique_features": ["Original 1970s pagoda neon sign", "Woks hanging from ceiling like roasted ducks", "International shipping to cooking enthusiasts worldwide"],
                "demo_highlights": ["Featured on PBS cooking shows", "International customer base", "50+ years serving SF Chinatown"]
            }
        }
    
    @root_validator(pre=False, skip_on_failure=True)
    def validate_business_data(cls, values):
        """Cross-field validation and data consistency checks"""
        
        # Ensure current location consistency
        current_address = values.get('current_address')
        location_history = values.get('location_history', [])
        
        if current_address and location_history:
            current_locations = [loc for loc in location_history if loc.is_current]
            if current_locations and current_locations[0].address != current_address:
                # Auto-sync current address with location history
                values['current_address'] = current_locations[0].address
        
        return values
    
    @validator('search_tags', pre=True, always=True)
    def generate_search_tags(cls, v, values):
        """Auto-generate search tags based on other fields"""
        tags = set(v) if v else set()
        
        # Add temporal tags
        founding_year = values.get('founding_year')
        if founding_year:
            if founding_year < 1900:
                tags.add("19th-century")
            elif founding_year < 1950:
                tags.add("early-20th-century")
            else:
                tags.add("mid-century")
            
            # Age-based tags
            current_year = datetime.now().year
            age = current_year - founding_year
            if age > 100:
                tags.add("century-old")
            elif age > 75:
                tags.add("historic")
            elif age > 50:
                tags.add("established")
        
        # Add content-based tags
        founding_story = values.get('founding_story', '').lower()
        if 'family' in founding_story:
            tags.add("family-owned")
        if 'immigrant' in founding_story:
            tags.add("immigrant-founded")
        
        # Recognition-based tags
        recognition = values.get('recognition', [])
        if recognition:
            tags.add("award-winning")
            
        # Neighborhood heritage tags
        neighborhood = values.get('neighborhood')
        if neighborhood:
            tags.add(f"{neighborhood.lower().replace(' ', '-')}-heritage")
        
        return list(tags)

class LegacyBusinessSummary(BaseModel):
    """Lightweight model for search results and list views"""
    business_name: str
    founding_year: Optional[int]
    neighborhood: Optional[str]
    business_type: Optional[str]
    unique_features: List[str] = Field(default_factory=list)
    demo_highlights: List[str] = Field(default_factory=list)
    heritage_score: Optional[int]
    current_status: Optional[str]

class LegacyBusinessSearch(BaseModel):
    """Search query model with advanced filtering"""
    query: str = Field(..., description="Full text search query")
    
    # Geographic filters
    neighborhood: Optional[NeighborhoodEnum] = None
    neighborhoods: List[NeighborhoodEnum] = Field(default_factory=list)
    
    # Temporal filters
    founding_year_min: Optional[int] = Field(None, ge=1850, le=2024)
    founding_year_max: Optional[int] = Field(None, ge=1850, le=2024)
    
    # Business filters
    business_type: Optional[str] = None
    business_types: List[str] = Field(default_factory=list)
    current_status: Optional[BusinessStatusEnum] = None
    
    # Content filters
    tags: List[str] = Field(default_factory=list)
    has_recognition: Optional[bool] = None
    heritage_score_min: Optional[int] = Field(None, ge=0, le=100)
    
    # Search behavior
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    include_inactive: bool = Field(default=False)
    
    # Semantic search options
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    search_fields: List[str] = Field(
        default_factory=lambda: ["founding_story", "cultural_significance", "business_name"],
        description="Fields to include in semantic search"
    )

class ExtractionMetadata(BaseModel):
    """Metadata for PDF extraction results"""
    source_file: str
    extraction_timestamp: datetime
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    extracted_fields: List[str] = Field(default_factory=list)
    processing_time_seconds: float
    extraction_method: str = "llama_parse"

class LegacyBusinessExtracted(LegacyBusiness):
    """Extended model including extraction metadata"""
    extraction_metadata: Optional[ExtractionMetadata] = None
    raw_extracted_text: Optional[str] = Field(
        None,
        description="Raw text extracted from PDF before structuring"
    )