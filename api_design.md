# API Design

## Implementation Stack

For the backend implementation, we'll use:
- **Node.js** with **Express.js** for the API server
- **MongoDB** for storing document metadata
- **Pinecone** for vector storage and similarity search
- **OpenAI Embeddings API** for generating embeddings

## Required Endpoints

### 1. Upload API

```javascript
// routes/upload.js
const express = require('express');
const router = express.Router();
const multer = require('multer');
const upload = multer({ dest: 'uploads/' });
const { processUpload } = require('../services/uploadService');

// PUT /api/upload
router.put('/', upload.single('file'), async (req, res) => {
  try {
    const { file_url, schema_version } = req.body;
    const file = req.file;
    
    // Validate request
    if (!file && !file_url) {
      return res.status(400).json({ error: 'Either file or file_url is required' });
    }
    
    if (!schema_version) {
      return res.status(400).json({ error: 'schema_version is required' });
    }
    
    // Process upload asynchronously
    const jobId = await processUpload({ file, file_url, schema_version });
    
    // Return 202 Accepted
    return res.status(202).json({
      status: 'accepted',
      message: 'Upload accepted and processing',
      job_id: jobId
    });
  } catch (error) {
    console.error('Upload error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
```

### 2. Similarity Search API

```javascript
// routes/similaritySearch.js
const express = require('express');
const router = express.Router();
const { searchSimilarDocuments } = require('../services/searchService');

// POST /api/similarity_search
router.post('/', async (req, res) => {
  try {
    const { query, k = 10, min_score = 0.25 } = req.body;
    
    // Validate request
    if (!query || typeof query !== 'string') {
      return res.status(400).json({ error: 'Valid query string is required' });
    }
    
    // Perform similarity search
    const results = await searchSimilarDocuments(query, k, min_score);
    
    // Return results
    return res.status(200).json({ results });
  } catch (error) {
    console.error('Search error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
```

## Core Services Implementation

### Upload Service

```javascript
// services/uploadService.js
const { v4: uuidv4 } = require('uuid');
const { generateEmbeddings } = require('./embeddingService');
const { storeVectors } = require('./vectorDbService');
const { processDocument } = require('./documentService');

async function processUpload({ file, file_url, schema_version }) {
  // Generate a unique job ID
  const jobId = uuidv4();
  
  // Process asynchronously
  setTimeout(async () => {
    try {
      // Extract document content
      const documentContent = await processDocument(file || file_url);
      
      // Generate embeddings for chunks
      const chunksWithEmbeddings = await generateEmbeddings(documentContent.chunks);
      
      // Store in vector database
      await storeVectors(chunksWithEmbeddings);
      
      console.log(`Job ${jobId} completed successfully`);
    } catch (error) {
      console.error(`Job ${jobId} failed:`, error);
    }
  }, 0);
  
  return jobId;
}

module.exports = { processUpload };
```

### Search Service

```javascript
// services/searchService.js
const { generateEmbedding } = require('./embeddingService');
const { searchVectors, updateUsageCount } = require('./vectorDbService');

async function searchSimilarDocuments(query, k, minScore) {
  // Generate embedding for the query
  const queryEmbedding = await generateEmbedding(query);
  
  // Search for similar vectors
  const searchResults = await searchVectors(queryEmbedding, k);
  
  // Filter by minimum score
  const filteredResults = searchResults.filter(result => result.score >= minScore);
  
  // Update usage counts
  await updateUsageCount(filteredResults.map(result => result.id));
  
  return filteredResults;
}

module.exports = { searchSimilarDocuments };
```

## Project Structure

```
citeMeIfYouCan/
├── server/
│   ├── index.js           # Main entry point
│   ├── routes/
│   │   ├── upload.js      # Upload API route
│   │   └── search.js      # Similarity search API route
│   ├── services/
│   │   ├── uploadService.js    # Handles document upload and processing
│   │   ├── searchService.js    # Handles similarity search
│   │   ├── embeddingService.js # Generates embeddings
│   │   ├── vectorDbService.js  # Interacts with vector database
│   │   └── documentService.js  # Processes document content
│   ├── models/
│   │   └── chunk.js       # Data model for document chunks
│   └── config/
│       └── index.js       # Configuration settings
├── client/
│   └── ...                # Frontend code (to be implemented later)
├── package.json
└── README.md
```

## Next Steps

1. Set up the Express.js server
2. Implement the core services
3. Connect to Pinecone vector database
4. Implement the API routes
5. Add error handling and validation
