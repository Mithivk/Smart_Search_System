from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
from embedding_client import encode_texts
from pinecone_client import query_vector, upsert_vectors
from contentstack_client import fetch_entry_by_uid
from config import WEBHOOK_SECRET, API_KEY_FOR_ADMIN
from typing import List

app = FastAPI(title="Contentstack Semantic Search API")

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    content_type: str = ""   # optional namespace
    locale: str = ""         # optional

@app.post("/search")
async def search(req: SearchRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="query required")
    vec = encode_texts([req.query])[0].tolist()
    res = query_vector(vec, top_k=req.top_k, namespace=req.content_type or "")
    hits = []
    for m in res.get("matches", []):
        hits.append({
            "id": m["id"],
            "score": m["score"],
            "metadata": m.get("metadata", {})
        })
    return {"results": hits}

# Webhook from Contentstack: expects JSON with content_type, uid, action (publish/delete)
@app.post("/webhook/reindex")
async def webhook_reindex(request: Request, background: BackgroundTasks):
    # optional simple verification
    if WEBHOOK_SECRET:
        token = request.headers.get("X-Webhook-Secret")
        if token != WEBHOOK_SECRET:
            raise HTTPException(status_code=403, detail="invalid webhook secret")

    payload = await request.json()
    # expected: payload contains content_type uid environment etc; adapt to your webhook format
    content_type = payload.get("content_type") or payload.get("contentType") or payload.get("data",{}).get("type")
    uid = payload.get("uid") or payload.get("data",{}).get("uid")
    locale = payload.get("locale") or payload.get("data",{}).get("locale", "")
    action = payload.get("action") or payload.get("event")

    if not content_type or not uid:
        raise HTTPException(status_code=400, detail="invalid payload")

    # reindex in background (still triggered synchronously; code runs now)
    background.add_task(reindex_single_entry, content_type, uid, locale)
    return {"status": "reindex scheduled", "content_type": content_type, "uid": uid}

def reindex_single_entry(content_type_uid: str, uid: str, locale: str = ""):
    # fetch entry from Contentstack
    entry = fetch_entry_by_uid(content_type_uid, uid, locale=locale or None)
    if not entry:
        return
    text = (entry.get("title") or "") + " " + (entry.get("body") or entry.get("description") or "")
    embedding = encode_texts([text])[0].tolist()
    vector_id = f"{content_type_uid}:{locale}:{uid}"
    metadata = {"title": entry.get("title"), "uid": uid, "locale": locale}
    upsert_vectors([(vector_id, embedding, metadata)], namespace=content_type_uid)

# admin endpoint to reindex full content type (protected by API_KEY_FOR_ADMIN)
class ReindexAllRequest(BaseModel):
    content_type: str
    locales: List[str] = ["en-us"]

@app.post("/reindex/all")
async def reindex_all(req: ReindexAllRequest, request: Request, background: BackgroundTasks):
    api_key = request.headers.get("X-Admin-Key")
    if API_KEY_FOR_ADMIN and api_key != API_KEY_FOR_ADMIN:
        raise HTTPException(status_code=403, detail="forbidden")
    # trigger background indexing (runs now)
    background.add_task(index_full_content_type, req.content_type, req.locales)
    return {"status": "reindex started", "content_type": req.content_type}

# Use the indexing function we built earlier
from indexing import index_content_type as index_content_type_fn

def index_full_content_type(content_type, locales):
    index_content_type_fn(content_type, locales)
