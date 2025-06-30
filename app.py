from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import numpy as np
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Cite Me If You Can API",
    description="API for scientific journal semantic search",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Can be replaced with a more domain-specific model

# Initialize Pinecone
api_key = os.getenv("PINECONE_API_KEY")
environment = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
index_name = os.getenv("PINECONE_INDEX", "journal-chunks")

if api_key:
    pc = Pinecone(api_key=api_key)
    # Check if index exists, if not create it
    try:
        index = pc.Index(index_name)
        print(f"Connected to existing index: {index_name}")
    except Exception:
        print(f"Creating new index: {index_name}")
        # Create a new index with serverless spec
        pc.create_index(
            name=index_name,
            dimension=model.get_sentence_embedding_dimension(),
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-west-2")
        )
        index = pc.Index(index_name)
else:
    print("Warning: PINECONE_API_KEY not found in environment variables")
    index = None

# Request and response models
class UploadRequest(BaseModel):
    file_url: Optional[str] = None
    schema_version: str

class ChunkMetadata(BaseModel):
    id: str
    source_doc_id: str
    chunk_index: int
    section_heading: str
    doi: str
    journal: str
    publish_year: int
    usage_count: int
    attributes: Dict[str, Any]
    link: str

class Chunk(ChunkMetadata):
    text: str

class SimilaritySearchRequest(BaseModel):
    query: str
    k: int = 10
    min_score: float = 0.25

class SimilaritySearchResult(BaseModel):
    id: str
    score: float
    metadata: ChunkMetadata
    text: str

class SimilaritySearchResponse(BaseModel):
    results: List[SimilaritySearchResult]

# Helper functions
def generate_embedding(text):
    """Generate embedding for a text using the sentence transformer model"""
    return model.encode(text).tolist()

def store_chunks_in_vector_db(chunks):
    """Store chunks with embeddings in Pinecone"""
    if not index:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    vectors = []
    for chunk in chunks:
        chunk_dict = chunk.dict()
        embedding = generate_embedding(chunk.text)
        
        # Prepare record for insertion
        vector = {
            'id': chunk.id,
            'values': embedding,
            'metadata': {
                **chunk_dict,
                'text': chunk.text  # Include text in metadata for retrieval
            }
        }
        
        vectors.append(vector)
    
    # Upsert vectors in batches (Pinecone has limits)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch)
    
    return len(vectors)

def process_document_chunks(chunks_data):
    """Process document chunks and prepare them for storage"""
    chunks = []
    for chunk_data in chunks_data:
        # Create Chunk object with validation
        chunk = Chunk(**chunk_data)
        chunks.append(chunk)
    
    return chunks

# API Endpoints
@app.put("/api/upload", status_code=202)
async def upload_chunks(request: UploadRequest = Body(...), file: Optional[UploadFile] = File(None)):
    """
    Upload journal chunks, generate embeddings, and store them in the vector database.
    
    - Request can include either file_url or direct file upload
    - Schema version must be provided for data validation
    """
    try:
        # Handle file upload or URL
        if file:
            # Read uploaded file content
            content = await file.read()
            chunks_data = json.loads(content)
        elif request.file_url:
            # TODO: Implement fetching from URL
            # For now, raise an error
            raise HTTPException(status_code=400, detail="file_url support not implemented yet")
        else:
            raise HTTPException(status_code=400, detail="Either file or file_url must be provided")
        
        # Process chunks
        chunks = process_document_chunks(chunks_data)
        
        # Store in vector database
        num_stored = store_chunks_in_vector_db(chunks)
        
        return {"message": f"Successfully processed and stored {num_stored} chunks", "status": "accepted"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

@app.post("/api/similarity_search")
async def similarity_search(request: SimilaritySearchRequest):
    """
    Perform semantic similarity search using the provided query.
    
    Returns top-k semantic matches above the minimum similarity score.
    """
    try:
        if not index:
            raise HTTPException(status_code=500, detail="Vector database not initialized")
        
        # Generate embedding for the query
        query_embedding = generate_embedding(request.query)
        
        # Perform similarity search
        search_results = index.query(
            vector=query_embedding,
            top_k=request.k,
            include_metadata=True
        )
        
        # Process and filter results
        results = []
        for match in search_results["matches"]:
            if match["score"] < request.min_score:
                continue
                
            # Extract metadata and create result object
            metadata = match["metadata"]
            text = metadata.pop("text", "")
            
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
