# Appota Knowledge Guard synthetic QA dataset

**APPOTA GROUP — SYNTHETIC DEMO ONLY.** Every policy, person, amount and key in this directory is fictional.

This corpus measures whether the Mission 2 MVP uses trusted user context, filters unauthorized knowledge before generation, selects a current applicable policy, cites its source and abstains when evidence is missing. It is intentionally messy so difficult cases remain visible.

The current app loads JSON from `data/seed.json`. It has no Markdown, TXT, PDF or CSV ingestion. The 53 standalone JSON documents and 18 users here are combined in `seed.json`, which can be passed to `answer_question(..., seed=fixture)` without changing the chatbot. The default Streamlit app still uses its original seed.

## Five live demo scenarios

| Demo | Cases | Show |
|---|---|---|
| DEMO-1 | S01 + S02 | Same leave question: AlphaPay 15 days, BetaGame 18 days. |
| DEMO-2 | S01 + S03 | Same leave question: AlphaPay full-time 15 days, intern 5 days. |
| DEMO-3 | F06 | Engineering user requests restricted salary band; the response must withhold value and document title. |
| DEMO-4 | F09 | Current AlphaPay expense cap 200,000 VND beats deprecated 150,000 VND. |
| DEMO-5 | H07 | Two active equal-authority taxi limits conflict; cite both and decline to choose. |

DEMO-4 and DEMO-5 currently expose the MVP's narrow intent handling. Other difficult cases cover department-specific working hours, manager/level approval thresholds, vague questions, long document noise and cross-company keyword similarity. Expected failures include employment-type scope for part-time or probationary users (`F01`, `F02`), a contractor inheriting a group remote guideline (`F18`), historical version lookup (`H06`) and multi-turn references (`F16`, `F17`). These remain in the golden tests to measure progress honestly.

## Use and extend

From the repository root:

```powershell
python data/synthetic/build_dataset.py
python data/synthetic/validate_dataset.py
python -m data.synthetic.run_mvp_evaluation
```

`tests/test_cases.json` is the golden oracle; `tests/golden_test_matrix.md` lists every case, and `tests/mission2_evaluation_template.md` is ready for observed evidence. `tests/mvp_results.json` records the offline MVP baseline. Read `DATASET_MANIFEST.md` for scope, schema, versioning and known limits.

To add a case, update `CASES` and its `CATEGORY` entry in `build_dataset.py`, rebuild, run validation, and record the observed result. To add a policy, add a `doc(...)` entry with explicit access, applicability, status, effective date and stable section heading, then add a test that cites its ID. Do not edit generated document JSON by hand; it is reproduced from the builder.
