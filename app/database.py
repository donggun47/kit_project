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

# --- Vector Connectivity (Enhanced with Auto-Creation) ---
def get_vector_store(openai_api_key: str, pinecone_api_key: str = None, index_name: str = "smma-brains"):
    """Initializes and returns the cloud Pinecone vector store. Creates index if missing."""
    import time
    from pinecone import Pinecone as PineconeClient, ServerlessSpec
    
    # Prioritize provided key, then environment variable
    pc_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
    if not pc_api_key:
        raise ValueError("Pinecone API Key is missing. Please configure it in Settings.")

    pc = PineconeClient(api_key=pc_api_key)
    
    # 1. Ensure Index Exists
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    if index_name not in existing_indexes:
        print(f"Index '{index_name}' not found. Creating a new Serverless index...")
        try:
            pc.create_index(
                name=index_name,
                dimension=1536, # OpenAI embedding dimension
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
        except Exception as e:
            if "AlreadyExists" in str(e) or "409" in str(e):
                print(f"Index '{index_name}' is already being created.")
            else:
                raise e

        # Wait until the index is ready
        max_retries = 300  # 5 minutes timeout
        retry_count = 0
        while retry_count < max_retries:
            try:
                status = pc.describe_index(index_name).status
                if status.get('ready'):
                    break
            except Exception:
                pass  # Ignore temporary errors during creation
            time.sleep(1)
            retry_count += 1
            
        if retry_count >= max_retries:
            raise TimeoutError(f"Timeout waiting for Pinecone index '{index_name}' to become ready.")
            
        print(f"Index '{index_name}' created and ready.")

    # 2. Return LangChain Wrapper
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vector_store = Pinecone(
        index_name=index_name,
        embedding=embeddings,
        pinecone_api_key=pc_api_key
    )
    return vector_store
 
