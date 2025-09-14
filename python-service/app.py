from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis
import os
import json
import re
import logging
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
from typing import List, Optional, Dict, Any, Generator
import asyncio
import google.generativeai as genai
import numpy as np
from collections import defaultdict
from fastapi.responses import JSONResponse
from embedding_client import encode_texts
from pinecone_client import query_vector
from langdetect import detect, DetectorFactory

# Load cross-encoder for reranking
try:
    from sentence_transformers import CrossEncoder
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
    RERANKER_AVAILABLE = True
except ImportError:
    try:
        reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        RERANKER_AVAILABLE = True
    except:
        reranker = None
        RERANKER_AVAILABLE = False
        logging.warning("CrossEncoder not available. Reranking will be disabled.")

load_dotenv()

app = FastAPI(title="Contentstack Semantic Search & Webhook API")

# -------------------------------
# CORS Setup
# -------------------------------
origins = [
    "http://localhost:3000",
    "https://66d0215dae31.ngrok-free.app",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Logging
# -------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# Configuration
# -------------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "techsurf")

# Search configuration
MIN_SCORE_THRESHOLD = float(os.getenv("MIN_SCORE_THRESHOLD", -15))
INITIAL_CANDIDATES = int(os.getenv("INITIAL_CANDIDATES", 50))
RERANK_ENABLED = os.getenv("RERANK_ENABLED", "true").lower() == "true"
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 200))  # Words per chunk

# LLM configuration for query expansion
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
LLM_ENABLED = os.getenv("LLM_ENABLED", "false").lower() == "true" and LLM_API_KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
GEMINI_MODEL = "gemini-1.5-pro"
DetectorFactory.seed = 0

# -------------------------------
# Service Connections
# -------------------------------
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
config_collection = db["configs"]


# -------------------------------
# Helper functions
# -------------------------------
def strip_html_tags(text: str) -> str:
    """Remove HTML tags from a string."""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text or "").strip()

def chunk_text(text: str, chunk_size: int = 200) -> Generator[str, None, None]:
    """
    Split text into chunks of approximately chunk_size words.
    """
    if not text:
        return
    
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])

def normalize_vector(vec: np.ndarray) -> np.ndarray:
    """Normalize vector to unit length for consistent cosine similarity."""
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm

async def prepare_document_vectors(uid: str, title: str, body: str, locale: str, content_type: str) -> List[Dict]:
    """
    Prepare chunked embeddings for a document with title and body chunks.
    """
    vectors = []
    
    # Encode and add title as separate chunk
    if title:
        title_vec = encode_texts([title])[0]
        title_vec_normalized = normalize_vector(title_vec)
        vectors.append({
            "id": f"{uid}_title",
            "values": title_vec_normalized.tolist(),
            "metadata": {
                "doc_id": uid,
                "title": title,
                "chunk_type": "title",
                "locale": locale,
                "content_type": content_type,
                "text": title
            }
        })
    
    # Encode body in chunks
    if body:
        for chunk_idx, chunk in enumerate(chunk_text(body, CHUNK_SIZE)):
            chunk_vec = encode_texts([chunk])[0]
            chunk_vec_normalized = normalize_vector(chunk_vec)
            vectors.append({
                "id": f"{uid}_body_{chunk_idx}",
                "values": chunk_vec_normalized.tolist(),
                "metadata": {
                    "doc_id": uid,
                    "title": title,
                    "chunk_type": "body",
                    "chunk_index": chunk_idx,
                    "locale": locale,
                    "content_type": content_type,
                    "text": chunk
                }
            })
    
    logger.info(f"Prepared {len(vectors)} vectors for document {uid}")
    return vectors

