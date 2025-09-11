import os
import json
import time
import logging
import redis
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Redis connection
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Pinecone setup
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX")
index = pc.Index(index_name)

def process_job(job_data: dict):
    """Process a single job: embed + Pinecone upsert/delete."""
    uid = job_data["uid"]
    title = job_data["title"]
    body = job_data["body"]
    locale = job_data["locale"]
    content_type = job_data["content_type"]
    event = job_data["event"]

    text_to_embed = f"{title} {body}".strip()
    vector = model.encode(text_to_embed).tolist()
    vector_id = f"{locale}_{uid}"

    metadata = {
        "title": title,
        "body": body,
        "locale": locale,
        "content_type": content_type,
    }

    if event in ["create", "update", "entry.create", "entry.update"]:
        index.upsert([{"id": vector_id, "values": vector, "metadata": metadata}])
        logging.info(f"✅ Upserted entry {vector_id} into Pinecone")

    elif event in ["delete", "entry.delete"]:
        index.delete(ids=[vector_id])
        logging.info(f"🗑️ Deleted entry {vector_id} from Pinecone")

    else:
        logging.warning(f"⚠️ Unhandled event type: {event}")

def worker_loop():
    logging.info("🚀 Worker started, waiting for jobs...")
    while True:
        _, job_json = redis_client.blpop("contentstack_jobs")  # blocking pop
        job = json.loads(job_json)
        logging.info(f"⚡ Processing job: {job['uid']}")
        try:
            process_job(job)
        except Exception as e:
            logging.error(f"❌ Failed to process job {job['uid']}: {str(e)}")

if __name__ == "__main__":
    worker_loop()
