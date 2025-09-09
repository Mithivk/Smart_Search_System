import os
from dotenv import load_dotenv

load_dotenv()

# Contentstack
CONTENTSTACK_API_KEY = os.getenv("CONTENTSTACK_API_KEY")
CONTENTSTACK_DELIVERY_TOKEN = os.getenv("CONTENTSTACK_ACCESS_TOKEN")
CONTENTSTACK_ENVIRONMENT = os.getenv("CONTENTSTACK_ENVIRONMENT", "development")
CONTENTSTACK_BASE_URL = os.getenv("CONTENTSTACK_BASE_URL", "https://cdn.contentstack.io/v3")  # or use GraphQL endpoint if preferred

# Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "contentstack-index")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")        # e.g. "aws" or "gcp"
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1") # e.g. "us-east-1"

# Embedding model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/distiluse-base-multilingual-cased-v2")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "512"))

# Security
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")  # optional: secret to validate Contentstack webhook
API_KEY_FOR_ADMIN = os.getenv("ADMIN_API_KEY")  # optional simple protection for reindex endpoints

# Misc
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))
