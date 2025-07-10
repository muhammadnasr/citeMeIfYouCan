import openai
from fastapi import HTTPException
from core.config import OPENAI_API_KEY

# Initialize OpenAI client
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    print("Warning: OPENAI_API_KEY not found in environment variables")

def generate_answer(question, context):
    """Generate an answer to a question using OpenAI and the provided context
    
    Args:
        question (str): The question to answer
        context (str): The context to use for answering
        
    Returns:
        str: The generated answer
        
    Raises:
        HTTPException: If OpenAI API key is not configured
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    # Generate prompt
    prompt = f"""Answer the following question based on the provided context. 
    Include information only from the context. If you cannot answer the question based on the context, 
    say that you don't have enough information.
    
    QUESTION: {question}
    
    CONTEXT: {context}
    
    Provide a comprehensive answer with proper citations. Do not mention 'CHUNK' or 'SOURCE' in your answer.
    Instead, integrate the information smoothly and cite sources at the end of relevant sentences or paragraphs.
    """
    
    try:
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
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")
