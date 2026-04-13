from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn
import logging
import sys
import os
import io

# Import our custom modules (Relative imports for cloud compatibility)
from .secret_manager import get_secret
from .database import init_db, SessionLocal, get_vector_store
from .models import ChatMessage
from .services import SMMAService
from .consolidation import discover_relationships
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SMMA-Backend")

app = FastAPI(title="SMMA (Semantic Mind-Map Archive) API", version="1.1.0")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files Mounting
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- Global Config ---
OPENAI_API_KEY = None

@app.on_event("startup")
def startup_event():
    global OPENAI_API_KEY
    logger.info("Initializing SMMA Backend...")
    try:
        OPENAI_API_KEY = get_secret("OPENAI_API_KEY", "Enter OpenAI API Key: ")
        logger.info("API Key loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load API Key: {e}")
    init_db()

# --- API Models ---
class IngestRequest(BaseModel):
    title: str
    content: str
    source_type: str = "manual"

class ChatRequest(BaseModel):
    message: str

# --- Routes ---
@app.get("/")
def read_index():
    index_path = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/graph/data")
def get_graph_data():
    try:
        return SMMAService.get_graph_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
def ingest_data(req: IngestRequest):
    try:
        archive_id = SMMAService.ingest_data(req.title, req.content, req.source_type, OPENAI_API_KEY)
        return {"status": "success", "id": archive_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat_interaction(req: ChatRequest):
    try:
        return SMMAService.chat_interaction(req.message, OPENAI_API_KEY)
    except Exception as e:
        logger.error(f"Chat service error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history")
def get_chat_history():
    from .database import SessionLocal
    from .models import ChatMessage
    db = SessionLocal()
    try:
        msgs = db.query(ChatMessage).order_by(ChatMessage.timestamp.asc()).limit(50).all()
        return [{"role": m.role, "content": m.content, "topic": m.topic_tag} for m in msgs]
    finally:
        db.close()

@app.post("/analyze/discover")
def run_discovery():
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="API Key missing")
    return discover_relationships(OPENAI_API_KEY)

@app.delete("/archive/{archive_id}")
def delete_archive(archive_id: str):
    try:
        success = SMMAService.delete_archive(archive_id, OPENAI_API_KEY)
        return {"status": "success" if success else "not_found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
 
