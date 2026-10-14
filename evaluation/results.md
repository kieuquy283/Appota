# Evaluation results

Synthetic corpus; run with `python -m scripts.evaluate`. This file records actual local results.

| Case | Expected | Actual | Result | Lesson |
|---|---|---|---|---|
| T01 Normal answer | ANSWER / ALPHA-LEAVE | ANSWER / ALPHA-LEAVE | PASS | Behavior matched |
| T02 Same query, different context | ANSWER / NOVA-LEAVE | ANSWER / NOVA-LEAVE | PASS | Behavior matched |
| T03 Unauthorized HR source | ABSTAIN | ABSTAIN / no citation | PASS | Behavior matched |
| T04 Current version | ANSWER | ANSWER / ALPHA-LEAVE | PASS | Behavior matched |
| T05 Authority beats FAQ | ANSWER / ALPHA-WFH-POLICY | ANSWER / ALPHA-WFH-POLICY | PASS | Behavior matched |
| T06 Equal authority conflict | CONFLICT | CONFLICT / NOVA-WFH-POLICY-A, NOVA-WFH-POLICY-B | PASS | Behavior matched |
| T07 Missing weekday evidence | ABSTAIN | ABSTAIN / no citation | PASS | Behavior matched |
| T08 Observed paraphrase limitation | ANSWER / ALPHA-LEAVE | ANSWER / ALPHA-LEAVE | PASS | Behavior matched |

Passed: 8/8.
Unauthorized context rate in these cases: 0 (no forbidden chunk entered LLM context).
Provider LLM and hosted embedding paths are not exercised in this offline run.
