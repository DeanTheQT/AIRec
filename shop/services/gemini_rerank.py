import json
import re
from .candidates import get_candidates
from google import genai
from django.conf import settings

MODEL = "gemini-2.5-flash"


def rerank_with_gemini(user_query: str, candidates_payload: list[dict], top_k: int):
    """
    Call Gemini AI to rerank candidate products.
    Returns (ranked_ids: list[int], reasons: dict[id->str])
    """

    if not settings.GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = f"""
You are a product recommender for an online shop.

User request:
{user_query}

Candidate products:
{json.dumps(candidates_payload, ensure_ascii=False)}

Return ONLY raw JSON in this exact format:
{{"ranked_product_ids":[1,2,3],"reasons":{{"1":"...","2":"...","3":"..."}}}}

Do NOT wrap the JSON in markdown.
Do NOT include explanations.
Always return at least one product if candidates exist.
Keep reasons short (1 sentence each).
In a scenario that item does not exist, output "NotExist"
"""

    resp = client.models.generate_content(model=MODEL, contents=prompt)
    text = (resp.text or "").strip()

    if not text:
        raise RuntimeError("Gemini returned empty response")

    # Strip markdown code blocks if present
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Gemini returned invalid JSON: {e}; raw text: {text}")

    ranked_ids = data.get("ranked_product_ids", [])
    reasons = data.get("reasons", {})
    
    if ranked_ids == "NotExist" or ranked_ids == ["NotExist"]:
        return "NotExist", {}

    return ranked_ids, reasons


def recommend_products(user_query: str, top_k: int = 8):
    """
    Returns a tuple: (list of (Product, reason), mode)
    mode = "AI" if AI ranking succeeded, "NON_AI" otherwise
    """
    candidates = get_candidates(user_query, limit=30)
    id_to_product = {str(p["_id"]): p for p in candidates}

    payload = [
        {
            "id": str(p["_id"]),
            "name": p.get("name"),
            "category": p.get("category"),
            "tags": p.get("tags", [])[:10],
            "price": float(p.get("price", 0)),
            "description": (p.get("description", "") or "")[:160],
        }
        for p in candidates
    ]

    results = []

    try:
        ranked_ids, reasons = rerank_with_gemini(user_query, payload, top_k=top_k)

        if ranked_ids == "NotExist":
            return [], "ITEM_NOT_FOUND"

        results = [
            (id_to_product[pid], reasons.get(str(pid)) or reasons.get(pid))
            for pid in ranked_ids
            if pid in id_to_product
        ]

        if results:
            return results, "AI"

    except Exception as e:
        error_msg = str(e)
        results = [
            (p, f"Matched by tags/popularity (AI Error: {error_msg})")
            for p in candidates[:top_k]
        ]
        return results, f"NON_AI: {error_msg}"

    if not results:
        results = [
            (p, "Matched by tags/popularity (AI produced no confident ranking)")
            for p in candidates[:top_k]
        ]
        return results, "NON_AI"