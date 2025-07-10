from fastapi import APIRouter, HTTPException
from models.qa import QuestionAnswerRequest, QuestionAnswerResponse, Citation
from models.search import SimilaritySearchRequest
from services.openai_service import generate_answer
from api.search import similarity_search

# Create router
router = APIRouter()

@router.post("/api/question_answer")
async def question_answer(request: QuestionAnswerRequest):
    """
    Generate an answer to a question using relevant chunks from the vector database.
    
    1. Performs semantic search to find relevant chunks
    2. Sends chunks to LLM to generate an answer
    3. Returns the answer with proper citations
    """
    try:
        # First, perform similarity search to find relevant chunks
        search_request = SimilaritySearchRequest(
            query=request.question,
            k=request.k,
            min_score=request.min_score
        )
        
        search_response = await similarity_search(search_request)
        
        if not search_response.results:
            return QuestionAnswerResponse(
                answer="I couldn't find any relevant information to answer your question.",
                citations=[]
            )
        
        # Prepare context from search results
        context = ""
        citations = []
        
        for i, result in enumerate(search_response.results):
            context += f"\n\nCHUNK {i+1}:\n{result.text}\n"
            context += f"SOURCE: {result.metadata.source_doc_id}, SECTION: {result.metadata.section_heading}\n"
            
            citation = Citation(
                source_doc_id=result.metadata.source_doc_id,
                section_heading=result.metadata.section_heading,
                link=result.metadata.link
            )
            citations.append(citation)
        
        # Generate answer using OpenAI
        answer = generate_answer(request.question, context)
        
        return QuestionAnswerResponse(
            answer=answer,
            citations=citations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")
