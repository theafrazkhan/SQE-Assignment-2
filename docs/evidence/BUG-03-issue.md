Requirement: FR-04/09

Reproduction: Use default decision fixture (docs/cases.json) and set outstanding_dues=1. Call registration_decision.

Expected: DUES_BLOCK

Actual in unchanged starter: REGISTERED

Failed test: `D02` in `tests/test_blackbox.py`.

Evidence: `docs/evidence/initial-blackbox/pytest.txt` (39 passed, 14 failed).

Proposed fix: Change the dues threshold from >1000 to >0.

Status: reproduced on the original source; fixed and regression-tested on `defect-fixes`. Awaiting PR merge/review.
