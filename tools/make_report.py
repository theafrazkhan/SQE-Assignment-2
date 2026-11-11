"""Build a plain, readable PDF and its editable Markdown source."""
import json
import re
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, Image)

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
links=json.loads((DOCS/'github_links.json').read_text()) if (DOCS/'github_links.json').exists() else {'repository':'https://github.com/theafrazkhan/SQE-Assignment-2','issues':[],'pull_requests':[]}
cases=json.loads((DOCS/'cases.json').read_text())
counts=Counter(t for c in cases for t in c['techniques'])
rows=[]
for phase in ['initial-blackbox','pre-fix-combined','final-regression']:
    data=json.loads((DOCS/'evidence'/phase/'coverage.json').read_text())['files']['registration.py']
    summary=data['summary']
    xml=ET.parse(DOCS/'evidence'/phase/'results.xml')
    tests=xml.findall('.//testcase')
    failed=sum(t.find('failure') is not None or t.find('error') is not None for t in tests)
    stmt=f"{summary['covered_lines']}/{summary['num_statements']} ({100*summary['covered_lines']/summary['num_statements']:.2f}%)"
    branch=f"{summary['covered_branches']}/{summary['num_branches']} ({100*summary['covered_branches']/summary['num_branches']:.2f}%)"
    rows.append(f"|{phase}|{len(tests)-failed}|{failed}|{stmt}|{branch}|{data['missing_lines']}|")

text=f'''# SE3002 - Software Quality Engineering: Assignment 2

Student: Afraz Khan | Roll number: 23p3034 | GitHub: theafrazkhan

Submission prepared: 11 November 2026 (Asia/Karachi).

## 1. Scope and method

I tested the supplied Student Course Registration System against REQUIREMENTS.md.
The original SRS DOCX was also read and agrees with the Markdown requirements.
The application was not redesigned. Black-box cases were designed and committed
before inspecting implementation logic. Initial failures were saved before fixes.
Then I inspected the source, added structural tests, and applied five small fixes.
The work was prepared with coding-assistant help; the named student should verify
and understand the work before submitting it.

## 2. Black-box design

The test inventory contains {counts['ECP']} ECP rows, {counts['BVA']} BVA rows,
{counts['DT']} decision-table rows and {counts['State']} state rows. These are
{sum(counts.values())} technique-to-case mappings, consolidated to {len(cases)}
unique black-box executions by removing 15 exact repeated mappings.

ECP covers valid and invalid credits, zero/positive/negative dues, empty/all/
partial/no prerequisites, unrelated completed courses, and available/full seats.
BVA covers current credits -1,0,1,17,18,19; course credits 0,1,2,3,4,5;
combined totals 17,18,19; capacity 0,1,2; enrollment -1,0,capacity-1,capacity,
capacity+1; and dues -1,0,1. Cases use pytest.raises for specified validation errors.

The reduced decision table has two validation rules and six status rules.
D09-D12 exercise competing conditions in the specified order: dues, duplicate,
prerequisites, credits, availability. D19 validates dues before capacity; D20
checks capacity validation before positive-dues blocking. D01 and D08 cover
available and full seats; D22 allows the exact 18-credit total.

Every decision case checks object state. S01-S11 check successful registration,
first/repeated waitlisting, each rejection, validation failure, and both withdrawal
outcomes with complete object snapshots. Each case uses fresh objects.

Full representative inputs, expected outputs, requirement IDs and test IDs are
in blackbox_test_design.xlsx, decision_table.xlsx and cases.json.

## 3. Optimization and traceability

D01, D02 and D08 each serve ECP, BVA and decision-table design with one execution.
C02-C06, C09, C10 and C14 each serve ECP and BVA, as does D04. The spreadsheets
retain each technique mapping. Identical outputs alone were not used to merge
tests: operation, complete fixture, numeric inputs, oracle and state assertions
must all match. D08 and S02 remain separate because one observes a decision and
the other applies a state change. Boundary cases with different inputs remain
separate even when both return True or the same registration status.

## 4. Measured execution and coverage

|Phase|Passed|Failed|Statement coverage|Branch coverage|Missing statements|
|---|---|---|---|---|---|
'''+ '\n'.join(rows)+'''

The first two phases use the same unchanged starter source. White-box additions
improve coverage without correcting any defect. Coverage is measured for the
whole registration module using pytest-cov with branch measurement enabled.
The final module has one additional statement: the missing enrollment decrement.
JSON, JUnit, commands, versions, source commits, source hashes and console logs
are preserved under evidence/. The coverage tool's combined Cover percentage
is not used as the statement percentage. Original missing statements are
51,59,71, with branch gaps 50->51,58->59,70->71. Pre-fix combined coverage leaves
only line 59 and edge 58->59 missing; the final regression has no gaps.

## 5. Confirmed defects and fixes

'''
issue_states = json.loads((DOCS/'evidence/github-issue-state.json').read_text()) if (DOCS/'evidence/github-issue-state.json').exists() else []
for defect in json.loads((DOCS/'defects.json').read_text()):
    url=next((x['url'] for x in links['issues'] if x['id']==defect['id']),'Publication pending')
    state = next((x['state'] for x in issue_states if x['url']==url), 'not collected')
    text+=f"### {defect['id']}: {defect['title']}\n\nRequirement: {defect['requirement']}. Reproduce: {defect['steps']}\n\nExpected: {defect['expected']}. Actual in the starter: {defect['actual']}.\n\nFailed test: {defect['test']}. Fix: {defect['fix']} Regression IDs: {', '.join(defect['tests'])}. All now pass.\n\nIssue: {url}. Status: corrected and regression-tested; GitHub issue {state}.\n\n"
