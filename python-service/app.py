from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List
from embedding_client import encode_texts
from pinecone_client import query_vector, upsert_vectors
# from contentstack_client import fetch_entry_by_uid
# from indexing import index_content_type  # use our final indexing function
from config import WEBHOOK_SECRET, API_KEY_FOR_ADMIN

app = FastAPI(title="Contentstack Semantic Search API")


# -------------------------------
# Search API
# -------------------------------
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    content_type: str = ""  # optional namespace
    locale: str = ""        # optional


@app.post("/search")
async def search(req: SearchRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="query required")
    
    # encode query
    vec = encode_texts([req.query])[0].tolist()
    
    # query Pinecone
    res = query_vector(vec, top_k=req.top_k)
    
    hits = []
    for m in res.get("matches", []):
        hits.append({
            "id": m["id"],
            "score": m["score"],
            "metadata": m.get("metadata", {})
        })
    return {"results": hits}


# # -------------------------------
# # Webhook API for single entry reindex
# # -------------------------------
# @app.post("/webhook/reindex")
# async def webhook_reindex(request: Request, background: BackgroundTasks):
#     if WEBHOOK_SECRET:
#         token = request.headers.get("X-Webhook-Secret")
#         if token != WEBHOOK_SECRET:
#             raise HTTPException(status_code=403, detail="invalid webhook secret")
    
#     payload = await request.json()
#     content_type = payload.get("content_type") or payload.get("contentType") or payload.get("data", {}).get("type")
#     uid = payload.get("uid") or payload.get("data", {}).get("uid")
#     locale = payload.get("locale") or payload.get("data", {}).get("locale", "")
    
#     if not content_type or not uid:
#         raise HTTPException(status_code=400, detail="invalid payload")
    
#     background.add_task(reindex_single_entry, content_type, uid, locale)
#     return {"status": "reindex scheduled", "content_type": content_type, "uid": uid}


# def reindex_single_entry(content_type_uid: str, uid: str, locale: str = ""):
#     entry = fetch_entry_by_uid(content_type_uid, uid, locale=locale or None)
#     if not entry:
#         return
    
#     # combine title + body
#     text = (entry.get("title") or "") + " " + (entry.get("body") or "")
#     embedding = encode_texts([text])[0].tolist()
    
#     vector_id = f"{content_type_uid}:{locale}:{uid}"
#     metadata = {"title": entry.get("title"), "uid": uid, "locale": locale, "body": entry.get("body") or ""}
    
#     # upsert into Pinecone
#     upsert_vectors([{"id": vector_id, "values": embedding, "metadata": metadata}], namespace=content_type_uid)


# # -------------------------------
# # Admin API to reindex full content type
# # -------------------------------
# class ReindexAllRequest(BaseModel):
#     content_type: str
#     locales: List[str] = ["en-us"]


# @app.post("/reindex/all")
# async def reindex_all(req: ReindexAllRequest, request: Request, background: BackgroundTasks):
#     api_key = request.headers.get("X-Admin-Key")
#     if API_KEY_FOR_ADMIN and api_key != API_KEY_FOR_ADMIN:
#         raise HTTPException(status_code=403, detail="forbidden")
    
#     background.add_task(index_full_content_type, req.content_type, req.locales)
#     return {"status": "reindex started", "content_type": req.content_type}


# def index_full_content_type(content_type, locales):
#     # call the indexing function from indexing.py
#     index_content_type(content_type, locales)
