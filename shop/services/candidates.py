import re
import pymongo
from django.conf import settings


client = pymongo.MongoClient(settings.MONGODB_URI)
db = client["ecommerce_db"]
product_collection = db["products"]


STOPWORDS = {
    "the", "a", "an", "for", "with", "and", "or",
    "to", "of", "in", "on", "my", "i", "want", "need"
}

def tokenize(text: str) -> list[str]:
    text = (text or "").lower()
    words = re.findall(r"[a-z0-9]+", text)
    return [w for w in words if w not in STOPWORDS]


def get_candidates(user_query: str, limit: int = 30):
    tokens = tokenize(user_query)

    products = list(
        product_collection.find().sort("popularity", -1).limit(200)
    )

    scored = []

    for p in products:
        tags = p.get("tags", [])
        name = p.get("name", "")
        popularity = p.get("popularity", 0)

        tag_overlap = sum(
            1 for t in tags if str(t).lower() in tokens
        )

        name_overlap = sum(
            1 for w in tokenize(name) if w in tokens
        )

        score = (popularity * 0.05) + (tag_overlap * 2) + (name_overlap * 1)

        if score > 0:
            scored.append((p, score))

    ranked = sorted(scored, key=lambda x: x[1], reverse=True)


    return [p for p, _ in ranked[:limit]]