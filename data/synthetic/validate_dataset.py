"""Check the synthetic corpus and its test oracle without calling the MVP."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REQUIRED_METADATA = {
    "document_id", "title", "company", "department", "team", "allowed_roles",
    "allowed_levels", "allowed_employment_types", "confidentiality", "version",
    "document_status", "effective_date", "expiry_date", "supersedes",
    "status", "access_scope",
}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> tuple[int, int, int]:
    seed = read(ROOT / "seed.json")
    users = read(ROOT / "users" / "users.json")
    cases = read(ROOT / "tests" / "cases.json")
    documents = seed["documents"]
    assert seed["users"] == users
    assert seed["org_units"] == read(ROOT / "users" / "organization.json")
    assert "SYNTHETIC DEMO ONLY" in seed["disclaimer"]
    assert len(users) >= 12 and len(documents) >= 25
    assert len(cases) >= 20
    assert len({u["user_id"] for u in users}) == len(users)
    assert len({d["id"] for d in documents}) == len(documents)
    assert {u["company"] for u in users} == {"AlphaPay", "BetaGame", "CloudX"}
    assert {u["employment_type"] for u in users} >= {"FULL_TIME", "PART_TIME", "INTERN", "CONTRACTOR"}
    assert {u["level_label"] for u in users} >= {"L1", "L2", "L3", "L4", "L5", "Manager", "Director"}
    for user in users:
        assert {"user_id", "name", "company", "department", "team", "level", "level_label", "employment_type"} <= user.keys()
        assert user["active"] is True

    by_id = {d["id"]: d for d in documents}
    for document in documents:
        assert read(ROOT / "documents" / f'{document["id"]}.json') == document
        assert {"id", "title", "topic", "authority", "access", "applicability", "versions", "metadata"} <= document.keys()
        meta = document["metadata"]
        assert REQUIRED_METADATA <= meta.keys(), document["id"]
        assert meta["document_id"] == document["id"] and meta["title"] == document["title"]
        assert meta["confidentiality"] in {"INTERNAL", "RESTRICTED"}
        assert meta["status"] == {"APPROVED": "ACTIVE", "DEPRECATED": "DEPRECATED", "DRAFT": "DRAFT"}[meta["document_status"]]
        assert document["access"] and any(r["effect"] == "ALLOW" for r in document["access"])
        assert document["versions"]
        assert (meta["version"], meta["document_status"], meta["effective_date"], meta["expiry_date"]) == (
            document["versions"][0]["version"], document["versions"][0]["status"],
            document["versions"][0]["from"], document["versions"][0]["to"])
        for version in document["versions"]:
            assert version["status"] in {"APPROVED", "DEPRECATED", "DRAFT"}
            assert version["value"] and len(version["content"]) >= 60, document["id"]
            assert version["section"]
            date.fromisoformat(version["from"])
            if version["to"]:
                assert date.fromisoformat(version["from"]) < date.fromisoformat(version["to"])
        if meta["supersedes"]:
            assert meta["supersedes"] in by_id, document["id"]
    assert len(list((ROOT / "documents").glob("*.json"))) == len(documents)
    lengths = {doc["id"]: len(doc["versions"][0]["content"].split()) for doc in documents}
    assert sum(words >= 400 for words in lengths.values()) > len(documents) / 2
    assert all(lengths[doc_id] >= 1500 for doc_id in (
        "GRP-WORKPLACE-2026", "AP-HANDBOOK-2025", "BG-TRAVEL-FAQ-2026"))

    tiers = Counter(case["tier"] for case in cases)
    assert all(tiers[tier] for tier in ("success", "hard_ambiguous", "expected_failure"))
    assert len({case["id"] for case in cases}) == len(cases)
    user_ids = {u["user_id"] for u in users}
    for case in cases:
        assert {"test_id", "category", "description", "user_id", "question", "expected_behavior",
                "expected_answer_contains", "expected_answer_not_contains", "expected_document_ids",
                "forbidden_document_ids", "difficulty", "mission2_type"} <= case.keys()
        assert case["user_id"] in user_ids
        assert case["question"] and case["expected_status"] in {"ANSWER", "ABSTAIN", "CONFLICT"}
        assert set(case.get("expected_sources", []) + case.get("forbidden_sources", [])) <= by_id.keys()
        assert not set(case.get("expected_sources", [])) & set(case.get("forbidden_sources", []))
        if case.get("query_date"):
            date.fromisoformat(case["query_date"])
        if case["expected_status"] == "ANSWER":
            assert case.get("expected_sources"), case["id"]
        if case["expected_status"] == "CONFLICT":
            assert len(case.get("expected_sources", [])) >= 2, case["id"]
    assert len({case["test_id"] for case in cases}) == len(cases)
    assert cases == read(ROOT / "tests" / "test_cases.json")
    assert {"context_company", "employment_type", "department_scope", "employee_level",
            "authorized_restricted", "unauthorized_restricted", "prompt_injection",
            "historical_version", "specific_over_general", "equal_authority_conflict",
            "missing_data", "ambiguous_question", "cross_company_similarity",
            "explicit_document_id", "forbidden_inventory", "multi_turn",
            "long_document_noise"} <= {case["category"] for case in cases}
    assert (ROOT / "tests" / "golden_test_matrix.md").read_text(encoding="utf-8").count("| TC") == len(cases)
    assert (ROOT / "tests" / "mission2_evaluation_template.md").read_text(encoding="utf-8").count("## Test TC") == len(cases)
    corpus_text = json.dumps(seed, ensure_ascii=False)
    assert not re.search(r"\b(?:sk-[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16})\b", corpus_text)

    # Confirm the deliberate traps are actually present in the corpus.
    assert [by_id[f"AP-HR-LEAVE-{year}"]["versions"][0]["value"] for year in (2024, 2025, 2026)] == [
        "12 days/year", "14 days/year", "15 days/year"]
    assert [by_id[x]["versions"][0]["value"] for x in ("AP-EXPENSE-2025", "AP-EXPENSE-2026")] == [
        "150000 VND/day", "200000 VND/day"]
    assert {by_id[x]["versions"][0]["value"] for x in ("AP-TRAVEL-TAXI-A", "AP-TRAVEL-TAXI-FAQ")} == {
        "500000 VND/trip", "600000 VND/trip"}
    assert all(by_id[x]["versions"][0]["status"] == "APPROVED" for x in ("AP-TRAVEL-TAXI-A", "AP-TRAVEL-TAXI-FAQ"))
    assert all(by_id[x]["authority"] == "OFFICIAL_POLICY" for x in ("AP-TRAVEL-TAXI-A", "AP-TRAVEL-TAXI-FAQ"))
    assert all(by_id[x]["metadata"]["confidentiality"] == "RESTRICTED" for x in (
        "AP-HR-SALARY-BANDS", "AP-FIN-AUDIT-2026", "CX-SEC-SEV1-2026"))
    return len(documents), len(users), len(cases)


if __name__ == "__main__":
    docs, users, cases = validate()
    print(f"VALID: {docs} documents, {users} users, {cases} QA cases")
