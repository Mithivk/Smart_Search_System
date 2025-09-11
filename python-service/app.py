import os
import json
import re
import logging
import redis
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Import your embedding and Pinecone clients
from embedding_client import encode_texts
from pinecone_client import query_vector

load_dotenv()

app = FastAPI(title="Contentstack Semantic Search & Webhook API")

# -------------------------------
# Logging
# -------------------------------
logging.basicConfig(level=logging.INFO)

# -------------------------------
# Redis connection
# -------------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))  # cache TTL in seconds
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# -------------------------------
# Helper functions
# -------------------------------
def strip_html_tags(text: str) -> str:
    """Remove HTML tags from a string."""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text or "").strip()

# -------------------------------
# Webhook API
# -------------------------------
@app.post("/webhook")
async def webhook_receiver(request: Request):
    payload = await request.json()
    logging.info(f"📩 Webhook received: {payload}")

    try:
        event = payload.get("event")
        data = payload.get("data", {})

        entry_data = data.get("entry", {})
        content_type_data = data.get("content_type", {})

        uid = entry_data.get("uid")
        title = strip_html_tags(entry_data.get("title", ""))
        body = strip_html_tags(entry_data.get("body", ""))
        locale = entry_data.get("locale", "en-us")
        content_type = content_type_data.get("uid", "unknown")

        if not uid or not (title or body):
            logging.warning("⚠️ Skipping: missing uid, title, or body")
            return {"status": "skipped"}

        job = {
            "event": event,
            "uid": uid,
            "title": title,
            "body": body,
            "locale": locale,
            "content_type": content_type,
        }

        # Push job to Redis list (queue)
        redis_client.rpush("contentstack_jobs", json.dumps(job))
        logging.info(f"📌 Job queued: {uid}")

        return {"status": "queued", "id": uid}

    except Exception as e:
        logging.error(f"❌ Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

# -------------------------------
# Search API with Redis caching
# -------------------------------
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/search")
async def search(req: SearchRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="Query required")

    # Normalize query for cache key
    cache_key = f"search:{req.query.strip().lower()}:{req.top_k}"
    
    # Check cache first
    cached = redis_client.get(cache_key)
    if cached:
        logging.info("⚡ Returning cached search results")
        return json.loads(cached)

    # Encode query
    vec = encode_texts([req.query])[0].tolist()
    
    # Query Pinecone
    res = query_vector(vec, top_k=req.top_k)

    hits = []
    for m in res.get("matches", []):
        hits.append({
            "id": m["id"],
            "score": m["score"],
            "metadata": m.get("metadata", {})
        })

    # Store results in Redis cache
    redis_client.setex(cache_key, REDIS_TTL, json.dumps({"results": hits}))
    logging.info("✅ Search results cached")

    return {"results": hits}
