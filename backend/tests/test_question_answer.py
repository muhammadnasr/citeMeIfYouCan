from fastapi.testclient import TestClient
import pytest
import os
import sys

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import config and services
from core.config import settings
from services.pinecone_service import initialize_pinecone

# Initialize Pinecone before importing app
index = initialize_pinecone()

# Import app after initialization
from main import app

client = TestClient(app)

def test_question_answer_endpoint():
    """Test the question_answer endpoint with a simple question"""
    # Skip test if OpenAI API key is not set
    if not settings.openai_api_key:
        pytest.skip("OpenAI API key not set in settings, skipping test")
    
    # Test data
    test_data = {
        "question": "What is semantic search?",
        "k": 3,
        "min_score": 0.2
    }
    
    # Make request
    response = client.post("/api/question_answer", json=test_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "answer" in data
    assert "citations" in data
    assert isinstance(data["answer"], str)
    assert isinstance(data["citations"], list)
    
    # Check that answer is not empty
    assert len(data["answer"]) > 0
    
    # If citations are present, check their structure
    if data["citations"]:
        citation = data["citations"][0]
        assert "source_doc_id" in citation
        assert "section_heading" in citation
        assert "link" in citation
