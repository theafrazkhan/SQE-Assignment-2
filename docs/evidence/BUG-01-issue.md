Requirement: FR-01

Reproduction: Call check_credit_limit(15, 3).

Expected: True

Actual in unchanged starter: False

Failed test: `C13` in `tests/test_blackbox.py`.

Evidence: `docs/evidence/initial-blackbox/pytest.txt` (39 passed, 14 failed).

Proposed fix: Change the total comparison from <18 to <=18.

Status: reproduced on the original source; fixed and regression-tested on `defect-fixes`. Awaiting PR merge/review.
