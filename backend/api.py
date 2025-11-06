"""FastAPI backend for Local Recall."""
import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db
from embeddings import pipeline
from rag import query_engine
from vector_store import vector_store
from config import settings, ensure_directories


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Pydantic models for API
class KeybindCreate(BaseModel):
    action: str
    key_sequence: str


class DataCreate(BaseModel):
    text: str
    source: Optional[str] = None
    tags: Optional[List[str]] = None


class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = None
    k: Optional[int] = 5


class StatusResponse(BaseModel):
    status: str


# Background task for embedding pipeline
embedding_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting Local Recall backend...")
    ensure_directories()

    # Start embedding pipeline in background
    global embedding_task
    embedding_task = asyncio.create_task(pipeline.start())

    yield

    # Shutdown
    logger.info("Shutting down Local Recall backend...")
    pipeline.stop()
    if embedding_task:
        embedding_task.cancel()


# Create FastAPI app
app = FastAPI(
    title="Local Recall API",
    description="Privacy-preserving local text capture and RAG system",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Keybind endpoints
@app.post("/keybind/selected", response_model=StatusResponse)
async def create_keybind_selected(keybind: KeybindCreate):
    """Create keybind for capturing selected text."""
    try:
        db.add_keybind(action="capture_selected", key_sequence=keybind.key_sequence)
        return StatusResponse(status="success")
    except Exception as e:
        logger.error(f"Error creating keybind: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/keybind/screenshot", response_model=StatusResponse)
async def create_keybind_screenshot(keybind: KeybindCreate):
    """Create keybind for capturing screenshot text."""
    try:
        db.add_keybind(action="capture_screenshot", key_sequence=keybind.key_sequence)
        return StatusResponse(status="success")
    except Exception as e:
        logger.error(f"Error creating keybind: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/keybinds")
async def get_keybinds():
    """Get all active keybinds."""
    try:
        keybinds = db.get_keybinds()
        return [kb.to_dict() for kb in keybinds]
    except Exception as e:
        logger.error(f"Error retrieving keybinds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Data endpoints
@app.post("/data", response_model=StatusResponse)
async def create_data_entry(data: DataCreate):
    """Create a new data entry."""
    try:
        entry = db.add_entry(
            content=data.text,
            source=data.source,
            capture_method="api",
            tags=data.tags
        )
        logger.info(f"Created entry {entry.id}")
        return StatusResponse(status="success")
    except Exception as e:
        logger.error(f"Error creating data entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data")
async def get_data_entries(
    id: Optional[int] = None,
    tag: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 100
):
    """Get data entries with optional filters."""
    try:
        filters = {}
        if id:
            filters["id"] = id
        if tag:
            filters["tag"] = tag
        if source:
            filters["source"] = source

        entries = db.get_entries(filters=filters, limit=limit)
        return [entry.to_dict() for entry in entries]
    except Exception as e:
        logger.error(f"Error retrieving data entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/data/{entry_id}", response_model=StatusResponse)
async def delete_data_entry(entry_id: int):
    """Delete a data entry."""
    try:
        success = db.delete_entry(entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entry not found")
        return StatusResponse(status="success")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/data", response_model=Dict[str, Any])
async def clear_all_entries():
    """Clear all data entries from the database."""
    try:
        count = db.clear_all_entries()
        # Also clear vector store
        vector_store.reset()
        logger.info(f"Cleared all data: {count} entries removed")
        return {
            "status": "success",
            "entries_deleted": count,
            "message": f"Successfully deleted {count} entries and reset vector store"
        }
    except Exception as e:
        logger.error(f"Error clearing all entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Query endpoint
@app.post("/query")
async def query_data(request: QueryRequest):
    """Perform semantic search or RAG query."""
    try:
        if request.model:
            # RAG query with LLM
            result = await query_engine.query_with_rag(
                query=request.query,
                model=request.model
            )
            return result
        else:
            # Semantic search only
            results = await query_engine.semantic_search(
                query=request.query,
                k=request.k
            )
            return {"results": results}
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System control endpoints
@app.post("/control/start", response_model=StatusResponse)
async def start_capture():
    """Start background data capture."""
    try:
        db.set_capturing(True)
        logger.info("Data capture started")
        return StatusResponse(status="started")
    except Exception as e:
        logger.error(f"Error starting capture: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/control/stop", response_model=StatusResponse)
async def stop_capture():
    """Stop background data capture."""
    try:
        db.set_capturing(False)
        logger.info("Data capture stopped")
        return StatusResponse(status="stopped")
    except Exception as e:
        logger.error(f"Error stopping capture: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Get system status."""
    try:
        stats = db.get_stats()
        state = db.get_system_state()
        vector_stats = vector_store.get_stats()

        return {
            "capturing": state.is_capturing if state else False,
            "database": stats,
            "vector_store": vector_stats,
            "backend_version": "0.1.0"
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.BACKEND_PORT)
