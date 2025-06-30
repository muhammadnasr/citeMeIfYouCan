import json
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add parent directory to path to import app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

client = TestClient(app)

# Load sample chunks for testing
with open(os.path.join(os.path.dirname(__file__), 'sample_chunks.json'), 'r') as f:
    sample_chunks = json.load(f)

def test_similarity_search_endpoint():
    """Test the similarity search endpoint with a query related to agriculture"""
    request_data = {
        "query": "soil fertility improvement using legumes",
        "k": 3,
        "min_score": 0.1
    }
    
    response = client.post("/api/similarity_search", json=request_data)
    
    # The endpoint should return a valid response structure
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)

def test_upload_endpoint():
    """Test the upload endpoint with sample chunks"""
    # Prepare the request with sample chunks
    files = {
        'file': ('sample_chunks.json', json.dumps(sample_chunks), 'application/json')
    }
    data = {
        'schema_version': '1.0'
    }
    
    response = client.put("/api/upload", files=files, data=data)
    
    # Should return 202 Accepted
    assert response.status_code == 202
    assert "message" in response.json()
    assert "status" in response.json()
    assert response.json()["status"] == "accepted"

def test_upload_endpoint_validation():
    """Test validation of the upload endpoint"""
    # Missing both file and file_url
    response = client.put(
        "/api/upload",
        data={"schema_version": "1.0"}
    )
    assert response.status_code == 400
    
    # Test with invalid chunk format
    invalid_chunks = [{"invalid_field": "value"}]
    files = {
        'file': ('invalid_chunks.json', json.dumps(invalid_chunks), 'application/json')
    }
    data = {
        'schema_version': '1.0'
    }
    
    response = client.put("/api/upload", files=files, data=data)
    assert response.status_code == 422
