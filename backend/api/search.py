from fastapi import APIRouter, HTTPException
from models.search import SimilaritySearchRequest, SimilaritySearchResponse, SimilaritySearchResult
from models.chunks import ChunkMetadata
from core.embeddings import generate_embedding
from services.pinecone_service import query_vectors

# Create router
router = APIRouter()

@router.post("/api/similarity_search")
async def similarity_search(request: SimilaritySearchRequest):
    """
    Perform semantic similarity search using the provided query.
    
    Returns top-k semantic matches above the minimum similarity score.
    """
    try:
        # Generate embedding for the query
        query_embedding = generate_embedding(request.query)
        
        # Perform similarity search
        search_results = query_vectors(
            query_vector=query_embedding,
            top_k=request.k,
            include_metadata=True
        )
        
        # Process and filter results
        results = []
        for match in search_results.get("matches", []):
            if match["score"] < request.min_score:
                continue
                
            # Extract metadata and create result object
            metadata = match["metadata"]
            text = metadata.pop("text", "")  # Remove text from metadata
            
            # Add missing fields with defaults if needed
            required_fields = ["id", "source_doc_id", "chunk_index", "section_heading", 
                            "doi", "journal", "publish_year", "usage_count", 
                            "attributes", "link"]
            
            for field in required_fields:
                if field not in metadata:
                    if field == "attributes":
                        metadata[field] = {}
                    elif field in ["chunk_index", "publish_year", "usage_count"]:
                        metadata[field] = 0
                    else:
                        metadata[field] = ""
            
            result = SimilaritySearchResult(
                id=match["id"],
                score=match["score"],
                metadata=ChunkMetadata(**metadata),
                text=text
            )
            results.append(result)
        
        return SimilaritySearchResponse(results=results)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing similarity search: {str(e)}")
