from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import numpy as np
from dotenv import load_dotenv
import pinecone
from sentence_transformers import SentenceTransformer
import openai

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai.api_key = openai_api_key
else:
    print("Warning: OPENAI_API_KEY not found in environment variables")

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
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
index_name = os.getenv("PINECONE_INDEX", "journal-chunks")

if api_key:
    pc = pinecone.Pinecone(api_key=api_key)
    # Check if index exists, if not create it
    try:
        index = pc.Index(index_name)
        print(f"Connected to existing index: {index_name}")
    except Exception:
        print(f"Creating new index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=model.get_sentence_embedding_dimension(),
            metric="cosine",
            spec=pinecone.ServerlessSpec(cloud="aws", region=pinecone_environment)
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

class QuestionAnswerRequest(BaseModel):
    question: str
    k: int = 10
    min_score: float = 0.25

class Citation(BaseModel):
    source_doc_id: str
    section_heading: str
    link: str

class QuestionAnswerResponse(BaseModel):
    answer: str
    citations: List[Citation]

# Helper functions
def generate_embedding(text):
    """Generate embedding for a text using the sentence transformer model"""
    return model.encode(text).tolist()

def store_chunks_in_vector_db(chunks):
    """Store processed chunks in the vector database"""
    if not index:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    vectors = []
    for chunk in chunks:
        chunk_dict = chunk.model_dump() if hasattr(chunk, 'model_dump') else chunk.dict()
        embedding = generate_embedding(chunk.text)
        
        # Prepare metadata - Pinecone only accepts simple types
        metadata = {}
        for key, value in chunk_dict.items():
            if key == 'attributes':
                # Convert attributes dict to a list of strings for Pinecone
                if isinstance(value, dict):
                    metadata['attribute_keys'] = list(value.keys())
                else:
                    metadata['attribute_keys'] = []
            elif isinstance(value, (str, int, float, bool)) or (
                isinstance(value, list) and all(isinstance(item, str) for item in value)
            ):
                metadata[key] = value
        
        # Always include text in metadata for retrieval
        metadata['text'] = chunk.text
        
        # Prepare record for insertion
        vector = {
            'id': chunk.id,
            'values': embedding,
            'metadata': metadata
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
        # Ensure attributes is a dictionary
        if isinstance(chunk_data.get('attributes', []), list):
            # Convert list of attributes to a dictionary
            attributes = {attr: True for attr in chunk_data.get('attributes', [])}
            chunk_data['attributes'] = attributes
            
        # Set default values for optional fields
        if 'doi' not in chunk_data:
            chunk_data['doi'] = 'Unknown'
            
        # Create Chunk object with validation
        try:
            chunk = Chunk(**chunk_data)
            chunks.append(chunk)
        except Exception as e:
            print(f"Error processing chunk {chunk_data.get('id', 'unknown')}: {str(e)}")
            raise
    
    return chunks

# API Endpoints
@app.put("/api/upload", status_code=202)
async def upload_chunks(schema_version: str = Form(...), file: Optional[UploadFile] = File(None), file_url: Optional[str] = Form(None)):
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
        elif file_url:
            # TODO: Implement fetching from URL
            # For now, raise an error
            raise HTTPException(status_code=400, detail="file_url support not implemented yet")
        else:
            raise HTTPException(status_code=400, detail="Either file or file_url must be provided")
        
        # Process chunks
        try:
            chunks = process_document_chunks(chunks_data)
        except Exception as validation_error:
            raise HTTPException(status_code=422, detail=f"Invalid chunk format: {str(validation_error)}")
        
        # Store in vector database
        num_stored = store_chunks_in_vector_db(chunks)
        
        return {"message": f"Successfully processed and stored {num_stored} chunks", "status": "accepted"}
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
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
        
        # Check if index has any vectors
        stats = index.describe_index_stats()
        if stats.get('total_vector_count', 0) == 0:
            return SimilaritySearchResponse(results=[])
        
        # Perform similarity search
        search_results = index.query(
            vector=query_embedding,
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

@app.post("/api/question_answer")
async def question_answer(request: QuestionAnswerRequest):
    """
    Generate an answer to a question using relevant chunks from the vector database.
    
    1. Performs semantic search to find relevant chunks
    2. Sends chunks to LLM to generate an answer
    3. Returns the answer with proper citations
    """
    try:
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
            
        # First, perform similarity search to find relevant chunks
        search_request = SimilaritySearchRequest(
            query=request.question,
            k=request.k,
            min_score=request.min_score
        )
        
        search_response = await similarity_search(search_request)
        
        if not search_response.results:
            return QuestionAnswerResponse(
                answer="I couldn't find any relevant information to answer your question.",
                citations=[]
            )
        
        # Prepare context from search results
        context = ""
        citations = []
        
        for i, result in enumerate(search_response.results):
            context += f"\n\nCHUNK {i+1}:\n{result.text}\n"
            context += f"SOURCE: {result.metadata.source_doc_id}, SECTION: {result.metadata.section_heading}\n"
            
            citation = Citation(
                source_doc_id=result.metadata.source_doc_id,
                section_heading=result.metadata.section_heading,
                link=result.metadata.link
            )
            citations.append(citation)
        
        # Generate answer using OpenAI
        prompt = f"""Answer the following question based on the provided context. 
        Include information only from the context. If you cannot answer the question based on the context, 
        say that you don't have enough information.
        
        QUESTION: {request.question}
        
        CONTEXT: {context}
        
        Provide a comprehensive answer with proper citations. Do not mention 'CHUNK' or 'SOURCE' in your answer.
        Instead, integrate the information smoothly and cite sources at the end of relevant sentences or paragraphs.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",  # or another appropriate model
            messages=[
                {"role": "system", "content": "You are a helpful research assistant that provides accurate information with proper citations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        return QuestionAnswerResponse(
            answer=answer,
            citations=citations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
