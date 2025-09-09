from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_API_KEY, PINECONE_INDEX, PINECONE_CLOUD, PINECONE_REGION

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if it doesn't exist
if PINECONE_INDEX not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX,
        dimension=512,
        metric="cosine",
        spec=ServerlessSpec(
            cloud=PINECONE_CLOUD,
            region=PINECONE_REGION
        )
    )

index = pc.Index(PINECONE_INDEX)

def upsert_vectors(vectors):
    index.upsert(vectors=vectors)

def query_vector(vector, top_k=5):
    return index.query(vector=vector, top_k=top_k, include_metadata=True)