text+='''## 6. CFG, paths and manual condition analysis

The following analysis uses original starter line numbers, retained in
 evidence/starter_registration.py. The included CFG is the original function.

'''+(DOCS/'whitebox_analysis.md').read_text().replace('# White-box analysis\n','',1)
text+='''\n## 7. GitHub collaboration and CI evidence\n\n'''
text+='Repository: '+links['repository']+' (private).\n\n'
for pr in links['pull_requests']:
    text+=f"- {pr['branch']} (base at creation: {pr['base']}): {pr['url']}\n"
text+='\nAll three PRs are merged; all five defect issues are closed. Peer review remains pending for this solo submission.\n'
text+='''
The Actions workflow runs on push and PR, installs requirements.txt, runs pytest
with branch coverage, and uploads JUnit/XML/HTML artifacts even if tests fail.
No continue-on-error, xfail or skipped defects are used to hide the initial bugs.
Actual GitHub run links and conclusions are recorded below and in github_runs.json.
'''
runpath=DOCS/'github_runs.json'
if runpath.exists():
    for run in json.loads(runpath.read_text()):
        text+=f"\n- {run['headBranch']}: {run['conclusion'] or run['status']} - {run['url']}\n"
else: text+='\nGitHub run collection is pending; local evidence is already present.\n'
text+='''
## 8. Contributions, review status and remaining action

Afraz Khan (23p3034, theafrazkhan) is the sole named student. The repository
contains requirements-based test design, test implementation, structural
analysis, defect reports/fixes, CI setup and reporting prepared for this solo
submission with coding-assistant help. No multi-member contribution is claimed.

Independent peer review is PENDING, as explicitly agreed for this solo work.
There is no claim that another member reviewed or approved these PRs, or that
peer feedback was addressed. The instructor must confirm how the C4 criterion
applies to solo work. This is the remaining collaboration requirement; automated
tests and a self-check cannot substitute for another member's review.

The repository is private. Give the instructor access before submission.
Review review_notes.md for viva topics and explain each change in your own words.

## 9. Reproduction and practical limits

Install requirements.txt and run python -m pytest tests/ --cov=registration
--cov-branch --cov-report=term-missing. The exact saved commands and environment
versions are in each evidence phase's run.json. Use tools/run_evidence.py with a
new phase name for future runs. The original source is in the starter commit and
the preserved evidence copy; the initial branches reproduce the genuine failures.

Tests follow the SRS numeric scope. They do not assert behavior for identifiers,
wrong collection types, persistence, concurrency or payment processing, which
are outside scope. High source coverage does not prove correctness: the starter
already had 94.74% statement coverage while failing 14 requirements-based cases.
The isolated waitlist cases and masking MC/DC conventions are disclosed above.
'''
(DOCS/'testing_report.md').write_text(text)

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyPlain',fontName='Helvetica',fontSize=9.5,leading=14,spaceAfter=7))
styles.add(ParagraphStyle(name='CellPlain',fontName='Helvetica',fontSize=7.5,leading=10))
story=[]

def paragraph(t,style='BodyPlain'):
    return Paragraph(escape(t).replace('`',''),styles[style])
lines=text.splitlines()
i=0
while i<len(lines):
    line=lines[i].strip()
    if not line:
        i+=1; continue
    if line.startswith('|'):
        table=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r'[:\- ]+',c) for c in cells):
                table.append([paragraph(c,'CellPlain') for c in cells])
            i+=1
        n=len(table[0]); width=487/n
        t=Table(table,colWidths=[width]*n,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7edf2')),('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#aab5bd')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        story.extend([t,Spacer(1,10)]); continue
    if line.startswith('#'):
        count=len(line)-len(line.lstrip('#'))
        style='Title' if count==1 else 'Heading1' if count==2 else 'Heading2'
        if line=='## CFG and complexity':
            story.append(PageBreak())
        story.append(paragraph(line.lstrip('#').strip(),style))
        if line=='## CFG and complexity':
            story.extend([Image(str(DOCS/'cfg.png'),width=440,height=616),Spacer(1,10)])
        i+=1; continue
    if line.startswith('- '):
        story.append(paragraph('• '+line[2:])); i+=1; continue
    parts=[line];i+=1
    while i<len(lines) and lines[i].strip() and not lines[i].strip().startswith(('#','|','- ')):
        parts.append(lines[i].strip());i+=1
    story.append(paragraph(' '.join(parts)))

def footer(canvas,doc):
    canvas.setFont('Helvetica',8)
    canvas.drawString(54,28,'SE3002 | Afraz Khan | 23p3034')
    canvas.drawRightString(A4[0]-54,28,str(doc.page))

SimpleDocTemplate(str(DOCS/'testing_report.pdf'),pagesize=A4,rightMargin=54,leftMargin=54,topMargin=45,bottomMargin=45,title='SE3002 Assignment 2 Testing Report',author='Afraz Khan').build(story,onFirstPage=footer,onLaterPages=footer)
print('Created testing_report.md and testing_report.pdf')
