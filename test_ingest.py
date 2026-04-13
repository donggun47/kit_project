import requests
import os
from dotenv import load_dotenv

load_dotenv()
resp = requests.post("http://localhost:8000/ingest", json={
    "title": "Test Memory",
    "content": "This is a test memory",
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "pinecone_api_key": os.getenv("PINECONE_API_KEY")
})
print("STATUS CODE:", resp.status_code)
print("RESPONSE:", resp.text)
