"""Export the test inventory and decision table using simple spreadsheet formatting."""
import json
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
cases = json.loads((ROOT / 'docs/cases.json').read_text())

def finish(workbook, name):
    for sheet in workbook:
        sheet.freeze_panes = 'A2'
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill('solid', fgColor='244766')
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical='top', wrap_text=True)
            sheet.row_dimensions[row[0].row].height = 60
        for col in sheet.columns:
            width = min(65, max(15, max(len(str(c.value or '')) for c in col) // 2))
            sheet.column_dimensions[get_column_letter(col[0].column)].width = width
    workbook.save(ROOT / 'docs' / name)

book = Workbook()
book.remove(book.active)
for technique in ['ECP', 'BVA', 'DT', 'State']:
    sheet = book.create_sheet(technique)
    sheet.append(['Test ID', 'Requirement', 'Class / boundary / scenario', 'Representative inputs (overrides)', 'Expected result', 'Operation'])
    for c in cases:
        if technique in c['techniques']:
            sheet.append([c['id'], c['requirements'], c['description'], json.dumps(c['inputs']), str(c['expected']), c['kind']])
sheet = book.create_sheet('Defaults and optimization')
sheet.append(['Item','Details'])
sheet.append(['Defaults', 'S001; current=6; dues=0; completed={CS101,MATH101}; registrations={}; CS201; credits=3; capacity=2; enrolled=1; prerequisites={CS101,MATH101}; waitlist=[]'])
sheet.append(['Credit helper', 'current and new are explicit; prerequisites helper uses completed and required explicitly.'])
sheet.append(['Common assertions', 'Every decision preserves full state; every rejected register/withdraw preserves full state; successful mutations match FR-11/12/13.'])
for c in cases:
    if len(c['techniques'])>1:
        sheet.append([c['id'], ' + '.join(c['techniques']) + ': one execution, identical operation/input/state/oracle/assertions'])
sheet.append(['Technique rows', sum(len(c['techniques']) for c in cases)])
sheet.append(['Unique executions', len(cases)])
sheet.append(['Removed exact duplicates', sum(len(c['techniques']) for c in cases)-len(cases)])
# Attach measured outcomes without changing the original design oracle.
from xml.etree import ElementTree as ET
sheet = book.create_sheet('Execution results')
sheet.append(['Test ID', 'Initial starter', 'Final fixed module'])
results = {}
for phase in ['initial-blackbox', 'final-regression']:
    file = ROOT / 'docs/evidence' / phase / 'results.xml'
    results[phase] = {}
    if file.exists():
        for test in ET.parse(file).findall('.//testcase'):
            key = test.attrib['name'].split('[')[-1].rstrip(']')
            results[phase][key] = 'FAIL' if test.find('failure') is not None else 'PASS'
for case in cases:
    sheet.append([case['id'], results['initial-blackbox'].get(case['id'], 'Not run'), results['final-regression'].get(case['id'], 'Not run')])
finish(book, 'blackbox_test_design.xlsx')

book = Workbook()
sheet = book.active
sheet.title = 'Decision rules'
sheet.append(['Rule', 'Dues valid', 'Capacity/enrollment valid', 'Dues > 0', 'Duplicate', 'All prereqs', 'Credits eligible', 'Seat available', 'Expected', 'Test IDs'])
for row in [
['V1','F','-','-','-','-','-','-','ValueError: Invalid dues','D04,D19'],
['V2','T','F','-','-','-','-','-','ValueError: Invalid capacity or enrollment','D13,D16,D18,D20'],
['R1','T','T','T','-','-','-','-','DUES_BLOCK','D02,D03,D09'],
['R2','T','T','F','T','-','-','-','ALREADY_REGISTERED','D05,D10'],
['R3','T','T','F','F','F','-','-','PREREQUISITES_MISSING','D06,D11,D21'],
['R4','T','T','F','F','T','F','-','CREDIT_LIMIT','D07,D12'],
['R5','T','T','F','F','T','T','F','WAITLISTED','D08,D15'],
['R6','T','T','F','F','T','T','T','REGISTERED','D01,D14,D17,D22']]: sheet.append(row)
sheet = book.create_sheet('Priority examples')
sheet.append(['ID','Dues > 0','Duplicate','All prereqs','Credits eligible','Seat available','Expected'])
for row in [('D09','T','T','F','F','F','DUES_BLOCK'),('D10','F','T','F','F','F','ALREADY_REGISTERED'),('D11','F','F','F','F','F','PREREQUISITES_MISSING'),('D12','F','F','T','F','F','CREDIT_LIMIT')]: sheet.append(row)
sheet = book.create_sheet('Notes')
sheet.append(['Item','Meaning'])
sheet.append(['Dash','Do not care: earlier rule determines the result. This differs from NE (not evaluated) in condition tables.'])
sheet.append(['Source','FR-04 to FR-10 and FR-15. Expected results derive from requirements.'])
sheet.append(['Validation','Credit validation occurs when credit eligibility is reached; FR-09 earlier statuses take priority for valid numeric fixtures.'])
finish(book, 'decision_table.xlsx')
print('Created both required workbooks')
