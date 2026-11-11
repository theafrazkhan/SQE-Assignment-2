# Requirements-based black-box design

Prepared before inspecting registration.py. REQUIREMENTS.md is the oracle.
The full case inventory, inputs, requirements, expected outputs and technique tags
are stored in cases.json and exported to blackbox_test_design.xlsx.

Defaults: student S001, 6 current credits, zero dues, completed CS101 and MATH101,
no registrations; course CS201, 3 credits, capacity 2, enrollment 1, prerequisites
CS101 and MATH101, empty waitlist. Each case gets fresh objects.
Decision tests verify FR-10 even when an exception is expected. State cases verify
all student/course fields with before/after snapshots.

## Equivalence classes
Credits: valid current/course, invalid current below/above range, invalid course
below/above range; valid totals within/above limit. Dues: zero, positive, negative.
Prerequisites: empty, all, partial, none, unrelated. Availability: free or full.
Each class maps to an executable ID in cases.json.

## Decision table (first matching rule)
Validation occurs first: negative dues; then invalid capacity/enrollment.
For valid data: dues positive -> DUES_BLOCK; otherwise duplicate ->
ALREADY_REGISTERED; otherwise missing prerequisite -> PREREQUISITES_MISSING;
otherwise total >18 -> CREDIT_LIMIT; otherwise full -> WAITLISTED; otherwise
REGISTERED. D09-D12 cover several competing conditions and their priority.

## Optimization
One case can carry several technique tags. D01 is shared by ECP, BVA (dues=0,
enrollment=capacity-1), and decision table; D02 by all three; D08 by all three.
C02-C06, C09, C10 and C14 share ECP/BVA execution. D04 shares ECP/BVA.
Separate source-technique rows point to the same test ID in the spreadsheet.
These are exact duplicates because operation, complete starting state, input,
expected result and state assertions match. Tests with the same status but a
different initial state or operation remain separate (e.g. D08 and S02).
No marks are claimed for identifiers or types outside the stated numeric scope.
