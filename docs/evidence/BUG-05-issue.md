Requirement: FR-13

Reproduction: Student has CS201 registered, 6 credits; CS201 has 3 credits, capacity=2 and enrolled=1. Call withdraw_course.

Expected: True; course removed, credits=3, enrolled=0

Actual in unchanged starter: True; course removed, credits=3, enrolled remains 1

Failed test: `S10` in `tests/test_blackbox.py`.

Evidence: `docs/evidence/initial-blackbox/pytest.txt` (39 passed, 14 failed).

Proposed fix: Subtract one from course.enrolled on successful withdrawal.

Status: reproduced on the original source; fixed and regression-tested on `defect-fixes`. Awaiting PR merge/review.
