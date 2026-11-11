Requirement: FR-08/12

Reproduction: Use default decision fixture; set capacity=2 and enrolled=2. Call registration_decision. Calling register_course also incorrectly raises enrollment to 3.

Expected: WAITLISTED

Actual in unchanged starter: REGISTERED

Failed test: `D08` in `tests/test_blackbox.py`.

Evidence: `docs/evidence/initial-blackbox/pytest.txt` (39 passed, 14 failed).

Proposed fix: Use enrolled == capacity; validation already excludes over-capacity states.

Status: reproduced on the original source; fixed and regression-tested on `defect-fixes`. Awaiting PR merge/review.
