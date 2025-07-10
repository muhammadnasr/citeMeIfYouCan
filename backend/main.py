from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import settings
from api.routes import router
from services.pinecone_service import initialize_pinecone
from utils.helpers import get_logger

# Configure logger
logger = get_logger("cite_me_if_you_can")

# Initialize FastAPI app
app = FastAPI(
    title="Cite Me If You Can API",
    description="API for scientific journal semantic search",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(router)

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    logger.info("Initializing services...")
    initialize_pinecone()
    logger.info("Services initialized")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
