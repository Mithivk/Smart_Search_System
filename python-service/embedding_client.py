# embedding_client.py
from sentence_transformers import SentenceTransformer

# Load model once
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

def encode_texts(texts):
    """Return embeddings for a list of texts"""
    return model.encode(texts)
