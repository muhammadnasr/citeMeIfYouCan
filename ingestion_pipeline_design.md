# Ingestion Pipeline Design

## Overview
This document outlines the design for the ingestion pipeline that processes newly uploaded scientific journal files, chunks them into coherent segments, generates embeddings, and stores them in a vector database for semantic search capabilities.

## Pipeline Steps

### 1. Detecting Newly Uploaded Journal Files

```python
def detect_new_files(watch_directory, processed_files_log):
    """
    Monitor a directory for new files and identify unprocessed ones.
    
    Args:
        watch_directory: Directory where new journal files are deposited
        processed_files_log: Record of previously processed files
        
    Returns:
        List of new file paths to be processed
    """
    # Get all files in the watch directory
    current_files = list_files_in_directory(watch_directory)
    
    # Load log of previously processed files
    processed_files = load_processed_files(processed_files_log)
    
    # Identify new files by comparing with processed log
    new_files = [file for file in current_files if file not in processed_files]
    
    return new_files
```

### 2. Chunking Content into Coherent Segments

```python
def chunk_document(file_path):
    """
    Process a document and split it into coherent chunks.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        List of document chunks with metadata
    """
    # Extract document content based on file type (PDF, DOCX, etc.)
    raw_content = extract_document_content(file_path)
    
    # Extract metadata from the document
    doc_metadata = extract_document_metadata(file_path)
    
    # Split document into sections based on headings
    sections = split_by_headings(raw_content)
    
    chunks = []
    for i, section in enumerate(sections):
        # Generate a unique ID for the chunk
        chunk_id = f"{doc_metadata['doc_id']}_{i+1:02d}_{slugify(section['heading'])}"
        
        # Create chunk with metadata
        chunk = {
            "id": chunk_id,
            "source_doc_id": doc_metadata['doc_id'],
            "chunk_index": i + 1,
            "section_heading": section['heading'],
            "doi": doc_metadata.get('doi', 'Unknown'),
            "journal": doc_metadata.get('journal', 'Unknown'),
            "publish_year": doc_metadata.get('publish_year', datetime.now().year),
            "usage_count": 0,
            "attributes": extract_attributes(section['content']),
            "link": doc_metadata.get('link', ''),
            "text": section['content']
        }
        
        chunks.append(chunk)
    
    return chunks
```

### 3. Generating Embeddings

```python
def generate_embeddings(chunks, embedding_model):
    """
    Generate vector embeddings for each chunk.
    
    Args:
        chunks: List of document chunks
        embedding_model: Model to use for generating embeddings
        
    Returns:
        Chunks with added embedding vectors
    """
    for chunk in chunks:
        # Generate embedding for the chunk text
        embedding = embedding_model.encode(chunk['text'])
        
        # Add embedding to the chunk
        chunk['embedding'] = embedding
    
    return chunks
```

### 4. Storing in Vector Database

```python
def store_in_vector_db(chunks, vector_db):
    """
    Store chunks with embeddings in the vector database.
    
    Args:
        chunks: List of chunks with embeddings
        vector_db: Vector database client
        
    Returns:
        Status of the storage operation
    """
    # Prepare batch for insertion
    batch = []
    for chunk in chunks:
        # Extract embedding
        embedding = chunk.pop('embedding')
        
        # Prepare record for insertion
        record = {
            'id': chunk['id'],
            'vector': embedding,
            'metadata': chunk
        }
        
        batch.append(record)
    
    # Insert batch into vector database
    result = vector_db.insert(batch)
    
    # Update processed files log
    update_processed_files_log(chunks)
    
    return result
```

### 5. Main Ingestion Pipeline

```python
def run_ingestion_pipeline():
    """
    Main function to run the complete ingestion pipeline.
    """
    # Initialize components
    watch_directory = config.WATCH_DIRECTORY
    processed_files_log = config.PROCESSED_FILES_LOG
    embedding_model = load_embedding_model()
    vector_db = connect_to_vector_db()
    
    # Detect new files
    new_files = detect_new_files(watch_directory, processed_files_log)
    
    # Process each new file
    for file_path in new_files:
        try:
            # Chunk the document
            chunks = chunk_document(file_path)
            
            # Generate embeddings
            chunks_with_embeddings = generate_embeddings(chunks, embedding_model)
            
            # Store in vector database
            store_in_vector_db(chunks_with_embeddings, vector_db)
            
            # Log successful processing
            log_success(file_path)
            
        except Exception as e:
            # Log error
            log_error(file_path, str(e))
```

## Vector Database Selection

For this project, I recommend using **Pinecone** as the vector database for the following reasons:

1. **Scalability**: Pinecone is designed to handle billions of vectors efficiently, which is important as the journal collection grows over time.

2. **Performance**: It provides fast similarity search with low latency, which is crucial for a responsive research assistant.

3. **Ease of Integration**: Pinecone offers simple APIs and SDKs for Python and JavaScript, making it easy to integrate with both the ingestion pipeline and the frontend application.

4. **Metadata Filtering**: Pinecone supports filtering by metadata fields, which will be useful for filtering results by journal, publication year, or other attributes.

5. **Managed Service**: As a fully managed service, it reduces operational overhead and allows the team to focus on application development rather than database management.

6. **Cost-Effectiveness**: Pinecone offers a free tier that's suitable for prototyping, with reasonable pricing for scaling up.

Alternative options that could also work well include:

- **Milvus**: Open-source vector database with strong performance, but requires more setup and management.
- **Weaviate**: Combines vector search with GraphQL, offering more complex data modeling capabilities.
- **Qdrant**: Good performance with rich filtering capabilities, but less widely adopted.

For this prototype, Pinecone offers the best balance of performance, ease of use, and features needed for the research assistant application.
