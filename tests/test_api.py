import json
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_similarity_search_endpoint():
    """Test the similarity search endpoint with a mock query"""
    request_data = {
        "query": "climate change impact on coral reefs",
        "k": 5,
        "min_score": 0.2
    }
    
    response = client.post("/api/similarity_search", json=request_data)
    
    # Even without data, the endpoint should return a valid response structure
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)

def test_upload_endpoint_validation():
    """Test validation of the upload endpoint"""
    # Missing both file and file_url
    response = client.put(
        "/api/upload",
        json={"schema_version": "1.0"}
    )
    assert response.status_code == 400
    
    # Test with invalid chunk format
    invalid_chunks = [{"invalid_field": "value"}]
    response = client.put(
        "/api/upload",
        files={"file": ("chunks.json", json.dumps(invalid_chunks), "application/json")},
        data={"schema_version": "1.0"}
    )
    assert response.status_code == 422 or response.status_code == 500
