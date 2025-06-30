# Cite Me If You Can

A semantic search application for scientific journals that allows users to find relevant research papers based on natural language queries and get AI-generated answers with proper citations.

## Project Structure

The project is organized into two main components:

- **Backend**: FastAPI-based semantic search API with Pinecone vector database integration
- **Frontend**: React-based single-page web application for user interaction

## Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example` and add your Pinecone API key

4. Start the server:
   ```
   uvicorn app:app --reload
   ```

## Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

## Ingestion Pipeline

The system includes a comprehensive ingestion pipeline for processing scientific journal documents. For detailed information about the pipeline design, implementation, and vector database selection, please refer to the [Ingestion Pipeline Design](./ingestion_pipeline_design.md) document.

## Backend API Endpoints

### Upload Journal Chunks

```
PUT /api/upload
```

Accepts JSON of journal chunks, generates embeddings, and stores them in the vector database.

**Request Body:**
- `file`: Direct file upload containing JSON array of chunks
- `file_url`: Alternative URL to fetch the JSON file from
- `schema_version`: Version of the schema being used

**Response:**
- Status: 202 Accepted
- Body: Success message with number of chunks processed

### Similarity Search

```
POST /api/similarity_search
```

Performs semantic similarity search using the provided query.

**Request Body:**
```json
{
  "query": "your search query here",
  "k": 10,
  "min_score": 0.25
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "chunk_id",
      "score": 0.85,
      "metadata": {
        "id": "chunk_id",
        "source_doc_id": "doc_123",
        "chunk_index": 1,
        "section_heading": "Introduction",
        "doi": "10.1234/example",
        "journal": "Journal of Examples",
        "publish_year": 2023,
        "usage_count": 0,
        "attributes": {},
        "link": "https://example.com/paper"
      },
      "text": "The content of the chunk..."
    }
  ]
}
```

## Frontend Features

The frontend provides a user-friendly interface for interacting with the semantic search API:

1. **Question Input**: Users can enter natural language questions about scientific topics

2. **AI-Generated Answers**: The system processes the question, retrieves relevant journal chunks, and generates a comprehensive answer

3. **Citation Display**: All answers include proper citations showing:
   - Source document ID (e.g., `extension_brief_mucuna.pdf`)
   - Section heading (e.g., "Why Grow Velvet Bean?")
   - Clickable link to the original document

## Chunk Format

Each chunk should follow this structure:

```json
{
  "id": "unique_chunk_id",
  "source_doc_id": "source_document_id",
  "chunk_index": 1,
  "section_heading": "Section Title",
  "doi": "10.1234/example",
  "journal": "Journal Name",
  "publish_year": 2023,
  "usage_count": 0,
  "attributes": {
    "key": "value"
  },
  "link": "https://example.com/paper",
  "text": "The actual content of the chunk..."
}
```
