"""
PDF Processing Service with LlamaParse Integration
=================================================

Adapts the legacy-pdf-to-site LlamaParse implementation to work with our 
LegacyBusiness data model. Provides PDF processing functionality with 
automatic mock/live mode detection.
"""

import os
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from pydantic import ValidationError

# LlamaIndex imports
from llama_index.core import SimpleDirectoryReader, Document
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.prompts import PromptTemplate

# Conditional imports for live mode - prioritize OpenAI
try:
    from llama_parse import LlamaParse
    LLAMAPARSE_AVAILABLE = True
except ImportError:
    LLAMAPARSE_AVAILABLE = False

try:
    from llama_index.llms.openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# FriendliAI removed due to dependency conflicts
FRIENDLI_AVAILABLE = False

# Live mode is available if we have at least OpenAI
LIVE_IMPORTS_AVAILABLE = OPENAI_AVAILABLE and LLAMAPARSE_AVAILABLE

# Local imports
from models.legacy_business import LegacyBusiness, LegacyBusinessExtracted, ExtractionMetadata

logger = logging.getLogger(__name__)


class PDFProcessingService:
    """
    PDF processing service with automatic mock/live mode detection.
    
    Features:
    - Automatic mode detection based on API key availability
    - Mock mode with realistic data for testing and demos
    - Live mode with LlamaIndex + LlamaParse + OpenAI integration
    - Quality scoring and validation
    - Error handling and fallback mechanisms
    """
    
    def __init__(self, mock_mode: Optional[bool] = None):
        """
        Initialize PDF processing service.
        
        Args:
            mock_mode: Force mock mode (None for auto-detection)
        """
        # Detect processing mode
        self.mock_mode = mock_mode if mock_mode is not None else self._detect_mock_mode()
        
        # Initialize components based on mode
        self.llm = None
        self.llamaparse = None
        self.extraction_program = None
        
        # Processing configuration
        self.processing_timeout = int(os.getenv('PDF_PROCESSING_TIMEOUT', '120'))
        self.data_quality_threshold = float(os.getenv('DATA_QUALITY_THRESHOLD', '0.7'))
        
        # Setup based on mode
        if self.mock_mode:
            logger.info("🎭 PDFProcessingService initialized in MOCK mode")
            self._setup_mock_mode()
        else:
            logger.info("🚀 PDFProcessingService initialized in LIVE mode")
            self._setup_live_mode()
    
    def _detect_mock_mode(self) -> bool:
        """Detect if we should run in mock mode."""
        # Check for explicit mock mode
        if os.getenv('MOCK_MODE', '').lower() in ('true', '1', 'yes'):
            logger.info("🎭 Mock mode explicitly enabled via MOCK_MODE")
            return True
        
        # Check for required API keys
        llamaparse_key = os.getenv('LLAMA_CLOUD_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        # Check if we have required dependencies
        if not LIVE_IMPORTS_AVAILABLE:
            logger.info("🎭 LlamaParse/OpenAI imports not available - enabling mock mode")
            return True
        
        # Check if we have at least one LLM provider and LlamaParse
        has_llm = bool(openai_key)
        has_llamaparse = bool(llamaparse_key)
        
        if not has_llm:
            logger.info("🎭 No OpenAI API key detected - enabling mock mode")
            return True
        
        if not has_llamaparse:
            logger.info("🎭 No LlamaParse API key detected - enabling mock mode")
            return True
        
        # We have required API keys available
        logger.info("🚀 API keys detected - enabling live mode")
        return False
    
    def _setup_mock_mode(self):
        """Setup mock mode components."""
        logger.info("🎭 Setting up mock mode PDF processing")
        
        # Mock components will be created on-demand
        self.mock_businesses = self._load_mock_business_data()
        
        logger.info(f"✅ Mock mode ready with {len(self.mock_businesses)} sample businesses")
    
    def _setup_live_mode(self):
        """Setup live mode components with real API integration."""
        try:
            logger.info("🚀 Setting up live mode PDF processing")
            
            # Initialize LLM (prefer OpenAI)
            self.llm = self._initialize_llm()
            
            # Initialize LlamaParse
            self.llamaparse = self._initialize_llamaparse()
            
            # Create extraction program
            self._create_extraction_program()
            
            logger.info("✅ Live mode PDF processing ready")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup live mode: {e}")
            logger.info("🎭 Falling back to mock mode")
            self.mock_mode = True
            self._setup_mock_mode()
    
    def _initialize_llm(self):
        """Initialize LLM with preference for OpenAI.""" 
        if not LIVE_IMPORTS_AVAILABLE:
            raise Exception("OpenAI imports not available")
            
        # Use OpenAI as primary
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and OPENAI_AVAILABLE:
            try:
                logger.info("🤖 Initializing OpenAI LLM")
                return OpenAI(
                    model="gpt-4o",
                    temperature=0.0,
                    api_key=openai_key
                )
            except Exception as e:
                logger.error(f"❌ OpenAI initialization failed: {e}")
        
        raise Exception("No LLM providers available (OpenAI required)")
    
    def _initialize_llamaparse(self):
        """Initialize LlamaParse for advanced PDF processing."""
        llamaparse_key = os.getenv('LLAMA_CLOUD_API_KEY')
        if not llamaparse_key:
            raise Exception("LlamaParse API key required for live mode")
        
        try:
            logger.info("📄 Initializing LlamaParse")
            return LlamaParse(
                api_key=llamaparse_key,
                result_type="markdown",  # Better for structured extraction
                verbose=True,
                language="en"
            )
        except Exception as e:
            logger.error(f"❌ LlamaParse initialization failed: {e}")
            raise
    
    def _create_extraction_program(self):
        """Create LlamaIndex extraction program."""
        if not self.llm:
            return
        
        extraction_prompt = self._get_extraction_prompt()
        
        try:
            self.extraction_program = LLMTextCompletionProgram.from_defaults(
                output_cls=LegacyBusiness,
                llm=self.llm,
                prompt_template_str=extraction_prompt,
                verbose=True
            )
            logger.info("✅ Extraction program created")
        except Exception as e:
            logger.error(f"❌ Failed to create extraction program: {e}")
            raise
    
    def _get_extraction_prompt(self) -> str:
        """Get the extraction prompt template adapted for our LegacyBusiness model."""
        return """
You are an expert at extracting structured information from San Francisco Legacy Business PDF applications.

Please carefully analyze the following PDF content and extract detailed information to create a comprehensive business profile using our specific data model. Pay special attention to heritage stories, community impact, and unique characteristics.

PDF Content:
{pdf_content}

Instructions:
1. Extract the business_name accurately (look for "Business Name:", "THE WOK SHOP", etc.)
2. Find founding_year (look for "founded", "established", "opened", "since", etc.)
3. Extract current_address and neighborhood information
4. Identify business_type/business_category
5. Create rich narratives for:
   - founding_story (2-3 paragraphs minimum, from CRITERION 1 sections)
   - cultural_significance (how it contributes to neighborhood culture, CRITERION 2)
   - physical_traditions (unique features and traditions, CRITERION 3)
   - community_impact (documented community benefits)
   - historical_significance (role in historical events)
6. Look for ownership_history (family generations, successions)
7. Find recognition/awards (media coverage, certificates, features)
8. Identify unique_features and signature_products
9. Extract application_id if mentioned (LBR-2016-17-064 format)

Focus on creating content that:
- Tells the heritage story in an engaging way
- Highlights community connections and impact
- Captures what makes this business unique and special
- Preserves the historical and cultural significance
- Would be compelling for visitors and researchers

Be thorough but accurate. If information isn't clearly stated in the PDF, use null/empty values rather than guessing.

Return the structured data following the LegacyBusiness model schema.
"""
    
    def _load_mock_business_data(self) -> Dict[str, Dict[str, Any]]:
        """Load mock business data adapted to our model using real sample PDFs."""
        return {
            "el-faro": {
                "url_pattern": "el_faro",
                "data": {
                    "business_name": "El Faro Restaurant",
                    "founding_year": 1961,
                    "current_address": "2399 Folsom St, San Francisco, CA 94110",
                    "neighborhood": "Mission District",
                    "business_type": "Mexican Restaurant",
                    "founding_story": "El Faro Restaurant was established in 1961 by the Guerrero family, who immigrated from Mexico seeking to share authentic Mexican cuisine with San Francisco. The restaurant became a cornerstone of the Mission District's vibrant Latino community, serving traditional dishes passed down through generations.",
                    "cultural_significance": "El Faro has been a cultural anchor in the Mission District for over six decades, preserving Mexican culinary traditions and serving as a gathering place for the Latino community. The restaurant has maintained its authentic character while witnessing the neighborhood's transformation.",
                    "physical_traditions": "The restaurant features traditional Mexican decor with hand-painted murals depicting scenes from Mexico, colorful papel picado banners, and a classic Mexican tile bar. The kitchen uses traditional cooking methods including wood-fired preparation techniques.",
                    "community_impact": "Beyond serving food, El Faro has supported community events, hosted cultural celebrations, and provided employment opportunities for generations of Mission District residents. The restaurant has been a safe haven and community center during neighborhood changes.",
                    "unique_features": ["Traditional wood-fired cooking", "Hand-painted Mexican murals", "Original 1960s interior", "Family recipes"],
                    "signature_products": ["Authentic tacos", "Traditional mole", "Fresh salsas", "Mexican seafood"],
                    "demo_highlights": ["60+ years in Mission District", "Family-owned since 1961", "Traditional Mexican cooking", "Community cultural center"],
                    "application_id": "LBR-2016-17-045",
                    "extraction_confidence": 0.90
                }
            },
            "original-joes": {
                "url_pattern": "original_joes",
                "data": {
                    "business_name": "Original Joe's",
                    "founding_year": 1937,
                    "current_address": "601 Union St, San Francisco, CA 94133",
                    "neighborhood": "North Beach",
                    "business_type": "Italian-American Restaurant",
                    "founding_story": "Original Joe's was founded in 1937 by Tony Rodinelli in the Tenderloin district of San Francisco. The restaurant became famous for its open kitchen concept where customers could watch chefs prepare meals on a large grill visible from the dining room. This transparency and showmanship became a hallmark of the Original Joe's experience.",
                    "cultural_significance": "Original Joe's represents classic American dining culture of the mid-20th century, maintaining the tradition of counter service, open kitchens, and hearty comfort food. The restaurant has been a gathering place for locals, celebrities, and visitors seeking an authentic San Francisco dining experience.",
                    "physical_traditions": "The restaurant features the iconic open kitchen with a large grill where all cooking is done in full view of customers. Red vinyl booths, classic bar stools, and vintage signage maintain the authentic 1950s American diner atmosphere.",
                    "community_impact": "Original Joe's has been a North Beach institution, providing employment for generations of San Francisco residents and serving as a meeting place for the local community. The restaurant has maintained its commitment to quality and tradition through multiple ownership changes.",
                    "unique_features": ["Open kitchen concept", "Visible cooking grill", "Red vinyl booths", "Classic counter service"],
                    "signature_products": ["Joe's Special (scrambled eggs with ground beef and spinach)", "Steaks", "Classic cocktails", "American comfort food"],
                    "demo_highlights": ["SF institution since 1937", "Famous open kitchen", "Celebrity dining history", "Classic American cuisine"],
                    "application_id": "LBR-2015-16-023",
                    "extraction_confidence": 0.88
                }
            }
        }
    
    async def process_pdf_url(self, pdf_url: str, store_metadata: bool = True) -> Dict[str, Any]:
        """
        Process PDF from URL and return structured business data.
        
        Args:
            pdf_url: URL to the PDF document
            store_metadata: Whether to include extraction metadata
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        
        try:
            logger.info(f"📄 Processing PDF: {pdf_url}")
            
            if self.mock_mode:
                result = await self._process_pdf_mock_mode(pdf_url)
            else:
                result = await self._process_pdf_live_mode(pdf_url, store_metadata)
            
            processing_time = time.time() - start_time
            result["processing_time_seconds"] = round(processing_time, 2)
            
            logger.info(f"✅ PDF processing completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ PDF processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "mode": "mock" if self.mock_mode else "live",
                "processing_time_seconds": round(processing_time, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _process_pdf_mock_mode(self, pdf_url: str) -> Dict[str, Any]:
        """Process PDF in mock mode with realistic data."""
        logger.info("🎭 Processing PDF in mock mode")
        
        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        # Find matching mock business based on URL pattern
        mock_business = None
        for business_id, business_info in self.mock_businesses.items():
            if business_info["url_pattern"] in pdf_url.lower():
                mock_business = business_info["data"].copy()
                break
        
        # Also check for local sample PDFs
        if not mock_business:
            if "el_faro" in pdf_url.lower():
                mock_business = self.mock_businesses["el-faro"]["data"].copy()
            elif "original_joes" in pdf_url.lower():
                mock_business = self.mock_businesses["original-joes"]["data"].copy()
        
        # Use generic mock data if no specific match
        if not mock_business:
            mock_business = {
                "business_name": "Sample Legacy Business",
                "founding_year": 1950,
                "current_address": "123 Sample St, San Francisco, CA 94100",
                "neighborhood": "Mission District",
                "business_type": "Retail Store",
                "founding_story": "This sample business was established in 1950 by a local entrepreneur who saw a need in the community. The business has served the neighborhood for decades, building strong relationships with customers and contributing to the local economy.",
                "cultural_significance": "This business represents the entrepreneurial spirit of San Francisco and serves as a cornerstone of the local community.",
                "unique_features": ["Historic building", "Community focus", "Local institution"],
                "signature_products": ["Sample products"],
                "demo_highlights": ["San Francisco Legacy Business", "Community cornerstone"],
                "extraction_confidence": 0.75
            }
        
        # Add metadata
        mock_business.update({
            "source_documents": [pdf_url],
            "created_at": datetime.utcnow(),
            "last_verified": datetime.utcnow()
        })
        
        # Create LegacyBusiness object for validation
        try:
            business_obj = LegacyBusiness(**mock_business)
            business_dict = business_obj.model_dump()
        except ValidationError as e:
            logger.error(f"❌ Mock data validation failed: {e}")
            # Return basic structure on validation failure
            business_dict = mock_business
        
        return {
            "success": True,
            "mode": "mock",
            "business": business_dict,
            "timestamp": datetime.utcnow().isoformat(),
            "quality_score": business_dict.get("extraction_confidence", 0.75)
        }
    
    async def _process_pdf_live_mode(self, pdf_url: str, store_metadata: bool) -> Dict[str, Any]:
        """Process PDF in live mode with real API calls."""
        logger.info("🚀 Processing PDF in live mode")
        
        if not self.extraction_program:
            raise Exception("Extraction program not initialized")
        
        # Load PDF content
        pdf_content = await self._load_pdf_content(pdf_url)
        if not pdf_content:
            raise Exception("Failed to load PDF content")
        
        # Extract structured data
        business_data = await self._extract_structured_data(pdf_content, pdf_url, store_metadata)
        
        return {
            "success": True,
            "mode": "live",
            "business": business_data.model_dump(),
            "timestamp": datetime.utcnow().isoformat(),
            "quality_score": business_data.extraction_confidence or 0.0
        }
    
    async def _load_pdf_content(self, pdf_url: str) -> Optional[str]:
        """Load PDF content using LlamaParse."""
        try:
            if self.llamaparse:
                # Use LlamaParse for advanced processing
                logger.info("📄 Using LlamaParse for PDF processing")
                documents = await self.llamaparse.aload_data([pdf_url])
                
                if documents:
                    return "\n\n".join([doc.text for doc in documents if doc.text])
            
            raise Exception("LlamaParse not available")
            
        except Exception as e:
            logger.error(f"❌ Error loading PDF content: {e}")
            return None
    
    async def _extract_structured_data(self, pdf_content: str, pdf_url: str, store_metadata: bool) -> LegacyBusiness:
        """Extract structured data using LLM."""
        try:
            logger.info("🧠 Extracting structured data with LLM")
            
            # Run extraction program
            extracted_data = self.extraction_program(pdf_content=pdf_content)
            
            # Add metadata
            extracted_data.source_documents = [pdf_url]
            extracted_data.created_at = datetime.utcnow()
            extracted_data.last_verified = datetime.utcnow()
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(extracted_data)
            extracted_data.extraction_confidence = quality_score
            
            logger.info(f"✨ Extracted: {extracted_data.business_name} (Quality: {quality_score:.2f})")
            
            # Add extraction metadata if requested
            if store_metadata:
                extraction_metadata = ExtractionMetadata(
                    source_file=pdf_url,
                    extraction_timestamp=datetime.utcnow(),
                    confidence_scores={"overall": quality_score},
                    extracted_fields=self._get_populated_fields(extracted_data),
                    processing_time_seconds=0.0,  # Will be set later
                    extraction_method="llama_parse_openai"
                )
                
                # Return enhanced model with metadata
                return LegacyBusinessExtracted(
                    **extracted_data.model_dump(),
                    extraction_metadata=extraction_metadata,
                    raw_extracted_text=pdf_content[:1000] + "..." if len(pdf_content) > 1000 else pdf_content
                )
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"❌ Structured extraction failed: {e}")
            raise
    
    def _calculate_quality_score(self, business: LegacyBusiness) -> float:
        """Calculate data quality score based on completeness."""
        score = 0.0
        max_score = 0.0
        
        # Core fields (40% of score)
        core_fields = [
            (business.business_name, 0.15),
            (business.founding_year, 0.1),
            (business.business_type, 0.1),
            (business.current_address, 0.05)
        ]
        
        for field_value, weight in core_fields:
            max_score += weight
            if field_value and str(field_value).strip():
                score += weight
        
        # Rich content fields (50% of score)
        content_fields = [
            (business.founding_story, 0.2, 100),
            (business.cultural_significance, 0.15, 50),
            (business.community_impact, 0.1, 50),
            (business.physical_traditions, 0.05, 30)
        ]
        
        for field_value, weight, min_length in content_fields:
            max_score += weight
            if field_value and len(field_value.strip()) >= min_length:
                score += weight
        
        # List fields (10% of score)
        list_fields = [
            (business.unique_features, 0.03),
            (business.signature_products, 0.03),
            (business.demo_highlights, 0.02),
            (business.recognition, 0.02)
        ]
        
        for field_list, weight in list_fields:
            max_score += weight
            if field_list and len(field_list) > 0:
                score += weight
        
        final_score = score / max_score if max_score > 0 else 0.0
        return round(min(1.0, max(0.0, final_score)), 2)
    
    def _get_populated_fields(self, business: LegacyBusiness) -> List[str]:
        """Get list of fields that have data."""
        populated = []
        
        for field_name, field_info in business.__fields__.items():
            value = getattr(business, field_name, None)
            if value is not None:
                if isinstance(value, str) and value.strip():
                    populated.append(field_name)
                elif isinstance(value, list) and len(value) > 0:
                    populated.append(field_name)
                elif not isinstance(value, (str, list)):
                    populated.append(field_name)
        
        return populated
    
    async def batch_process_pdfs(self, pdf_urls: List[str]) -> Dict[str, Any]:
        """
        Process multiple PDFs in batch.
        
        Args:
            pdf_urls: List of PDF URLs to process
            
        Returns:
            Dictionary with batch processing results
        """
        logger.info(f"📦 Starting batch processing of {len(pdf_urls)} PDFs")
        start_time = time.time()
        
        results = []
        successful = 0
        failed = 0
        
        for i, pdf_url in enumerate(pdf_urls, 1):
            logger.info(f"📄 Processing PDF {i}/{len(pdf_urls)}: {pdf_url}")
            
            try:
                result = await self.process_pdf_url(pdf_url)
                results.append(result)
                
                if result.get("success"):
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"❌ Failed to process PDF {pdf_url}: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "pdf_url": pdf_url
                })
                failed += 1
        
        total_time = time.time() - start_time
        
        return {
            "success": True,
            "mode": "mock" if self.mock_mode else "live",
            "total_processed": len(pdf_urls),
            "successful": successful,
            "failed": failed,
            "processing_time_seconds": round(total_time, 2),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status and configuration."""
        return {
            "mode": "mock" if self.mock_mode else "live",
            "components": {
                "llm_available": self.llm is not None,
                "llamaparse_available": self.llamaparse is not None,
                "extraction_program_ready": self.extraction_program is not None
            },
            "configuration": {
                "processing_timeout": self.processing_timeout,
                "quality_threshold": self.data_quality_threshold,
                "mock_businesses_available": len(self.mock_businesses) if self.mock_mode else 0
            },
            "api_keys_detected": {
                "llama_cloud": bool(os.getenv('LLAMA_CLOUD_API_KEY')),
                "openai": bool(os.getenv('OPENAI_API_KEY')),
                "friendli": bool(os.getenv('FRIENDLI_API_KEY'))
            },
            "dependencies_available": {
                "llamaparse": LLAMAPARSE_AVAILABLE,
                "openai": OPENAI_AVAILABLE,
                "friendli": FRIENDLI_AVAILABLE
            }
        }


# Global service instance (initialized on first import)
_pdf_service_instance = None

def get_pdf_service(mock_mode: Optional[bool] = None) -> PDFProcessingService:
    """Get or create PDF service instance."""
    global _pdf_service_instance
    
    if _pdf_service_instance is None:
        _pdf_service_instance = PDFProcessingService(mock_mode=mock_mode)
    
    return _pdf_service_instance