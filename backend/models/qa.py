from pydantic import BaseModel
from typing import List

class QuestionAnswerRequest(BaseModel):
    """Request model for question answering"""
    question: str
    k: int = 10
    min_score: float = 0.25

class Citation(BaseModel):
    """Model for a citation in an answer"""
    source_doc_id: str
    section_heading: str
    link: str

class QuestionAnswerResponse(BaseModel):
    """Response model for question answering"""
    answer: str
    citations: List[Citation]
