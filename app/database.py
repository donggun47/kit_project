from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from langchain_openai import OpenAIEmbeddings
from app.models import Base
from langchain_pinecone import Pinecone
import os

# --- SQL Connectivity (Supports local SQLite & Cloud Supabase) ---
DEFAULT_DB_URL = "sqlite:///./smma.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Use NullPool for PostgreSQL (Supabase) to avoid connection pooling issues in serverless
engine_args = {}
if DATABASE_URL.startswith("postgresql"):
    engine_args["poolclass"] = NullPool
else:
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes the SQLite database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        print("SQL Database initialized successfully.")
    except Exception as e:
        print(f"SQL Initialization error: {e}")

# --- Vector Connectivity (Migrated to Pinecone for persistence) ---
def get_vector_store(api_key: str):
    """Initializes and returns the cloud Pinecone vector store."""
    pc_api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "smma-brains")
    
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    
    vector_store = Pinecone(
        index_name=index_name,
        embedding=embeddings,
        pinecone_api_key=pc_api_key
    )
    return vector_store
 
