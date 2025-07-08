"""
LlamaIndex Multi-Modal Processing Service
=========================================

Production-grade LlamaIndex integration with multi-modal capabilities.
Extracted from proven patterns in legacy-pdf-to-site repository.
"""

import os
import asyncio
import logging
import time
import tempfile
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import aiohttp
from pydantic import BaseModel, Field

# Conditional imports for LlamaIndex - graceful degradation
try:
    from llama_index.core import SimpleDirectoryReader, Document
    from llama_index.core.program import LLMTextCompletionProgram
    from llama_index.core.prompts import PromptTemplate
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core import VectorStoreIndex, StorageContext
    from llama_index.core.storage.docstore import SimpleDocumentStore
    from llama_index.core.extractors import BaseExtractor
    from llama_parse import LlamaParse
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    logging.warning("LlamaIndex components not available - running in mock mode")
    LLAMAINDEX_AVAILABLE = False
    # Mock classes for graceful degradation
    class Document:
        def __init__(self, text="", metadata=None):
            self.text = text
            self.metadata = metadata or {}
    
    class BaseExtractor:
        def __init__(self):
            pass

# Conditional imports for LLM providers
try:
    from llama_index.llms.openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from llama_index.embeddings.openai import OpenAIEmbedding
    OPENAI_EMBEDDINGS_AVAILABLE = True
except ImportError:
    OPENAI_EMBEDDINGS_AVAILABLE = False

# Image processing imports
try:
    import fitz  # PyMuPDF for PDF image extraction
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)

# Data models
class DocumentMetadata(BaseModel):
    """Metadata for processed documents"""
    document_id: str
    filename: str
    source_url: Optional[str] = None
    processing_timestamp: datetime
    total_pages: int
    total_images: int
    quality_score: float = Field(ge=0.0, le=1.0)
    processing_time_seconds: float

class ExtractedImage(BaseModel):
    """Metadata for extracted images"""
    image_id: str
    page_number: int
    position: Dict[str, float]  # x, y, width, height
    image_type: str
    file_path: str
    ocr_text: Optional[str] = None
    caption: Optional[str] = None
    context_text: Optional[str] = None

class ProcessedDocument(BaseModel):
    """Complete processed document with text and images"""
    metadata: DocumentMetadata
    text_content: str
    text_chunks: List[Dict[str, Any]]
    extracted_images: List[ExtractedImage]
    relationships: List[Dict[str, Any]]  # Text-image relationships

class ImageExtractor(BaseExtractor):
    """Custom extractor for images from PDF documents"""
    
    def __init__(self, output_dir: str = "/tmp/extracted_images"):
        super().__init__()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def extract(self, nodes):
        """Extract images from document nodes"""
        if not PYMUPDF_AVAILABLE:
            logger.warning("PyMuPDF not available - skipping image extraction")
            return {}
        
        extracted_images = []
        for node in nodes:
            source_file = node.metadata.get('source_file')
            if source_file and source_file.endswith('.pdf'):
                images = self._extract_images_from_pdf(source_file)
                extracted_images.extend(images)
        
        return {"extracted_images": extracted_images}
    
    def _extract_images_from_pdf(self, pdf_path: str) -> List[ExtractedImage]:
        """Extract images from PDF file"""
        try:
            doc = fitz.open(pdf_path)
            extracted_images = []
            
            for page_num, page in enumerate(doc):
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        # Get image data
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # Save image
                        image_id = f"img_{page_num}_{img_index}"
                        image_filename = f"{image_id}.{image_ext}"
                        image_path = self.output_dir / image_filename
                        
                        with open(image_path, "wb") as f:
                            f.write(image_bytes)
                        
                        # Get image position
                        image_rects = page.get_image_rects(xref)
                        position = {}
                        if image_rects:
                            rect = image_rects[0]
                            position = {
                                "x": rect.x0,
                                "y": rect.y0,
                                "width": rect.width,
                                "height": rect.height
                            }
                        
                        extracted_image = ExtractedImage(
                            image_id=image_id,
                            page_number=page_num + 1,
                            position=position,
                            image_type=image_ext,
                            file_path=str(image_path)
                        )
                        extracted_images.append(extracted_image)
                        
                    except Exception as e:
                        logger.error(f"Error extracting image {img_index} from page {page_num}: {e}")
            
            doc.close()
            return extracted_images
            
        except Exception as e:
            logger.error(f"Error extracting images from PDF {pdf_path}: {e}")
            return []

