from __future__ import annotations

from datetime import date
from time import perf_counter
from uuid import uuid4

from .governance import can_read, current_versions, is_applicable, resolve_authority
from .citations import citation_from_chunk
from .llm import generate
from .models import AnswerResult, Citation
from .retrieval import detect_intent, retrieve
from .store import get_user, load_seed


def list_demo_users() -> list[dict]:
    return [dict(user) for user in load_seed()["users"] if user["active"]]


def answer_question(user_id: str, question: str, *, query_date: date | None = None,
                    seed: dict | None = None) -> AnswerResult:
    if not question.strip():
        raise ValueError("Question must not be empty")
    started = perf_counter()
    dataset = seed if seed is not None else load_seed()
    user = get_user(user_id, dataset)
    topic, weekday_specific = detect_intent(question)
    today = query_date or date.today()
    trace = {"request_id": str(uuid4()), "user_id": user_id, "query_mode": "SELF_CONTEXT",
             "user_context": {k: user[k] for k in ("company", "department", "team", "role", "level")},
             "total_document_count": len(dataset["documents"]), "topic": topic}

    readable = [doc for doc in dataset["documents"] if can_read(user, doc)]
    applicable = [doc for doc in readable if is_applicable(user, doc)]
    eligible = []
    for doc in applicable:
        for version in current_versions(doc, today):
            eligible.append({"document_id": doc["id"], "title": doc["title"], "authority": doc["authority"],
                             "topic": doc["topic"], **version})
    trace.update({"access_rejected_count": len(dataset["documents"]) - len(readable),
                  "readable_document_count": len(readable),
                  "applicability_rejected_count": len(readable) - len(applicable),
                  "applicable_document_count": len(applicable),
                  "version_excluded_count": sum(len(d["versions"]) for d in applicable) - len(eligible),
                  "current_version_count": len(eligible)})

    chunks = retrieve(question, eligible, topic)
    trace["retrieved_document_ids"] = [x["document_id"] for x in chunks]
    trace["retrieved_versions"] = [x["version"] for x in chunks]
    decision, selected = resolve_authority(chunks)
    trace["resolver_decision"] = decision
    documents = {d["id"]: d for d in dataset["documents"]}
    for chunk in selected:
        doc = documents[chunk["document_id"]]
        if not can_read(user, doc) or not is_applicable(user, doc) or chunk not in eligible:
            raise AssertionError("Invalid source reached citation or LLM context")

    if decision == "CONFLICT":
        result = AnswerResult("CONFLICT", "Có các chính sách hiện hành cùng thẩm quyền nhưng mâu thuẫn. Vui lòng hỏi chủ sở hữu chính sách.",
                              [citation_from_chunk(x) for x in selected],
                              "equal_authority_conflict")
    elif decision == "INSUFFICIENT" or weekday_specific:
        result = AnswerResult("ABSTAIN", "Tài liệu hiện có chưa đủ căn cứ để trả lời câu hỏi này.",
                              reason="missing_evidence")
    else:
        result = generate(question, topic, selected)
        valid = {(x["document_id"], x["version"]): x["content"] for x in selected}
        if not result.citations or any(
            (c.document_id, c.version) not in valid
            or not c.excerpt
            or c.excerpt not in valid[(c.document_id, c.version)]
            for c in result.citations
        ):
            raise ValueError("Answer contains invalid citations")
    trace.update(result.trace)
    trace["llm_context_document_ids"] = [x["document_id"] for x in selected] if result.status == "ANSWER" else []
    trace["llm_context_version_ids"] = [x["version"] for x in selected] if result.status == "ANSWER" else []
    trace["decision"] = result.status
    trace["latency_ms"] = round((perf_counter() - started) * 1000, 2)
    result.trace = trace
    return result
