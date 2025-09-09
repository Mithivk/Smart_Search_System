from sentence_transformers import SentenceTransformer

# Multilingual model
model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')

def encode_texts(texts):
    """
    Returns embeddings for a list of texts.
    """
    return model.encode(texts)
