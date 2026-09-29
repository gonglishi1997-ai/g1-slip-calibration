import sys,json,copy,importlib.util
from pathlib import Path
sys.path.insert(0,'/tests')
import check
spec=importlib.util.spec_from_file_location('before','/audit/check_before.py');before=importlib.util.module_from_spec(spec);spec.loader.exec_module(before)
rows=[]
for name,t,v,want in [('valid',[.1,9.9],[0,960],True),('exact_boundary',[0,10],[480,480],True),('nominal_low_exposure_valid',[-.001],[960],False),('nominal_high_exposure_valid',[10.001],[0],False),('exposure_low',[.001],[0],False),('exposure_high',[9.999],[960],False),('nonfinite',[float('nan')],[480],False)]:
 try:check.check_time_domain(t,v,.02,0,10);passed=True;reason='accepted'
 except AssertionError as e:passed=False;reason=str(e)
 assert passed==want
 rows.append(dict(name=name,accepted=passed,expected=want,reason=reason))
cases=[]
for case in sorted(Path('/tests/cases').iterdir()):
 truth=json.loads((case/'answer.json').read_text());check.grade_campaign(case,truth)
 for which in ['low','high']:
  out=copy.deepcopy(truth);rec=next(iter(out['records']));p=json.loads((case/rec/'private.json').read_text());s=json.loads((case/rec/'states.json').read_text())
  i=min(range(len(p['times'])),key=lambda j:p['times'][j]) if which=='low' else max(range(len(p['times'])),key=lambda j:p['times'][j])
  delta=(s[0]['timestamp']-.001 if which=='low' else s[-1]['timestamp']+.001)-p['times'][i]
  out['records'][rec]['clocks'][str(p['boots'][i])]['offset']+=delta
  result={}
  for label,grader in [('before',before),('after',check)]:
   try:grader.grade_campaign(case,out);result[label]='accepted'
   except Exception as e:result[label]='rejected: '+str(e)
  cases.append(dict(campaign=case.name,mutation=which,**result))
report=dict(boundary_controls=rows,truth_campaigns_passed=3,actual_campaign_mutations=cases,note='Synthetic boundary controls isolate time-domain validation; actual fixed-data mutations may already fail other original checks. No model calls.')
Path('/audit/RESULTS.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
