"""Score the existing offline MVP against the separate synthetic QA corpus."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

from src.service import answer_question

from data.synthetic.validate_dataset import ROOT, validate


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def main() -> None:
    validate()
    seed = json.loads((ROOT / "seed.json").read_text(encoding="utf-8"))
    cases = json.loads((ROOT / "tests" / "cases.json").read_text(encoding="utf-8"))
    documents = {doc["id"]: doc for doc in seed["documents"]}
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
            row = {"id": case["id"], "tier": case["tier"], "pass": not errors,
                   "expected_status": case["expected_status"], "actual_status": result.status,
                   "citations": sorted(actual_sources), "errors": errors}
        except Exception as exc:
            row = {"id": case["id"], "tier": case["tier"], "pass": False,
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
    print(f"MVP matched {summary['passed']}/{summary['total']} synthetic QA cases")
    for row in rows:
        if not row["pass"]:
            print(f"{row['id']}: {', '.join(row['errors'])}")


if __name__ == "__main__":
    main()
