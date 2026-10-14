"""Score the existing offline MVP against the separate synthetic QA corpus."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

from src.service import answer_question
from src.governance import can_read, current_versions, is_applicable

from data.synthetic.validate_dataset import ROOT, validate


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def main() -> None:
    validate()
    seed = json.loads((ROOT / "seed.json").read_text(encoding="utf-8"))
    cases = json.loads((ROOT / "tests" / "cases.json").read_text(encoding="utf-8"))
    documents = {doc["id"]: doc for doc in seed["documents"]}
    users = {user["user_id"]: user for user in seed["users"]}
    rows = []
    for case in cases:
        errors = []
        try:
            result = answer_question(
                case["user_id"], case["question"], seed=seed,
                query_date=date.fromisoformat(case.get("query_date", seed["as_of"])),
            )
            actual_sources = {citation.document_id for citation in result.citations}
            context_sources = set(result.trace.get("llm_context_document_ids", []))
            retrieved_sources = set(result.trace.get("retrieved_document_ids", []))
            user = users[case["user_id"]]
            query_date = date.fromisoformat(case.get("query_date", seed["as_of"]))
            unauthorized = sorted(doc_id for doc_id in retrieved_sources | context_sources
                                  if not can_read(user, documents[doc_id]) or not is_applicable(user, documents[doc_id]))
            employment_mismatch = sorted(doc_id for doc_id in context_sources
                                         if user["employment_type"] not in documents[doc_id]["metadata"]["allowed_employment_types"])
            invalid_versions = [(doc_id, version) for doc_id, version in zip(
                result.trace.get("llm_context_document_ids", []), result.trace.get("llm_context_version_ids", []))
                if version not in {v["version"] for v in current_versions(documents[doc_id], query_date)}]
            if unauthorized:
                errors.append("unauthorized retrieval/context: " + ", ".join(unauthorized))
            if employment_mismatch:
                errors.append("employment scope ignored: " + ", ".join(employment_mismatch))
            if invalid_versions:
                errors.append("noncurrent version in context")
            if not actual_sources <= context_sources:
                errors.append("citation outside generated context")
            if result.status != case["expected_status"]:
                errors.append(f"status={result.status}, expected={case['expected_status']}")
            if not set(case.get("expected_sources", [])) <= actual_sources:
                errors.append("missing expected citation")
            if case.get("expected_value") and compact(case["expected_value"]) not in compact(result.answer):
                errors.append("expected value absent from answer")
            if case["expected_status"] == "ANSWER" and not result.citations:
                errors.append("answer has no citation")
            if case["expected_status"] == "ABSTAIN" and result.citations:
                errors.append("abstention contains a citation")
            for source in case.get("forbidden_sources", []):
                if source in actual_sources or source in context_sources:
                    errors.append(f"forbidden source used: {source}")
                if documents[source]["metadata"]["confidentiality"] == "RESTRICTED" and source in retrieved_sources:
                    errors.append(f"restricted source retrieved: {source}")
            exposed = result.answer + " " + " ".join(c.title for c in result.citations)
            for needle in case.get("must_not_contain", []):
                if needle.casefold() in exposed.casefold():
                    errors.append(f"sensitive text exposed: {needle}")
            row = {"id": case["id"], "test_id": case["test_id"], "category": case["category"],
                   "user_id": case["user_id"], "question": case["question"],
                   "expected_sources": case.get("expected_sources", []),
                   "actual_answer": result.answer,
                   "retrieved_documents": sorted(retrieved_sources),
                   "context_documents": sorted(context_sources),
                   "authorization_outcome": "PASS" if not unauthorized and not employment_mismatch else "FAIL",
                   "tier": case["tier"], "pass": not errors,
                   "expected_status": case["expected_status"], "actual_status": result.status,
                   "citations": [{"document_id": c.document_id, "version": c.version, "section": c.section}
                                 for c in result.citations], "errors": errors}
        except Exception as exc:
            row = {"id": case["id"], "test_id": case["test_id"], "tier": case["tier"], "pass": False,
                   "expected_status": case["expected_status"], "actual_status": "ERROR",
                   "citations": [], "errors": [f"{type(exc).__name__}: {exc}"]}
        rows.append(row)
    summary = {"passed": sum(row["pass"] for row in rows), "total": len(rows),
               "by_tier": {tier: {"passed": sum(r["pass"] for r in rows if r["tier"] == tier),
                                  "total": count}
                           for tier, count in Counter(row["tier"] for row in rows).items()}}
    report = {"corpus": "APPOTA GROUP — SYNTHETIC DEMO ONLY", "as_of": seed["as_of"],
              "summary": summary, "cases": rows}
    (ROOT / "tests" / "mvp_results.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Mission 2 observed evaluation", "", "Kỳ vọng → Kết quả thực tế → Đạt / Chưa đạt → Điều học được.", "",
             f"Offline MVP: {summary['passed']}/{summary['total']} passed. All data are fictional.", "",
             "| Test | Category | Kỳ vọng | Kết quả thực tế | Đạt / Chưa đạt | Điều học được |",
             "|---|---|---|---|---|---|"]
    for row in rows:
        lesson = "; ".join(row["errors"]) if row["errors"] else "Matched the golden expectation"
        lines.append(f"| {row['test_id']} | {row.get('category', 'error')} | {row['expected_status']} | "
                     f"{row['actual_status']} | {'Đạt' if row['pass'] else 'Chưa đạt'} | {lesson} |")
    lines += ["", "Detailed retrieved documents, citations and authorization outcomes are in `mvp_results.json`.",
              "Multi-turn cases are scored using the final question only because `answer_question` is stateless.", ""]
    (ROOT / "tests" / "mvp_results.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"MVP matched {summary['passed']}/{summary['total']} synthetic QA cases")
    for row in rows:
        if not row["pass"]:
            print(f"{row['id']}: {', '.join(row['errors'])}")


if __name__ == "__main__":
    main()
