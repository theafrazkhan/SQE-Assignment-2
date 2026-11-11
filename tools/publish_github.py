"""Publish issue/PR descriptions. Requires gh login and already-pushed branches."""
import json
import os
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GH=os.environ.get('SQE_GH','gh')
REPO='theafrazkhan/SQE-Assignment-2'

def gh(*args):
    return subprocess.check_output([GH,*args,'--repo',REPO],cwd=ROOT,text=True).strip()

links={'repository':'https://github.com/'+REPO,'issues':[],'pull_requests':[]}
existing=json.loads(gh('issue','list','--state','all','--json','title,url'))
for defect in json.loads((ROOT/'docs/defects.json').read_text()):
    title=defect['id']+': '+defect['title']
    found=next((x['url'] for x in existing if x['title']==title),None)
    body=f"""Requirement: {defect['requirement']}

Reproduction: {defect['steps']}

Expected: {defect['expected']}

Actual in unchanged starter: {defect['actual']}

Failed test: `{defect['test']}` in `tests/test_blackbox.py`.

Evidence: `docs/evidence/initial-blackbox/pytest.txt` (39 passed, 14 failed).

Proposed fix: {defect['fix']}

Status: reproduced on the original source; fixed and regression-tested on `defect-fixes`. Awaiting PR merge/review.
"""
    path=ROOT/'docs/evidence'/f"{defect['id']}-issue.md"
    path.write_text(body)
    url=found or gh('issue','create','--title',title,'--body-file',str(path))
    links['issues'].append({'id':defect['id'],'url':url})
    print(url,flush=True)

prs=[('blackbox-testing','main','Add requirements-based black-box tests and design sheets',
"""Add 53 requirements-based tests, with 21 ECP, 25 BVA, 11 decision-table and 11 state technique rows consolidated to 53 executions. Include both design spreadsheets, priority combinations, full-state assertions and a pytest/coverage Actions workflow.

Validation on unchanged starter: 39 passed, 14 failed. Expected values remain as specified in the SRS. Initial failures and coverage are retained in docs/evidence/initial-blackbox. These failures reproduce the five defect issues below.
"""),
('whitebox-testing','blackbox-testing','Add structural tests, CFG and manual MC/DC analysis',
"""Add ten structural cases for missing coverage, credit exception propagation, short-circuit validation and isolated waitlist application. Include the expanded CFG (V=10), feasible basis paths, and manual masking MC/DC tables.

Validation before fixes: 49 passed, 14 failed. Statement coverage is 56/57 and branch coverage is 25/26. Original WAITLISTED return remains infeasible. W04-W06 stub only the decision result; they do not establish end-to-end reachability. Full evidence is in docs/evidence/pre-fix-combined.
"""),
('defect-fixes','whitebox-testing','Fix five SRS violations and retain regression evidence',
"""Allow exactly 18 credits, require every prerequisite, block any positive dues, waitlist a full course, and reduce course enrollment during withdrawal. Each fix is a small change to the supplied implementation.

Validation: all 63 cases pass. Statement coverage is 58/58 and source branch coverage is 26/26. All initially failing tests pass with their expected values unchanged. Evidence: docs/evidence/final-regression.
""")]
existing=json.loads(gh('pr','list','--state','all','--json','headRefName,url'))
for head,base,title,body in prs:
    body+='\nDefects: '+', '.join(x['url'] for x in links['issues'])+'\n'
    if head=='defect-fixes':
        body+='\n'+ '\n'.join('Closes '+x['url'] for x in links['issues'])+'\n'
    body+='\nPeer review: pending a real second member. Afraz Khan is the only supplied member; no independent review is claimed.\n'
    path=ROOT/'docs/evidence'/f'{head}-pr.md'
    path.write_text(body)
    found=next((x['url'] for x in existing if x['headRefName']==head),None)
    url=found or gh('pr','create','--head',head,'--base',base,'--title',title,'--body-file',str(path))
    links['pull_requests'].append({'branch':head,'base':base,'url':url})
    print(url,flush=True)
(ROOT/'docs/github_links.json').write_text(json.dumps(links,indent=2)+'\n')
