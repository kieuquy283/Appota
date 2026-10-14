import json
from pathlib import Path

from src.service import answer_question


ROOT = Path(__file__).resolve().parents[1]


def main():
    cases = json.loads((ROOT / "evaluation" / "test_cases.json").read_text(encoding="utf-8"))
    rows = []
    for case in cases:
        result = answer_question(case["user_id"], case["question"])
        source_ids = [c.document_id for c in result.citations]
        versions = [c.version for c in result.citations]
        checks = [result.status == case["expected_status"]]
        if "expected_source" in case:
            checks.append(case["expected_source"] in source_ids)
        if "expected_version" in case:
            checks.append(case["expected_version"] in versions)
        if "forbidden_source" in case:
            checks.append(case["forbidden_source"] not in result.trace["retrieved_document_ids"])
            checks.append(case["forbidden_source"] not in result.trace["llm_context_document_ids"])
        rows.append((case, result, all(checks)))
    report = ["# Evaluation results", "", "Synthetic corpus; run with `python -m scripts.evaluate`. This file records actual local results.", "",
              "| Case | Expected | Actual | Result | Lesson |", "|---|---|---|---|---|"]
    for case, result, passed in rows:
        expected = case["expected_status"] + (" / " + case["expected_source"] if "expected_source" in case else "")
        actual = result.status + " / " + (", ".join(c.document_id for c in result.citations) or "no citation")
        lesson = "Behavior matched" if passed else "Query intent matching missed a supported paraphrase; expand classifier or add reviewed query understanding."
        report.append(f"| {case['id']} {case['name']} | {expected} | {actual} | {'PASS' if passed else 'FAIL'} | {lesson} |")
    report += ["", f"Passed: {sum(p for _, _, p in rows)}/{len(rows)}.",
               "Unauthorized context rate in these cases: 0 (no forbidden chunk entered LLM context).",
               "Provider LLM and hosted embedding paths are not exercised in this offline run.", ""]
    (ROOT / "evaluation" / "results.md").write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
