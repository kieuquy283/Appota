# Synthetic corpus evaluation

Offline MVP snapshot, query date 2026-10-14 unless specified. All content is fictional.

Documents: 53. Users: 18. Scenarios: 60.

| Case | Tier | Expected | Actual | Result |
|---|---|---|---|---|
| S01 | success | ANSWER | ANSWER / AP-HR-LEAVE-2026 | PASS |
| S02 | success | ANSWER | ANSWER / BG-HR-LEAVE-2026 | PASS |
| S03 | success | ANSWER | ANSWER / AP-HR-LEAVE-INTERN-2026 | PASS |
| S04 | success | ANSWER | ANSWER / CX-HR-LEAVE-2026 | PASS |
| S05 | success | ANSWER | ANSWER / AP-HR-CONTRACTOR-LEAVE | PASS |
| S06 | success | ANSWER | ANSWER / AP-ENG-REMOTE-2026 | PASS |
| S07 | success | ANSWER | ANSWER / AP-FIN-REMOTE-2026 | PASS |
| S08 | success | ANSWER | ANSWER / BG-REMOTE-2026 | PASS |
| S09 | success | ABSTAIN | ABSTAIN | PASS |
| S10 | success | ABSTAIN | ABSTAIN | PASS |
| S11 | success | ANSWER | ANSWER / AP-HR-LEAVE-2026 | FAIL |
| S12 | success | ANSWER | ANSWER / AP-HR-LEAVE-MANAGER-2026 | FAIL |
| H01 | hard_ambiguous | CONFLICT | ABSTAIN | FAIL |
| H02 | hard_ambiguous | ABSTAIN | ABSTAIN | PASS |
| H03 | hard_ambiguous | ABSTAIN | ABSTAIN | PASS |
| H04 | hard_ambiguous | ANSWER | ABSTAIN | FAIL |
| H05 | hard_ambiguous | ANSWER | ABSTAIN | FAIL |
| H06 | hard_ambiguous | ANSWER | ABSTAIN | FAIL |
| F01 | expected_failure | ABSTAIN | ANSWER / CX-HR-LEAVE-2026 | FAIL |
| F02 | expected_failure | ABSTAIN | ANSWER / AP-HR-LEAVE-2026 | FAIL |
| F03 | expected_failure | ABSTAIN | ABSTAIN | PASS |
| F04 | expected_failure | ABSTAIN | ANSWER / BG-HR-LEAVE-2026 | FAIL |
| F05 | expected_failure | ABSTAIN | ABSTAIN | PASS |
| S13 | success | ANSWER | ANSWER / AP-HR-SALARY-BANDS | PASS |
| S14 | success | ANSWER | ANSWER / AP-HR-SALARY-BANDS | PASS |
| S15 | success | ANSWER | ABSTAIN | FAIL |
| S16 | success | ANSWER | ABSTAIN | FAIL |
| S17 | success | ANSWER | ABSTAIN | FAIL |
| S18 | success | ANSWER | ABSTAIN | FAIL |
| S19 | success | ANSWER | ABSTAIN | FAIL |
| S20 | success | ANSWER | ABSTAIN | FAIL |
| S21 | success | ANSWER | ABSTAIN | FAIL |
| H07 | hard_ambiguous | CONFLICT | ABSTAIN | FAIL |
| H08 | hard_ambiguous | ABSTAIN | ABSTAIN | PASS |
| H09 | hard_ambiguous | ABSTAIN | ABSTAIN | PASS |
| H10 | hard_ambiguous | ABSTAIN | ABSTAIN | PASS |
| F06 | expected_failure | ABSTAIN | ABSTAIN | PASS |
| F07 | expected_failure | ABSTAIN | ABSTAIN | PASS |
| F08 | expected_failure | ABSTAIN | ABSTAIN | PASS |
| F09 | expected_failure | ANSWER | ABSTAIN | FAIL |
| F10 | expected_failure | ANSWER | ABSTAIN | FAIL |
| F11 | expected_failure | ANSWER | ANSWER / AP-HR-LEAVE-2026 | PASS |
| F18 | expected_failure | ABSTAIN | ANSWER / GRP-REMOTE-GUIDE | FAIL |
| S22 | success | ANSWER | ABSTAIN | FAIL |
| F19 | expected_failure | ABSTAIN | ABSTAIN | PASS |
| H11 | hard_ambiguous | ABSTAIN | ABSTAIN | PASS |
| H12 | hard_ambiguous | ABSTAIN | ABSTAIN | PASS |
| H13 | hard_ambiguous | ANSWER | ABSTAIN | FAIL |
| H14 | hard_ambiguous | ANSWER | ABSTAIN | FAIL |
| H15 | hard_ambiguous | ANSWER | ABSTAIN | FAIL |
| H16 | hard_ambiguous | ANSWER | ABSTAIN | FAIL |
| H17 | hard_ambiguous | ANSWER | ANSWER / AP-MGR-APPROVAL-2026 | FAIL |
| F12 | expected_failure | ABSTAIN | ABSTAIN | PASS |
| F13 | expected_failure | ABSTAIN | ABSTAIN | PASS |
| F14 | expected_failure | ABSTAIN | ABSTAIN | PASS |
| F15 | expected_failure | ABSTAIN | ABSTAIN | PASS |
| F16 | expected_failure | ABSTAIN | ABSTAIN | PASS |
| F17 | expected_failure | ABSTAIN | ABSTAIN | PASS |
| H18 | hard_ambiguous | ANSWER | ABSTAIN | FAIL |
| H19 | hard_ambiguous | ANSWER | ANSWER / AP-HR-LEAVE-2026 | PASS |

## Summary

- success: 12/22 passed
- hard_ambiguous: 8/19 passed
- expected_failure: 13/19 passed

Failures are observations of the current MVP, not changes to the expected policy behavior.
The evaluator runs the offline extraction path; hosted embeddings and LLM generation are not exercised.
See results.json for each check, answer, and citation.
