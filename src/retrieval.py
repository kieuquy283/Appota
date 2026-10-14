from __future__ import annotations

import math
import json
import os
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from urllib import request

from .citations import source_excerpt


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", text)


def detect_intent(question: str) -> tuple[str | None, bool]:
    q = _normalize(question)
    friday = "thu sau" in q or "friday" in q
    if any(x in q for x in ("nghi phep", "ngay phep", "annual leave", "leave days")):
        return "leave_days", friday
    if any(x in q for x in ("wfh", "work from home", "lam viec tai nha", "remote work")):
        return "wfh_days", friday
    if any(x in q for x in ("duyet phep", "phe duyet", "approve leave")):
        return "leave_approval", friday
    if any(x in q for x in ("luong", "compensation", "salary")):
        return "compensation", friday
    return None, friday


def _vector(text: str) -> Counter:
    # Offline lexical vector fallback. A semantic embedding adapter can replace it.
    words = _normalize(text).split()
    return Counter(words)


def _cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    dot = sum(value * b[word] for word, value in a.items())
    return dot / (math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values())))


@lru_cache(maxsize=1024)
def _api_embedding(text: str, model: str, base: str, key: str) -> tuple[float, ...]:
    payload = json.dumps({"model": model, "input": text}).encode()
    req = request.Request(base.rstrip("/") + "/embeddings", data=payload,
                          headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    with request.urlopen(req, timeout=30) as response:
        return tuple(json.load(response)["data"][0]["embedding"])


def _embedding_document_text(source: dict) -> str:
    """Keep policy embedding input within the LFM model's 512-token window."""
    return f"{source['title']}\n{source_excerpt(source, limit=600)}"


def _dense_cosine(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("Invalid embedding dimensions")
    return sum(x * y for x, y in zip(a, b)) / (
        math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def retrieve(question: str, eligible: list[dict], topic: str | None, top_k: int = 5) -> list[dict]:
    if topic is None:
        return []
    candidates = [x for x in eligible if x["topic"] == topic]
    model = os.getenv("EMBEDDING_MODEL")
    key = os.getenv("EMBEDDING_API_KEY") or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if model and key:
        base = os.getenv("EMBEDDING_BASE_URL") or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        qvec = _api_embedding(question, model, base, key)
        return sorted(candidates, key=lambda x: (-_dense_cosine(qvec, _api_embedding(_embedding_document_text(x), model, base, key)), x["document_id"]))[:top_k]
    qvec = _vector(question)
    return sorted(candidates, key=lambda x: (-_cosine(qvec, _vector(x["content"] + " " + x["title"])), x["document_id"]))[:top_k]
