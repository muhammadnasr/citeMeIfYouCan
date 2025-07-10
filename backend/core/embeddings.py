from sentence_transformers import SentenceTransformer

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Can be replaced with a more domain-specific model

def generate_embedding(text):
    """Generate embedding for a text using the sentence transformer model
    
    Args:
        text (str): The text to generate embedding for
        
    Returns:
        list: The embedding vector as a list
    """
    return model.encode(text).tolist()

def get_model_dimension():
    """Get the embedding dimension of the current model
    
    Returns:
        int: The dimension of the embedding vectors
    """
    return model.get_sentence_embedding_dimension()
