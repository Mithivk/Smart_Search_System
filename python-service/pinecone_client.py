# pinecone_client.py
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables from .env
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")  # optional
INDEX_NAME = os.getenv("PINECONE_INDEX")

# sanity check
if not PINECONE_API_KEY or not INDEX_NAME:
    raise ValueError("PINECONE_API_KEY and PINECONE_INDEX must be set in environment variables")

# Create Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

# Check if index exists, create if not
existing_indexes = [i.name for i in pc.list_indexes()]
if INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=INDEX_NAME,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-west-2")
    )

# Connect to the index
index = pc.Index(INDEX_NAME)

# -------------------------------
# Upsert a vector
# -------------------------------
def upsert_vector(vector_id: str, vector: list, metadata: dict):
    """
    Upsert a single vector into Pinecone
    """
    index.upsert([{"id": vector_id, "values": vector, "metadata": metadata}])

# -------------------------------
# Query vectors
# -------------------------------
def query_vector(vector: list, top_k: int = 5,filter: dict = None):
    """
    Query Pinecone index and return top_k results
    """
    res = index.query(vector=vector, top_k=top_k, include_metadata=True)
    return res
