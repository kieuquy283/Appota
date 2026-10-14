"""Evaluate the synthetic fixture against the current offline MVP.

Run: python -m data.synthetic.tests.evaluate
The report records observed failures instead of changing application behavior.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

from src.governance import can_read, current_versions, is_applicable
from src.service import answer_question


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def validate_fixture(seed, cases):
    users = {u["user_id"]: u for u in seed["users"]}
    docs = {d["id"]: d for d in seed["documents"]}
    assert len(users) == len(seed["users"]) >= 12
    assert len(docs) == len(seed["documents"]) >= 25
    assert {"AlphaPay", "BetaGame", "CloudX"} <= {u["company"] for u in users.values()}
    assert {"FULL_TIME", "PART_TIME", "INTERN", "CONTRACTOR"} <= {u["employment_type"] for u in users.values()}
    assert all(u.keys() >= {"user_id", "name", "company", "department", "team", "level", "employment_type", "role", "active"} for u in users.values())
    assert all(d.keys() >= {"id", "title", "topic", "authority", "access", "applicability", "versions", "metadata"} for d in docs.values())
    assert all(d["metadata"].keys() >= {"document_id", "company", "department", "team", "allowed_roles", "allowed_levels", "allowed_employment_types", "confidentiality"} for d in docs.values())
    assert all(d["versions"] and all(v.keys() >= {"version", "status", "from", "to", "content", "section", "value"} for v in d["versions"]) for d in docs.values())
    assert all(c["user_id"] in users for c in cases)
    assert {"success", "hard_ambiguous", "expected_failure"} <= {c["tier"] for c in cases}
    assert all(set(c.get("expected_sources", []) + c.get("forbidden_sources", [])) <= docs.keys() for c in cases)
    assert all(load(ROOT / "documents" / f"{doc_id}.json") == doc for doc_id, doc in docs.items())
    assert load(ROOT / "users" / "users.json") == seed["users"]
    assert not can_read(users["U01"], docs["AP-ENG-BACKEND-ACCESS"])
    assert can_read(users["U18"], docs["AP-ENG-BACKEND-ACCESS"])
    assert not can_read(users["U01"], docs["AP-HR-SALARY-BANDS"])
    assert can_read(users["U04"], docs["AP-HR-SALARY-BANDS"])
    assert not can_read(users["U05"], docs["AP-HR-LEAVE-2026"])
    return users, docs


def evaluate():
    seed = load(ROOT / "seed.json")
    cases = load(ROOT / "tests" / "cases.json")
    users, docs = validate_fixture(seed, cases)
    rows = []
    for case in cases:
        query_date = date.fromisoformat(case["query_date"]) if case.get("query_date") else date.fromisoformat(seed["as_of"])
        result = answer_question(case["user_id"], case["question"], query_date=query_date, seed=seed)
        user = users[case["user_id"]]
        cited = {c.document_id for c in result.citations}
        context = set(result.trace["llm_context_document_ids"])
        retrieved = set(result.trace["retrieved_document_ids"])
        forbidden = set(case.get("forbidden_sources", []))
        checks = {
            "status": result.status == case["expected_status"],
            "value": case.get("expected_value") is None or compact(case["expected_value"]) in compact(result.answer),
            "sources": set(case.get("expected_sources", [])) <= cited,
            "forbidden_not_cited": not (forbidden & cited),
            "forbidden_not_in_context": not (forbidden & context),
            "retrieval_authorized": all(can_read(user, docs[doc_id]) and is_applicable(user, docs[doc_id]) for doc_id in retrieved),
            "context_authorized": all(can_read(user, docs[doc_id]) and is_applicable(user, docs[doc_id]) for doc_id in context),
            "metadata_employment_scope": all(user["employment_type"] in docs[doc_id]["metadata"]["allowed_employment_types"] for doc_id in context),
            "citation_in_context": cited <= context,
            "answer_cited": result.status != "ANSWER" or bool(result.citations),
            "sensitive_text_absent": all(
                text.casefold() not in (result.answer + " " + " ".join(c.title for c in result.citations)).casefold()
                for text in case.get("must_not_contain", [])),
        }
        # Every source sent for generation must be an approved current version.
        for doc_id, version in zip(result.trace["llm_context_document_ids"], result.trace["llm_context_version_ids"]):
            checks["current_version"] = checks.get("current_version", True) and version in {
                v["version"] for v in current_versions(docs[doc_id], query_date)
            }
        rows.append({"id": case["id"], "tier": case["tier"], "user_id": case["user_id"],
                     "question": case["question"], "expected_status": case["expected_status"],
                     "actual_status": result.status, "actual_answer": result.answer,
                     "actual_sources": sorted(cited), "checks": checks, "pass": all(checks.values()),
                     "note": case.get("note", "")})
    write = lambda path, body: path.write_text(body, encoding="utf-8")
    write(ROOT / "tests" / "results.json", json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    counts = Counter((r["tier"], r["pass"]) for r in rows)
    report = ["# Synthetic corpus evaluation", "", "Offline MVP snapshot, query date 2026-10-14 unless specified. All content is fictional.", "",
              f"Documents: {len(docs)}. Users: {len(users)}. Scenarios: {len(cases)}.", "",
              "| Case | Tier | Expected | Actual | Result |", "|---|---|---|---|---|"]
    for row in rows:
        actual = row["actual_status"] + (" / " + ", ".join(row["actual_sources"]) if row["actual_sources"] else "")
        report.append(f"| {row['id']} | {row['tier']} | {row['expected_status']} | {actual} | {'PASS' if row['pass'] else 'FAIL'} |")
    report += ["", "## Summary", ""]
    for tier in ("success", "hard_ambiguous", "expected_failure"):
        total = sum(r["tier"] == tier for r in rows)
        report.append(f"- {tier}: {counts[(tier, True)]}/{total} passed")
    report += ["", "Failures are observations of the current MVP, not changes to the expected policy behavior.",
               "The evaluator runs the offline extraction path; hosted embeddings and LLM generation are not exercised.",
               "See results.json for each check, answer, and citation.", ""]
    write(ROOT / "tests" / "results.md", "\n".join(report))
    print("\n".join(report))


if __name__ == "__main__":
    evaluate()
