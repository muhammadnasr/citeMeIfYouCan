from pydantic import BaseModel
from typing import List
from .chunks import ChunkMetadata

class SimilaritySearchRequest(BaseModel):
    """Request model for similarity search"""
    query: str
    k: int = 10
    min_score: float = 0.25

class SimilaritySearchResult(BaseModel):
    """Result model for a single search result"""
    id: str
    score: float
    metadata: ChunkMetadata
    text: str

class SimilaritySearchResponse(BaseModel):
    """Response model for similarity search"""
    results: List[SimilaritySearchResult]
