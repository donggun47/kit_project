from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from .models import Base
import os

# --- SQL Connectivity ---
DATABASE_URL = "sqlite:///./smma.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes the SQLite database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        print("SQL Database initialized successfully.")
    except Exception as e:
        print(f"SQL Initialization error: {e}")

# --- Vector Connectivity ---
def get_vector_store(api_key: str):
    """Initializes and returns the local Chroma vector store."""
    persist_directory = "./chroma_db"
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    
    vector_store = Chroma(
        collection_name="smma_memories",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    return vector_store
