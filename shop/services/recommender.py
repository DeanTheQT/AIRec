from .candidates import get_candidates
from .gemini_rerank import rerank_with_gemini

def recommend_products(user_query: str, top_k: int = 8):
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

    try:
        ranked_ids, reasons = rerank_with_gemini(user_query, payload, top_k=top_k)

        results = [
            (id_to_product[pid], reasons.get(str(pid)) or reasons.get(pid))
            for pid in ranked_ids
            if pid in id_to_product
        ]

        if results:
            return results, "AI"

    except Exception as e:
        error_msg = str(e)
        results = [(p, f"Matched by tags/popularity (AI Error: {error_msg})") for p in candidates[:top_k]]
        return results, f"NON_AI: {error_msg}"

    return [(p, "Matched by tags/popularity") for p in candidates[:top_k]], "NON_AI"