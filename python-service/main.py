import os
import logging
from fastapi import FastAPI, Request
from redis import Redis
from rq import Queue
from dotenv import load_dotenv
from worker import process_entry
from utils import strip_html_tags

load_dotenv()
app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Redis connection & queue
redis_conn = Redis(host="localhost", port=6379)
queue = Queue("contentstack", connection=redis_conn)

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
            return {"status": "skipped"}

        job_data = {
            "uid": uid,
            "title": title,
            "body": body,
            "locale": locale,
            "content_type": content_type,
            "event": event
        }

        # Enqueue job for background processing
        queue.enqueue(process_entry, job_data)
        return {"status": "queued", "uid": uid}

    except Exception as e:
        logging.error(f"❌ Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}
