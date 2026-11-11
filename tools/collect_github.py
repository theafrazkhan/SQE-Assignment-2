"""Save real GitHub run, issue and PR states without inventing evidence."""
import json
import os
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GH=os.environ.get('SQE_GH','gh')
REPO='theafrazkhan/SQE-Assignment-2'
def gh(*args):
 return subprocess.check_output([GH,*args,'--repo',REPO],cwd=ROOT,text=True)
runs=json.loads(gh('run','list','--limit','30','--json','databaseId,headBranch,headSha,event,status,conclusion,url,createdAt'))
(ROOT/'docs/github_runs.json').write_text(json.dumps(runs,indent=2)+'\n')
for run in runs:
 if run['status']=='completed':
  details=gh('run','view',str(run['databaseId']),'--json','jobs,conclusion,url,headBranch,headSha')
  (ROOT/'docs/evidence'/f"actions-{run['databaseId']}.json").write_text(details)
  if run['conclusion']=='failure':
   log=gh('run','view',str(run['databaseId']),'--log-failed')
   (ROOT/'docs/evidence'/f"actions-{run['databaseId']}-failed.txt").write_text(log)
for kind,fields in [('issue','number,title,state,url'),('pr','number,title,state,url,baseRefName,headRefName,reviewDecision,mergedAt')]:
 data=gh(kind,'list','--state','all','--json',fields)
 (ROOT/'docs/evidence'/f'github-{kind}-state.json').write_text(data)
print(json.dumps([{'branch':r['headBranch'],'status':r['status'],'conclusion':r['conclusion'],'url':r['url']} for r in runs],indent=2))