async def llm_query_expansion(query: str) -> List[str]:
    """
    Use LLM to generate intelligent query variations and paraphrases.
    """
    if not LLM_ENABLED or not query or len(query.split()) > 3:
        return [query]
    
    cache_key = f"llm_expansion:{query.lower()}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    prompt = f"""
    Generate 3-5 semantic search query variations for: "{query}"
    Focus on synonyms, related concepts, and natural language expressions.
    Return ONLY a JSON array of strings.
    Example: ["urban traffic congestion", "city traffic jams", "road congestion problems"]
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a search query optimization expert. Return only JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 150
            }
            
            async with session.post(LLM_API_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"].strip()
                    
                    # Extract JSON array from response
                    variations = json.loads(content)
                    if isinstance(variations, list) and all(isinstance(v, str) for v in variations):
                        variations = [query] + variations[:4]  # Keep 4 LLM variations + original
                        redis_client.setex(cache_key, REDIS_TTL * 24, json.dumps(variations))
                        logger.info(f"LLM generated variations: {variations}")
                        return variations
    except Exception as e:
        logger.warning(f"LLM query expansion failed: {str(e)}")
    
    return [query]

async def translate_text(text: str, target_lang: str) -> str:
    """
    Translate given text into target_lang using Gemini with strict chat instructions.
    """
    if not text or not target_lang or target_lang == "en":
        return text

    lang_map = {
        "en": "English",
        "mr": "Marathi",
        "hi": "Hindi", 
        "kn": "Kannada",
        "ta": "Tamil",
        "te": "Telugu",
        "gu": "Gujarati",
        "bn": "Bengali",
        "pa": "Punjabi",
        "ml": "Malayalam",
        "or": "Odia",
        "ur": "Urdu",
        "ne": "Nepali"
    }

    target_lang_full = lang_map.get(target_lang, "English")

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Start a chat with very clear system instructions
        chat = model.start_chat(history=[
            {
                "role": "user",
                "parts": ["You are a translation machine. Your only function is to translate text. Never provide explanations, options, or additional text. Only output the translated text."]
            },
            {
                "role": "model", 
                "parts": ["Understood. I will only output the translated text with no additional content, explanations, or options."]
            },
            {
                "role": "user",
                "parts": ["Translate 'Hello world' to Hindi"]
            },
            {
                "role": "model",
                "parts": ["नमस्ते दुनिया"]
            }
        ])
        
        prompt = f"Translate this to {target_lang_full}: {text}"
        response = chat.send_message(prompt)
        translated = response.text.strip()
        
        return translated

    except Exception as e:
        logger.warning(f"Translation failed: {str(e)}")
        return text

def expand_query_semantically(query: str) -> str:
    """
    Basic semantic expansion for short queries using known patterns.
    """
    if len(query.split()) > 2:
        return query
    
    expansion_map = {
        r"\btraffic\b": "urban traffic congestion city roads jam",
        r"\bflower\b": "flowers gardening plants blossom bloom",
        r"\bcheap\b": "affordable inexpensive budget low cost",
        r"\bhobby\b": "hobbies leisure activity pastime",
        r"\bjogging\b": "running exercise fitness workout",
        r"\bcity\b": "big city metropolis urban",
        r"\bhappy\b": "joyful happiness contentment",
    }
    
    expanded_query = query
    for pattern, expansion in expansion_map.items():
        if re.search(pattern, query, re.IGNORECASE):
            expanded_query += " " + expansion
            break
    
    if expanded_query == query:
        expanded_query = f"{query} related article blog post"
    
    logger.info(f"Expanded query: '{query}' -> '{expanded_query}'")
    return expanded_query

def aggregate_document_scores(matches: List[Dict]) -> List[Dict]:
    """
    Aggregate scores from multiple chunks to document-level scoring.
    Updated to work with current metadata structure.
    """
    doc_scores = defaultdict(float)
    doc_metadata = {}
    doc_chunk_count = defaultdict(int)
    
    for match in matches:
        metadata = match.get('metadata', {})
        
        # Use the document ID from the vector ID (since doc_id is missing)
        vector_id = match['id']
        if '_' in vector_id:
            # Extract doc ID from vector ID like "en-us_blt8f64b5c866280d11"
            doc_id = vector_id.split('_')[0] + '_' + vector_id.split('_')[1]
        else:
            doc_id = vector_id  # Fallback
            
        # Use max score for the document
        doc_scores[doc_id] = max(doc_scores[doc_id], match['score'])
        doc_chunk_count[doc_id] += 1
        
        # Store metadata from the highest scoring chunk
        if doc_id not in doc_metadata or match['score'] > doc_scores[doc_id]:
            doc_metadata[doc_id] = metadata
    
    # Create final results with document-level scoring
    aggregated_results = []
    for doc_id, score in doc_scores.items():
        aggregated_results.append({
            'id': doc_id,
            'score': score,
            'metadata': doc_metadata[doc_id],
            'chunk_matches': doc_chunk_count[doc_id]
        })
    
    # Sort by score descending
    aggregated_results.sort(key=lambda x: x['score'], reverse=True)
    return aggregated_results


def rerank_results(query: str, candidates: List[Dict], top_k: int) -> List[Dict]:
    """
    Re-rank search results using cross-encoder for better precision.
    """
    if not candidates or not RERANK_ENABLED or not RERANKER_AVAILABLE:
        return candidates[:top_k]
    
    try:
        # Prepare document texts for reranking
        doc_texts = []
        valid_candidates = []
        
        for candidate in candidates:
            metadata = candidate.get("metadata", {})
            doc_text = f"{metadata.get('title', '')} {metadata.get('text', '')}".strip()
            if doc_text:
                doc_texts.append(doc_text)
                valid_candidates.append(candidate)
        
        if not doc_texts:
            return candidates[:top_k]
        
        # Create query-document pairs for reranking
        pairs = [(query, doc_text) for doc_text in doc_texts]
        reranker_scores = reranker.predict(pairs)
        
        # Update candidate scores - use ONLY reranker score
        for i, candidate in enumerate(valid_candidates):
            candidate["reranker_score"] = float(reranker_scores[i])
            candidate["final_score"] = candidate["reranker_score"]
        
        valid_candidates.sort(key=lambda x: x["final_score"], reverse=True)
        logger.info(f"Reranked {len(valid_candidates)} candidates")
        return valid_candidates[:top_k]
        
    except Exception as e:
        logger.error(f"Reranking failed: {str(e)}")
        return candidates[:top_k]

# -------------------------------
# Webhook API (Updated for chunked embeddings)
# -------------------------------
@app.post("/webhook")
async def webhook_receiver(request: Request):
    payload = await request.json()
    logger.info(f"📩 Webhook received: {payload}")

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
            logger.warning("⚠️ Skipping: missing uid, title, or body")
            return {"status": "skipped"}

        # Prepare chunked embeddings
        vectors = await prepare_document_vectors(uid, title, body, locale, content_type)
        
        # Upsert to Pinecone
        if vectors:
            upsert_vectors(vectors)
            logger.info(f"✅ Successfully upserted {len(vectors)} chunks for {uid}")

        # Also store in Redis queue for backup processing
        job = {
            "event": event,
            "uid": uid,
            "title": title,
            "body": body,
            "locale": locale,
            "content_type": content_type,
        }
        redis_client.rpush("contentstack_jobs", json.dumps(job))

        return {"status": "success", "chunks_created": len(vectors), "id": uid}

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

# -------------------------------
# Search API with Chunked Embeddings
# -------------------------------
# -------------------------------
# Search API with Chunked Embeddings
# -------------------------------
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    use_reranking: bool = True
    target_lang: Optional[str] = None  # <--- add this line

@app.post("/search")
async def search(req: SearchRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="Query required")

    # Step 1: Detect query language FIRST
    try:
        detected_lang = detect(req.query)
        logger.info(f"Detected query language: {detected_lang}")
    except:
        detected_lang = "en"
        logger.warning("Language detection failed, defaulting to English")

    # Use detected language as target language if none specified
    target_lang = req.target_lang if req.target_lang else detected_lang
    logger.info(f"Target translation language: {target_lang}")

    cache_key = f"search:{req.query.strip().lower()}:{req.top_k}:{req.use_reranking}:{target_lang}"
    cached = redis_client.get(cache_key)
    if cached:
        logger.info("⚡ Returning cached search results")
        return json.loads(cached)

    try:
        # Step 2: Expand query
        expanded_query = expand_query_semantically(req.query)
        # Step 3: Encode query
        query_vec = encode_texts([expanded_query])[0]
        query_vec_normalized = normalize_vector(query_vec)
        
        # Step 4: Query Pinecone
        res = query_vector(vector=query_vec_normalized.tolist(), top_k=INITIAL_CANDIDATES)
        matches = res.get("matches", [])
        logger.info(f"Raw matches from Pinecone: {len(matches)}")

        if not matches:
            return {"results": []}

        # Step 5: Aggregate and rerank
        aggregated_results = aggregate_document_scores(matches)
        logger.info(f"Aggregated documents: {len(aggregated_results)}")

        if req.use_reranking and len(aggregated_results) > 1:
            final_results = rerank_results(req.query, aggregated_results, req.top_k)
            logger.info(f"🔎 Final results after reranking: {len(final_results)}")
        else:
            final_results = aggregated_results[:req.top_k]

        # Step 6: Filter by MIN_SCORE_THRESHOLD
        hits = []
        for r in final_results:
            score = r.get("final_score", r.get("score", 0))
            logger.info(f"Result {r['id']} score={score}, threshold={MIN_SCORE_THRESHOLD}")
            if score >= MIN_SCORE_THRESHOLD:
                hits.append({
                    "id": r['id'],
                    "score": score,
                    "metadata": r['metadata'],
                    "chunk_matches": r.get('chunk_matches', 0),
                    "reranker_score": r.get("reranker_score"),
                    "final_score": score
                })

        # Step 7: Translate results if query language is not English
        if target_lang != "en" and hits:
            logger.info(f"Translating results to: {target_lang}")
            for hit in hits:
                metadata = hit["metadata"]
                
                # Translate title
                if 'title' in metadata and metadata['title']:
                    translated_title = await translate_text(metadata['title'], target_lang)
                    metadata['title_translated'] = translated_title
                
                # Translate body/content
                content_to_translate = metadata.get('body') or metadata.get('text') or metadata.get('title', '')
                if content_to_translate:
                    # Only translate a preview to avoid long texts
                    content_preview = content_to_translate[:200] + "..." if len(content_to_translate) > 200 else content_to_translate
                    translated_content = await translate_text(content_preview, target_lang)
                    metadata['content_translated'] = translated_content
                
                # Add language info
                metadata['original_language'] = 'en'
                metadata['translated_language'] = target_lang

        # Step 8: Cache and return
        if hits:
            redis_client.setex(cache_key, REDIS_TTL, json.dumps({"results": hits}))
        
        logger.info(f"✅ Returning {len(hits)} results to client")
        return {
            "results": hits,
            "query_language": detected_lang,
            "target_language": target_lang
        }

    except Exception as e:
        logger.error(f"❌ Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")# -------------------------------
# Re-indexing Endpoint
# -------------------------------
@app.post("/reindex/all")
async def reindex_all_documents():
    """
    Re-index all documents from MongoDB with proper metadata
    """
    try:
        # Fetch all documents from your collection
        documents = db.your_collection.find({})  # Replace with your actual collection name
        
        total_chunks = 0
        for doc in documents:
            vectors = await prepare_document_vectors(
                doc["uid"],
                doc.get("title", ""),
                doc.get("body", ""),
                doc.get("locale", "en-us"),
                doc.get("content_type", "unknown")
            )
            
            if vectors:
                upsert_vectors(vectors)
                total_chunks += len(vectors)
                logger.info(f"Re-indexed {doc['uid']} with {len(vectors)} chunks")
        
        return {"status": "success", "total_chunks_reindexed": total_chunks}
        
    except Exception as e:
        logger.error(f"Reindexing failed: {str(e)}")
        return {"error": str(e)}


# Add this debug endpoint
@app.get("/debug/document/{doc_id}")
async def debug_document(doc_id: str):
    """
    Check what chunks exist for a specific document
    """
    try:
        # Query with a generic vector to find all chunks for this document
        query_vec = encode_texts(["test"])[0]
        res = query_vector(vector=query_vec.tolist(), top_k=100)
        
        # Filter chunks for this specific document
        doc_chunks = [
            match for match in res.get("matches", [])
            if match['id'].startswith(doc_id) or match.get('metadata', {}).get('doc_id') == doc_id
        ]
        
        return {
            "document_id": doc_id,
            "chunks_found": len(doc_chunks),
            "chunks": [
                {
                    "id": chunk["id"],
                    "score": chunk.get("score", 0),
                    "metadata": chunk.get("metadata", {})
                }
                for chunk in doc_chunks
            ]
        }
        
    except Exception as e:
        return {"error": str(e)}