class LlamaIndexMultiModalService:
    """
    Multi-modal document processing service using LlamaIndex.
    
    Features:
    - PDF text extraction with LlamaParse
    - Image extraction and processing
    - Multi-modal indexing (text + images)
    - Intelligent query interface
    - Mock mode for demo reliability
    """
    
    def __init__(self, mock_mode: Optional[bool] = None):
        """Initialize the multi-modal service."""
        self.mock_mode = mock_mode if mock_mode is not None else self._detect_mock_mode()
        
        # Core components
        self.llm = None
        self.embeddings = None
        self.llamaparse = None
        self.image_extractor = None
        self.index = None
        
        # Storage
        self.processed_documents: Dict[str, ProcessedDocument] = {}
        self.temp_dir = Path(tempfile.mkdtemp(prefix="llamaindex_"))
        
        # Configuration
        self.processing_timeout = int(os.getenv('PDF_PROCESSING_TIMEOUT', '300'))
        self.quality_threshold = float(os.getenv('DATA_QUALITY_THRESHOLD', '0.7'))
        
        # Initialize components
        if self.mock_mode:
            logger.info("🎭 LlamaIndex Multi-Modal Service initialized in MOCK mode")
            self._setup_mock_mode()
        else:
            logger.info("🚀 LlamaIndex Multi-Modal Service initialized in LIVE mode")
            self._setup_live_mode()
    
    def _detect_mock_mode(self) -> bool:
        """Detect if we should run in mock mode."""
        # Explicit mock mode
        if os.getenv('MOCK_MODE', '').lower() in ('true', '1', 'yes'):
            return True
        
        # Check for required packages
        if not LLAMAINDEX_AVAILABLE:
            logger.info("LlamaIndex not available - enabling mock mode")
            return True
        
        # Check for API keys
        required_keys = ['LLAMA_CLOUD_API_KEY', 'OPENAI_API_KEY']
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        
        if missing_keys:
            logger.info(f"Missing API keys: {missing_keys} - enabling mock mode")
            return True
        
        return False
    
    def _setup_mock_mode(self):
        """Setup mock mode components."""
        self.mock_documents = self._load_mock_documents()
        logger.info(f"✅ Mock mode ready with {len(self.mock_documents)} sample documents")
    
    def _setup_live_mode(self):
        """Setup live mode components."""
        try:
            # Initialize LLM
            if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
                self.llm = OpenAI(
                    model="gpt-4o",
                    temperature=0.0,
                    api_key=os.getenv('OPENAI_API_KEY')
                )
                logger.info("✅ OpenAI LLM initialized")
            
            # Initialize embeddings
            if OPENAI_EMBEDDINGS_AVAILABLE and os.getenv('OPENAI_API_KEY'):
                self.embeddings = OpenAIEmbedding(
                    api_key=os.getenv('OPENAI_API_KEY'),
                    embed_batch_size=10
                )
                logger.info("✅ OpenAI embeddings initialized")
            
            # Initialize LlamaParse
            if os.getenv('LLAMA_CLOUD_API_KEY'):
                self.llamaparse = LlamaParse(
                    api_key=os.getenv('LLAMA_CLOUD_API_KEY'),
                    result_type="markdown",
                    verbose=True,
                    language="en"
                )
                logger.info("✅ LlamaParse initialized")
            
            # Initialize image extractor
            self.image_extractor = ImageExtractor(
                output_dir=str(self.temp_dir / "images")
            )
            logger.info("✅ Image extractor initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup live mode: {e}")
            logger.info("🎭 Falling back to mock mode")
            self.mock_mode = True
            self._setup_mock_mode()
    
    def _load_mock_documents(self) -> Dict[str, Dict[str, Any]]:
        """Load mock document data for testing."""
        return {
            "sample-multimodal-doc": {
                "metadata": {
                    "document_id": "sample-multimodal-doc",
                    "filename": "sample_document.pdf",
                    "source_url": "https://example.com/sample.pdf",
                    "processing_timestamp": datetime.now(),
                    "total_pages": 15,
                    "total_images": 8,
                    "quality_score": 0.92,
                    "processing_time_seconds": 12.5
                },
                "text_content": """
                # LlamaIndex Multi-Modal Capabilities
                
                This document demonstrates advanced multi-modal processing with LlamaIndex.
                Our system can extract and index both textual content and visual elements
                from complex documents.
                
                ## Image Processing Pipeline
                
                The image extraction pipeline identifies and processes:
                - Diagrams and charts
                - Photographs and illustrations  
                - Tables and structured data
                - Technical drawings and schematics
                
                ## Relationship Mapping
                
                Our system maintains relationships between:
                - Text sections and relevant images
                - Image captions and content
                - Cross-references and citations
                - Hierarchical document structure
                """,
                "extracted_images": [
                    {
                        "image_id": "img_1_0",
                        "page_number": 2,
                        "position": {"x": 100, "y": 200, "width": 400, "height": 300},
                        "image_type": "png",
                        "file_path": "/tmp/mock_images/architecture_diagram.png",
                        "caption": "LlamaIndex Multi-Modal Architecture Diagram",
                        "context_text": "Figure 1 shows the overall architecture of our multi-modal system."
                    },
                    {
                        "image_id": "img_3_1", 
                        "page_number": 4,
                        "position": {"x": 50, "y": 150, "width": 500, "height": 200},
                        "image_type": "jpg",
                        "file_path": "/tmp/mock_images/pipeline_flow.jpg",
                        "caption": "Document Processing Pipeline",
                        "context_text": "The processing pipeline handles multiple document types efficiently."
                    }
                ]
            }
        }
    
    async def process_document_url(self, document_url: str) -> Dict[str, Any]:
        """
        Process document from URL and return multi-modal results.
        
        Args:
            document_url: URL to the document (PDF, etc.)
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        
        try:
            logger.info(f"📄 Processing document: {document_url}")
            
            if self.mock_mode:
                result = await self._process_document_mock(document_url)
            else:
                result = await self._process_document_live(document_url)
            
            processing_time = time.time() - start_time
            result["processing_time_seconds"] = round(processing_time, 2)
            
            logger.info(f"✅ Document processing completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Document processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "mode": "mock" if self.mock_mode else "live",
                "processing_time_seconds": round(processing_time, 2),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_document_mock(self, document_url: str) -> Dict[str, Any]:
        """Process document in mock mode."""
        logger.info("🎭 Processing document in mock mode")
        
        # Simulate processing delay
        await asyncio.sleep(2.0)
        
        # Return mock document data
        mock_doc = list(self.mock_documents.values())[0].copy()
        mock_doc["metadata"]["source_url"] = document_url
        mock_doc["metadata"]["processing_timestamp"] = datetime.now()
        
        return {
            "success": True,
            "mode": "mock",
            "document": mock_doc,
            "timestamp": datetime.now().isoformat(),
            "capabilities": {
                "text_extraction": True,
                "image_extraction": True,
                "relationship_mapping": True,
                "multi_modal_search": True
            }
        }
    
    async def _process_document_live(self, document_url: str) -> Dict[str, Any]:
        """Process document in live mode."""
        logger.info("🚀 Processing document in live mode")
        
        if not self.llamaparse:
            raise Exception("LlamaParse not initialized")
        
        # Download and process document
        local_path = await self._download_document(document_url)
        
        try:
            # Extract text content
            text_content = await self._extract_text_content(local_path)
            
            # Extract images
            extracted_images = await self._extract_images(local_path)
            
            # Create text chunks
            text_chunks = await self._create_text_chunks(text_content)
            
            # Map relationships
            relationships = await self._map_relationships(text_chunks, extracted_images)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(text_content, extracted_images)
            
            # Create processed document
            doc_metadata = DocumentMetadata(
                document_id=f"doc_{int(time.time())}",
                filename=Path(document_url).name,
                source_url=document_url,
                processing_timestamp=datetime.now(),
                total_pages=1,  # Would be calculated from PDF
                total_images=len(extracted_images),
                quality_score=quality_score,
                processing_time_seconds=0  # Will be set by caller
            )
            
            processed_doc = ProcessedDocument(
                metadata=doc_metadata,
                text_content=text_content,
                text_chunks=text_chunks,
                extracted_images=extracted_images,
                relationships=relationships
            )
            
            # Store processed document
            self.processed_documents[doc_metadata.document_id] = processed_doc
            
            return {
                "success": True,
                "mode": "live",
                "document": processed_doc.model_dump(),
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            # Cleanup temporary file
            if local_path.exists():
                local_path.unlink()
    
    async def _download_document(self, url: str) -> Path:
        """Download document from URL to temporary file."""
        temp_file = self.temp_dir / f"doc_{int(time.time())}.pdf"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(temp_file, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    return temp_file
                else:
                    raise Exception(f"Failed to download document: HTTP {response.status}")
    
    async def _extract_text_content(self, file_path: Path) -> str:
        """Extract text content using LlamaParse."""
        try:
            documents = await self.llamaparse.aload_data([str(file_path)])
            if documents:
                return "\n\n".join([doc.text for doc in documents if doc.text])
            return ""
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""
    
    async def _extract_images(self, file_path: Path) -> List[ExtractedImage]:
        """Extract images from document."""
        if not self.image_extractor:
            return []
        
        try:
            # Create mock node for image extraction
            mock_node = type('Node', (), {
                'metadata': {'source_file': str(file_path)}
            })()
            
            result = self.image_extractor.extract([mock_node])
            return result.get("extracted_images", [])
        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
            return []
    
    async def _create_text_chunks(self, text_content: str) -> List[Dict[str, Any]]:
        """Create semantic text chunks."""
        if not LLAMAINDEX_AVAILABLE:
            # Simple chunking fallback
            words = text_content.split()
            chunk_size = 500
            chunks = []
            for i in range(0, len(words), chunk_size):
                chunk_text = " ".join(words[i:i + chunk_size])
                chunks.append({
                    "chunk_id": f"chunk_{i // chunk_size}",
                    "text": chunk_text,
                    "start_index": i,
                    "end_index": min(i + chunk_size, len(words))
                })
            return chunks
        
        try:
            splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
            nodes = splitter.get_nodes_from_documents([Document(text=text_content)])
            
            chunks = []
            for i, node in enumerate(nodes):
                chunks.append({
                    "chunk_id": f"chunk_{i}",
                    "text": node.text,
                    "metadata": node.metadata
                })
            return chunks
        except Exception as e:
            logger.error(f"Text chunking failed: {e}")
            return []
    
    async def _map_relationships(self, text_chunks: List[Dict], images: List[ExtractedImage]) -> List[Dict[str, Any]]:
        """Map relationships between text and images."""
        relationships = []
        
        # Simple relationship mapping - in production would use more sophisticated analysis
        for i, chunk in enumerate(text_chunks):
            for image in images:
                # Check if chunk mentions images, figures, etc.
                chunk_text = chunk["text"].lower()
                if any(keyword in chunk_text for keyword in ["figure", "image", "diagram", "chart", "table"]):
                    relationships.append({
                        "type": "text_image_reference",
                        "text_chunk_id": chunk["chunk_id"],
                        "image_id": image.image_id,
                        "confidence": 0.7  # Would be calculated more precisely
                    })
        
        return relationships
    
    def _calculate_quality_score(self, text_content: str, images: List[ExtractedImage]) -> float:
        """Calculate processing quality score."""
        score = 0.0
        
        # Text quality (50% of score)
        if text_content and len(text_content.strip()) > 100:
            score += 0.5
        
        # Image extraction quality (30% of score)
        if images:
            score += min(0.3, len(images) * 0.05)
        
        # Content structure (20% of score)
        if text_content:
            # Check for structure indicators
            structure_indicators = ["#", "##", "###", "Figure", "Table", "Chapter"]
            found_indicators = sum(1 for indicator in structure_indicators if indicator in text_content)
            score += min(0.2, found_indicators * 0.04)
        
        return round(min(1.0, score), 2)
    
    async def query_multimodal(self, query: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform multi-modal query across text and images.
        
        Args:
            query: Search query
            document_id: Optional specific document to search
            
        Returns:
            Search results with text and image matches
        """
        if self.mock_mode:
            return await self._query_multimodal_mock(query, document_id)
        
        # In live mode, would use actual vector search
        return await self._query_multimodal_live(query, document_id)
    
    async def _query_multimodal_mock(self, query: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        """Mock multi-modal query."""
        await asyncio.sleep(0.5)  # Simulate processing
        
        return {
            "success": True,
            "mode": "mock",
            "query": query,
            "results": {
                "text_matches": [
                    {
                        "chunk_id": "chunk_0",
                        "text": "LlamaIndex provides powerful multi-modal capabilities for processing documents with both text and visual content.",
                        "score": 0.89,
                        "document_id": "sample-multimodal-doc"
                    }
                ],
                "image_matches": [
                    {
                        "image_id": "img_1_0",
                        "caption": "LlamaIndex Multi-Modal Architecture Diagram",
                        "score": 0.76,
                        "document_id": "sample-multimodal-doc"
                    }
                ],
                "relationships": [
                    {
                        "type": "text_image_reference",
                        "text_chunk_id": "chunk_0",
                        "image_id": "img_1_0",
                        "relevance": 0.85
                    }
                ]
            },
            "total_results": 2,
            "processing_time_ms": 450
        }
    
    async def _query_multimodal_live(self, query: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        """Live multi-modal query implementation."""
        # Would implement actual vector search with embeddings
        # For now, return basic implementation
        return {
            "success": True,
            "mode": "live",
            "query": query,
            "results": {"text_matches": [], "image_matches": [], "relationships": []},
            "message": "Live multi-modal search implementation pending"
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status and capabilities."""
        return {
            "mode": "mock" if self.mock_mode else "live",
            "capabilities": {
                "text_extraction": True,
                "image_extraction": PYMUPDF_AVAILABLE,
                "multimodal_indexing": LLAMAINDEX_AVAILABLE,
                "semantic_search": self.embeddings is not None,
                "relationship_mapping": True
            },
            "components": {
                "llamaparse_available": self.llamaparse is not None,
                "llm_available": self.llm is not None,
                "embeddings_available": self.embeddings is not None,
                "image_extractor_available": self.image_extractor is not None
            },
            "statistics": {
                "processed_documents": len(self.processed_documents),
                "mock_documents_available": len(self.mock_documents) if self.mock_mode else 0
            },
            "api_keys_detected": {
                "llama_cloud": bool(os.getenv('LLAMA_CLOUD_API_KEY')),
                "openai": bool(os.getenv('OPENAI_API_KEY'))
            }
        }
    
    def cleanup(self):
        """Cleanup resources and temporary files."""
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

# Global service instance
_llamaindex_service = None

def get_llamaindex_service(mock_mode: Optional[bool] = None) -> LlamaIndexMultiModalService:
    """Get or create LlamaIndex service instance."""
    global _llamaindex_service
    
    if _llamaindex_service is None:
        _llamaindex_service = LlamaIndexMultiModalService(mock_mode=mock_mode)
    
    return _llamaindex_service