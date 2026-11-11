# SE3002 Assignment 2 - Student Course Registration Testing

Afraz Khan | 23p3034 | GitHub: theafrazkhan

This assignment tests and corrects the supplied registration module. It uses
simple pytest cases and five small implementation fixes. REQUIREMENTS.md is
the source of expected behavior. Work was prepared with coding-assistant help;
Afraz should verify and be ready to explain the submitted work.

## Run the tests

Python 3.10 or later:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest tests/test_blackbox.py -v
python -m pytest tests/test_whitebox.py -v
python -m pytest tests/ --cov=registration --cov-branch --cov-report=term-missing
```

Final local result: **63 passed** (53 black-box and 10 white-box cases).
Statement coverage: **58/58**. Branch coverage: **26/26**.

## What to read

- `docs/testing_report.pdf`: complete report, including CFG and MC/DC analysis.
- `docs/testing_report.md`: editable report text.
- `docs/blackbox_test_design.xlsx`: ECP, BVA, traceability and optimization.
- `docs/decision_table.xlsx`: decision rules and priority examples.
- `docs/cases.json`: full inputs, expected results and test IDs.
- `docs/cfg.png` and `docs/whitebox_analysis.md`: structural analysis.
- `docs/evidence/`: actual initial, pre-fix and regression results, plus GitHub evidence.
- `docs/github_links.json`: repository, issue and PR links.
- `docs/review_notes.md`: honest review status and viva preparation.

The original starter is preserved in `docs/evidence/starter_registration.py`.
The initial run had 39 passing and 14 failing cases. The pre-fix combined run
had 49 passing and 14 failing cases. No expected values were changed to make
these failures pass. W04-W06 isolate waitlist application using a stub; this
limitation is explained in the report.

## GitHub history

Repository: https://github.com/theafrazkhan/SQE-Assignment-2 (private).
Branches: `blackbox-testing`, `whitebox-testing`, `defect-fixes`.
Five issues describe the distinct defects; three PRs separate the test designs,
structural work, and corrections. GitHub Actions retains test and coverage
artifacts even on legitimate failures.

This is solo work. Independent peer review is **pending**, as agreed with Afraz.
No second member, approval, or feedback has been invented. Confirm with the
instructor how the collaborative review criterion applies to a solo submission.
The private repository must be shared with the instructor for assessment.

## Rebuild documents (optional)

```bash
python -m pip install -r requirements-docs.txt
python tools/make_sheets.py
python tools/make_cfg.py
python tools/make_report.py
```

To save a fresh regression phase without overwriting the original evidence:

```bash
python tools/run_evidence.py another-regression tests/
```

Use a new phase name. The evidence includes commands, versions, source commit
and source SHA-256. The report compares separate statement and branch counts,
not just the combined percentage printed in the coverage terminal summary.
