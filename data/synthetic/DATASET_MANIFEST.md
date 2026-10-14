# Synthetic dataset manifest

**IMPORTANT: ALL DATA IN THIS DIRECTORY IS FICTIONAL AND CREATED ONLY FOR MVP TESTING.** The enterprise name, people, policy text, salary ranges, escalation key, and monetary thresholds are invented. The escalation key is a nonfunctional demo string.

## Inventory and organization

The reproducible source is `build_dataset.py`. It emits 53 JSON documents, 18 user profiles, a combined `seed.json`, and 60 golden scenarios. The hierarchy in `users/organization.json` is Group → AlphaPay / BetaGame / CloudX → department → team. AlphaPay includes Engineering (Backend, Mobile), Product, Finance and HR. BetaGame includes Game Development, Publishing, Marketing and HR. CloudX includes Infrastructure, Security, Sales and HR.

Profiles cover L1–L5, Manager and Director, plus FULL_TIME, PART_TIME, INTERN, CONTRACTOR and PROBATION. They contain work context only. `level` is numeric because the current access implementation compares integers; `level_label` preserves the human-readable grade.

## Document and authorization model

Each standalone `documents/*.json` file has a unique `id`/`metadata.document_id`, title, topic, authority, explicit `access` rules, `applicability`, version records, classification and scope metadata. `seed.json` combines exactly those same records for the current `answer_question(..., seed=fixture)` interface. JSON is the only currently ingested knowledge format. Markdown, TXT, PDF and CSV are not supported by the current loader.

The backend evaluates `DENY` before `ALLOW` and defaults to deny. Rules can match company, department, team, role and minimum numeric level. The fixture also records `allowed_employment_types` and `allowed_levels` as QA policy metadata. The current backend does **not** enforce employment type or maximum level, so the negative cases explicitly measure that gap. A user prompt must never be treated as trusted identity. Restricted source content and titles must be filtered before retrieval, generation and citation.

## Status and version rules

Version `status` is `APPROVED`, `DEPRECATED` or `DRAFT`, matching the existing service. Document-facing `metadata.document_status` mirrors it. `from` is inclusive and `to` is exclusive. The active 2026 AlphaPay leave document gives 15 days; its similar 2024 and 2025 predecessors give 12 and 14 days and are deprecated. AlphaPay expense limits move from 150,000 VND in 2025 to 200,000 VND in 2026. The future device allowance is a draft. The historical-query case is intentionally hard: the current service rejects deprecated versions even for an earlier query date.

## Deliberate overlap and gaps

- The group remote guideline says up to two days subject to company policy. BetaGame's active policy permits three days. AlphaPay Engineering permits two; Finance permits one.
- The older AlphaPay handbook summarizes 14 days of leave, while the active official 2026 leave policy gives 15. A current answer should cite the official policy.
- Two active equal-authority AlphaPay taxi records give 500,000 and 600,000 VND per trip. Both should be cited with `CONFLICT`, with no invented resolution. CloudX Security log retention has a second equal-authority conflict.
- Some information is deliberately absent: eyeglasses, CloudX gym benefit, a numeric sales commission rate, permitted remote weekdays, and the detailed terms of individual service contracts.
- Similar company expense documents deliberately reuse vocabulary. Three longer stress documents (`GRP-WORKPLACE-2026`, `AP-HANDBOOK-2025`, `BG-TRAVEL-FAQ-2026`) contain roughly 1,600–1,800 words and competing keywords.
- Restricted traps include AlphaPay salary bands, Finance audit thresholds, Backend production access, and CloudX SEV-1 escalation. The values are fictional, but the access expectation is strict.

The corpus is intentionally messy: most documents are current and clear, while the rest include older guidance, redundant text, conflicting authority, vague scope, restricted records and long irrelevant passages. The goal is to distinguish robust metadata and authorization handling from naive keyword retrieval.

## Test oracle

`tests/test_cases.json` is the canonical machine-readable oracle. Every case includes the required `test_id`, `category`, `description`, `user_id`, `question`, `expected_behavior`, positive and negative answer strings, expected and forbidden document IDs, `difficulty`, and `mission2_type`. It also retains aliases consumed by the current evaluator. `tests/cases.json` is a compatibility copy for existing QA scripts. `tests/golden_test_matrix.md` lists all cases and identifies DEMO-1 through DEMO-5. `tests/mission2_evaluation_template.md` provides the requested Kỳ vọng → Kết quả thực tế → Đạt / Chưa đạt → Điều học được structure for every case.

Run `python data/synthetic/validate_dataset.py` to check references, uniqueness, coverage, metadata, date/status consistency and synthetic fixture integrity. Run `python -m data.synthetic.run_mvp_evaluation` for the observed offline MVP baseline; results are written to `tests/mvp_results.json`. That baseline measures current behavior and deliberately preserves failures. It does not run hosted embedding or LLM providers, nor does it test a multi-turn UI conversation end to end.
