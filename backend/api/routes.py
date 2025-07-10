from fastapi import APIRouter
from .upload import router as upload_router
from .search import router as search_router
from .qa import router as qa_router

# Create main router
router = APIRouter()

# Include all routers
router.include_router(upload_router)
router.include_router(search_router)
router.include_router(qa_router)
