# indexing.py

from contentstack_client import fetch_entries, LOCALES
from embedding_client import encode_texts
from pinecone_client import upsert_vectors

BATCH_SIZE = 50
CONTENT_TYPE_UID = "page"

def extract_text_from_richtext(richtext_field):
    """
    Converts Contentstack Rich Text JSON to plain text.
    """
    if not richtext_field:
        return ""
    if isinstance(richtext_field, str):
        return richtext_field
    if isinstance(richtext_field, dict):
        # Rich Text JSON often has a 'html' key
        return richtext_field.get("html", "")
    return ""

print(f"Indexing content type '{CONTENT_TYPE_UID}' for locales: {LOCALES}")

for locale in LOCALES:
    skip = 0
    while True:
        entries = fetch_entries(CONTENT_TYPE_UID, locale, skip=skip, limit=BATCH_SIZE)
        if not entries:
            break

        vectors = []
        for idx, entry in enumerate(entries):
            title = entry.get("title", "")
            body = extract_text_from_richtext(entry.get("body", ""))
            text = f"{title} {body}".strip()
            if not text:
                continue

            embedding = encode_texts([text])[0]
            vectors.append({
                "id": f"{locale}_{skip}_{idx}",  # unique per locale & batch
                "values": embedding.tolist(),
                "metadata": {
                    "title": title,
                    "body": body,
                    "locale": locale
                }
            })

        if vectors:
            upsert_vectors(vectors)
            print(f"Inserted {len(vectors)} vectors for locale '{locale}' (skip={skip})")

        skip += BATCH_SIZE

print("✅ Indexing completed for all locales.")
