from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import json
from models.chunks import Chunk
from core.embeddings import generate_embedding
from services.pinecone_service import store_vectors

# Create router
router = APIRouter()

def process_document_chunks(chunks_data):
    """Process document chunks and prepare them for storage
    
    Args:
        chunks_data (list): Raw chunks data
        
    Returns:
        list: List of processed Chunk objects
    """
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

def prepare_vectors_for_storage(chunks):
    """Prepare vectors for storage in the vector database
    
    Args:
        chunks (list): List of Chunk objects
        
    Returns:
        list: List of vector objects ready for storage
    """
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
    
    return vectors

@router.put("/api/upload", status_code=202)
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
        
        # Prepare vectors
        vectors = prepare_vectors_for_storage(chunks)
        
        # Store in vector database
        num_stored = store_vectors(vectors)
        
        return {"message": f"Successfully processed and stored {num_stored} chunks", "status": "accepted"}
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")
