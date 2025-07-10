from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class ChunkMetadata(BaseModel):
    """Metadata for a document chunk"""
    id: str
    source_doc_id: str
    chunk_index: int
    section_heading: str
    doi: str = "Unknown"
    journal: str
    publish_year: int
    usage_count: int
    attributes: Dict[str, Any]
    link: str

class Chunk(ChunkMetadata):
    """Document chunk with text and metadata"""
    text: str

class UploadRequest(BaseModel):
    """Request model for uploading document chunks"""
    file_url: Optional[str] = None
    schema_version: str
