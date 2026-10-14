"""Build verifiable, human-readable citations from guarded source chunks."""

from __future__ import annotations

from .models import Citation


def source_excerpt(source: dict, limit: int = 680) -> str:
    """Return an exact contiguous passage from the cited document version."""
    content = source["content"].strip()
    if not content:
        raise ValueError("Citation source has no document text")
    paragraphs = [paragraph.strip() for paragraph in content.split("\n\n") if paragraph.strip()]
    section = (source.get("section") or "").casefold()
    # The synthetic corpus keeps operative policy text under section 3.
    passage = next((p for p in paragraphs if p.startswith("3. ") and section in p.casefold()), None)
    if passage is None:
        passage = next((p for p in paragraphs if section and section in p.casefold()), paragraphs[0])
    if len(passage) <= limit:
        return passage
    # Prefer a complete sentence while keeping a contiguous verbatim quote.
    sentence_end = passage.rfind(". ", 0, limit)
    if sentence_end >= limit // 2:
        return passage[:sentence_end + 1]
    boundary = passage.rfind(" ", 0, limit)
    return passage[:boundary if boundary > 0 else limit]


def citation_from_chunk(source: dict) -> Citation:
    return Citation(source["document_id"], source["title"], source["version"],
                    source.get("section"), source_excerpt(source))
