import requests
from config import CONTENTSTACK_API_KEY, CONTENTSTACK_DELIVERY_TOKEN, CONTENTSTACK_ENVIRONMENT

GRAPHQL_URL = f"https://eu-graphql.contentstack.com/stacks/{CONTENTSTACK_API_KEY}?environment={CONTENTSTACK_ENVIRONMENT}"

HEADERS = {
    "Content-Type": "application/json",
    "access_token": CONTENTSTACK_DELIVERY_TOKEN
}

# Hardcoded locales (you can update with your stack's locales)
LOCALES = ["en-us", "hi-in", "mr-in"]


def fetch_entries(content_type_uid, locale, limit=50, skip=0):
    """
    Fetch entries for a content_type_uid and locale with pagination.
    Returns a list of entries with locale info.
    """
    query = f"""
    query {{
      all_{content_type_uid}(limit: {limit}, skip: {skip}, locale: "{locale}") {{
        items {{
          title
          body
        }}
      }}
    }}
    """
    resp = requests.post(GRAPHQL_URL, headers=HEADERS, json={"query": query})
    if resp.status_code != 200:
        print(f"❌ Fetch entries failed. Response: {resp.text}")
        resp.raise_for_status()

    data = resp.json()
    return data["data"][f"all_{content_type_uid}"]["items"]

    """
    Fetch all entries for a content_type_uid.
    Returns a list of entries with locale info.
    """
    query = f"""
    query {{
      all_{content_type_uid} {{
        items {{
        title
        body
        }}
      }}
    }}
    """
    resp = requests.post(GRAPHQL_URL, headers=HEADERS, json={"query": query})
    if resp.status_code != 200:
        print(f"❌ Fetch entries failed. Response: {resp.text}")
        resp.raise_for_status()

    data = resp.json()
    return data["data"][f"all_{content_type_uid}"]["items"]
