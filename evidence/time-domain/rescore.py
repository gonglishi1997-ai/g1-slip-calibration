import sys,json
from pathlib import Path
sys.path.insert(0,'/tests')
from check import grade_campaign
rows=[]
for p in sorted(Path('/replay').glob('*/*/output.json')):
 try:grade_campaign(Path('/tests/cases')/p.parent.name,json.loads(p.read_text()));ok=True;reason=''
 except Exception as e:ok=False;reason=str(e)
 rows.append(dict(agent=p.parent.parent.name,campaign=p.parent.name,passed=ok,reason=reason))
Path('/audit/RESCORE.json').write_text(json.dumps(rows,indent=2));print('outputs',len(rows),'accepted',sum(x['passed'] for x in rows))
