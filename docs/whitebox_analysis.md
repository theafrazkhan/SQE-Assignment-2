# White-box analysis

Line references below refer to the preserved starter in evidence/starter_registration.py.
Black-box design and its initial run were completed before source inspection.

## CFG and complexity

See cfg.png. Rectangles are return/raise nodes (processing); diamonds are predicate
nodes. ENTRY and EXIT are the two control nodes. All explicit returns and raises
connect to one synthetic EXIT. Calls to the two helpers are atomic processing
within their predicate: their internal decisions and implicit exception edges
are not expanded into this intraprocedural graph. W02/W03 separately test propagation.

At source-if level there are seven predicates (lines 46,48,50,52,54,56,58).
With entry, seven decisions, eight terminal actions and exit: N=17, E=23.
V(G)=23-17+2=8, matching 7+1.

For the explicit short-circuit convention in cfg.png, line 48 expands into:
A = 0 <= enrolled; B = enrolled <= capacity; C = capacity < 1.
The decision is NOT(A AND B) OR C. B is skipped when A is false; C is skipped
when A or B is false. This replaces one predicate with three: N=19, E=27.
V(G)=27-19+2=10, matching 9+1. Both counts describe the same function at
different granularities. pytest-cov counts source branches, not these atomic edges.

## Independent basis paths

Use the expanded graph. Prefix ENTRY and suffix EXIT are implicit below.
Each path adds a distinct terminal edge or a new validation-failure edge.
Paths are structural; the last path cannot execute with the starter's guards.

|Path|Predicate route and terminal|Representative case|
|---|---|---|
|P1|D1 F,A T,B T,C F,D3 F,D4 F,D5 F,D6 F,D7 F -> R8|D01 / W07|
|P2|D1 T -> R1|D04|
|P3|D1 F,A F -> R2|D16 / W08|
|P4|D1 F,A T,B F -> R2|D18 / W09|
|P5|D1 F,A T,B T,C T -> R2|D13 / W10|
|P6|D1 F,A T,B T,C F,D3 T -> R3|W01|
|P7|valid prefix,D3 F,D4 T -> R4|D05|
|P8|valid prefix,D3 F,D4 F,D5 T -> R5|D06|
|P9|valid prefix,D3 F,D4 F,D5 F,D6 T -> R6|D07|
|P10|valid prefix,D3 F,D4 F,D5 F,D6 F,D7 T -> R7|Infeasible before fix; D08 after fix|

Line 48 requires enrolled <= capacity to continue, while line 58 requires
enrolled > capacity for WAITLISTED. Therefore P10 is contradictory, even for
invalid inputs: validation raises before reaching it. No fabricated test or
coverage exclusion is used. After the equality fix, D08 executes this path.

## Structural additions and coverage gaps

W01 adds the dues >1000 true edge and line 51. W02/W03 verify exceptions
propagating from the credit helper without mutation. W04-W06 isolate
register_course by stubbing only registration_decision's returned status:
W04 executes the previously unreachable line 71; W05 exercises an existing ID;
W06 tests the false first operand and skipped membership check.
These are unit tests of the application layer, not evidence that the original
registration_decision can return WAITLISTED. W07-W10 target each short-circuit
validation outcome. Some overlap with black-box cases is intentional structural
traceability; the black-box technique optimization does not remove these additions.

The initial missing statements are 51,59,71; missing branches are
50->51,58->59,70->71. With white-box additions before fixes, only 59 and
58->59 remain missing. The final fixed module has no uncovered statements
or source branches. Detailed totals are in testing_report.md and evidence JSON.
Coverage percentages are measured separately as covered statements/total
statements and covered branches/total branches; the terminal's Cover column
combines the two and must not be mislabeled as statement coverage.

## Atomic conditions in registration_decision

|Atom|Meaning in original function|True case|False case|
|---|---|---|---|
|D1|dues < 0|D04|D01|
|A|0 <= enrolled|W07|W08|
|B|enrolled <= capacity (only when A is true)|W07|W09|
|C|capacity < 1 (only when A and B are true)|W10|W07|
|D3|dues > 1000|W01|D01|
|D4|code in registered_courses|D05|D01|
|D5|not prerequisites_satisfied(...)|D06|D01|
|D6|not check_credit_limit(...)|D07|D01|
|D7|enrolled > capacity|Infeasible|D01|

Scope of the manual condition percentage: these nine atomic predicates in the
requested function. Helper internals are outside this scope; the additional
register_course compound decision is analyzed separately below. A returned
helper result is one atom at this function's level.
Initial black-box: 16 of 18 evaluated True/False outcomes = 88.89% (D3 true and
D7 true missing). Pre-fix combined: 17/18 = 94.44%, D7 true infeasible. Fixed:
18/18 = 100% with D3 now dues >0 and D7 now enrolled == capacity.
These are manual condition results; pytest-cov does not measure them.

## Short-circuit truth table and MC/DC for validation

NE means Python did not evaluate that operand, and is not counted as True/False.
D is NOT(A AND B) OR C, where True raises the validation exception.

|Case|enrolled|capacity|A|B|C|D|
|---|---|---|---|---|---|---|
|W07|0|1|T|T|F|F|
|W08|-1|1|F|NE|NE|T|
|W09|2|1|T|F|NE|T|
|W10|0|0|T|T|T|T|

A independent effect: W07/W08. In W08, latent B is T (-1<=1) and latent C
is F (1<1), matching W07; both are masked by A being false.
B independent effect: W07/W09. A stays T; latent C stays F (capacity=1).
C independent effect: W07/W10. A and B stay T; C changes F->T.
All three pairs change D. Thus 3/3 atomic conditions have a masking MC/DC
pair (100%) for this compound decision. This explicitly allows operands
skipped by short-circuiting. Strict all-operands-evaluated unique-cause MC/DC
is not claimed: Python necessarily skips B/C for relevant invalid rows.
Each atom is actually observed both T and F over the four tests: 6/6 condition
outcomes, 100%. Changing input values is allowed as long as the other atomic
truth values remain fixed or masked as stated.

## AND decision in register_course (line 70)

A = decision == WAITLISTED; B = student ID not in waitlist; D = A AND B.
The table is reached only when the preceding REGISTERED condition is false.

|Case|Returned status|Waitlist before|A|B|D|
|---|---|---|---|---|---|
|W04|WAITLISTED|[]|T|T|T|
|W05|WAITLISTED|[S001]|T|F|F|
|W06|DUES_BLOCK|[]|F|NE|F|

W04/W06 show A's independent effect with latent B=T fixed. W04/W05 show
B's independent effect with A=T fixed. Masking MC/DC is 2/2=100%; evaluated
condition outcomes are 4/4=100%. Before fixes these rows use the documented
stub; after fixes the black-box S02/S03/S04 cases exercise the corresponding
end-to-end behaviors. No manual percentage here is inferred from branch coverage.
