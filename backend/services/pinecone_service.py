import pinecone
from fastapi import HTTPException
from core.config import PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME
from core.embeddings import get_model_dimension

# Initialize Pinecone client
pc = None
index = None

def initialize_pinecone():
    """Initialize the Pinecone client and connect to the index
    
    Returns:
        pinecone.Index or None: The connected index or None if initialization failed
    """
    global pc, index
    
    if not PINECONE_API_KEY:
        print("Warning: PINECONE_API_KEY not found in environment variables")
        return None
    
    try:
        pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index exists, if not create it
        try:
            index = pc.Index(PINECONE_INDEX_NAME)
            print(f"Connected to existing index: {PINECONE_INDEX_NAME}")
        except Exception:
            print(f"Creating new index: {PINECONE_INDEX_NAME}")
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=get_model_dimension(),
                metric="cosine",
                spec=pinecone.ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT)
            )
            index = pc.Index(PINECONE_INDEX_NAME)
        
        return index
    except Exception as e:
        print(f"Error initializing Pinecone: {str(e)}")
        return None

def store_vectors(vectors):
    """Store vectors in Pinecone
    
    Args:
        vectors (list): List of vector objects to store
        
    Returns:
        int: Number of vectors stored
    
    Raises:
        HTTPException: If vector database is not initialized
    """
    if not index:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    # Upsert vectors in batches (Pinecone has limits)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch)
    
    return len(vectors)

def query_vectors(query_vector, top_k=10, include_metadata=True):
    """Query vectors in Pinecone
    
    Args:
        query_vector (list): Query vector
        top_k (int): Number of results to return
        include_metadata (bool): Whether to include metadata in results
        
    Returns:
        dict: Query results
        
    Raises:
        HTTPException: If vector database is not initialized
    """
    if not index:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    # Check if index has any vectors
    stats = index.describe_index_stats()
    if stats.get('total_vector_count', 0) == 0:
        return {"matches": []}
    
    # Perform similarity search
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=include_metadata
    )
    
    return results

def get_index_stats():
    """Get statistics about the Pinecone index
    
    Returns:
        dict: Index statistics
        
    Raises:
        HTTPException: If vector database is not initialized
    """
    if not index:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    return index.describe_index_stats()
