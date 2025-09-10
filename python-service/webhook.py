import os
import logging
import re
from fastapi import FastAPI, Request, BackgroundTasks
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Load embedding model (same as indexing.py)
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Pinecone setup
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX")
index = pc.Index(index_name)


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from a string."""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text or "").strip()


def process_webhook(payload: dict):
    """Process webhook in background."""
    try:
        event = payload.get("event")
        data = payload.get("data", {})

        # Extract entry and content type correctly
        entry_data = data.get("entry", {})
        content_type_data = data.get("content_type", {})

        uid = entry_data.get("uid")
        title = strip_html_tags(entry_data.get("title", ""))
        body = strip_html_tags(entry_data.get("body", ""))
        locale = entry_data.get("locale", "en-us")
        content_type = content_type_data.get("uid", "unknown")

        if not uid or not (title or body):
            logging.warning("⚠️ Skipping: missing uid, title, or body")
            return

        # Combine title + body
        text_to_embed = f"{title} {body}".strip()
        vector = model.encode(text_to_embed).tolist()
        vector_id = f"{locale}_{uid}"

        metadata = {"title": title, "body": body, "locale": locale, "content_type": content_type}

        # Handle create/update
        if event in ["create", "update", "entry.create", "entry.update"]:
            index.upsert([{"id": vector_id, "values": vector, "metadata": metadata}])
            logging.info(f"✅ Upserted entry {vector_id} into Pinecone")

        # Handle delete
        elif event in ["delete", "entry.delete"]:
            index.delete(ids=[vector_id])
            logging.info(f"🗑️ Deleted entry {vector_id} from Pinecone")

        else:
            logging.warning(f"⚠️ Unhandled event type: {event}")

    except Exception as e:
        logging.error(f"❌ Error processing webhook: {str(e)}")


@app.post("/webhook")
async def webhook_receiver(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    logging.info(f"📩 Webhook received: {payload}")

    # Run heavy processing in background
    background_tasks.add_task(process_webhook, payload)

    # Respond immediately to Contentstack
    return {"status": "received"}
