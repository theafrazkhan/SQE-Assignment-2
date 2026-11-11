Requirement: FR-03/06

Reproduction: Call prerequisites_satisfied({'CS101'}, {'CS101', 'MATH101'}).

Expected: False

Actual in unchanged starter: True

Failed test: `P03` in `tests/test_blackbox.py`.

Evidence: `docs/evidence/initial-blackbox/pytest.txt` (39 passed, 14 failed).

Proposed fix: Check required.issubset(completed).

Status: reproduced on the original source; fixed and regression-tested on `defect-fixes`. Awaiting PR merge/review.
