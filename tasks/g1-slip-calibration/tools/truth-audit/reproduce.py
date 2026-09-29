"""Rebuild frozen fixtures in a temporary tree; never overwrite evaluated data."""
from pathlib import Path
import tempfile,shutil,json,hashlib,sys
HERE=Path(__file__).resolve().parent
TASK=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load_functions(script,cut,root):
 ns={'__file__':str(root/'tools'/script.name),'__name__':'forward_generation'}
 exec(compile(script.read_text().split(cut)[0],str(script),'exec'),ns)
 return ns
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);base=root/'base';base.mkdir()
 for folder in [base,root]:
  (folder/'environment').mkdir(exist_ok=True)
  for n in ['kinematics.py','camera_model.py']:shutil.copy2(TASK/'environment'/n,folder/'environment'/n)
 shutil.copytree(HERE/'sources',base/'tools/sources')
 provenance=json.loads((TASK/'DATA_PROVENANCE.json').read_text())
 for e in provenance['episodes']:
  assert sha(HERE/'sources'/('episode_%d.json'%e['episode']))==e['sha256'],'source hash mismatch'
 ns=load_functions(HERE/'source_v5_build.py',"campaign('example_a'",base)
 for name,eps,seed,public in [('example_a',[0,0,0],106111,True),('example_b',[0,0,0],106102,True),('fresh_a',[1,2,3],681401,False),('fresh_b',[3,1,2],681402,False)]:ns['campaign'](name,eps,seed,public)
 ns=load_functions(HERE/'build.py',"base=ROOT/",root)
 for name,source,seed,public,slips in [('example_a','example_a',61101,True,True),('example_b','example_b',61102,True,True),('held_a','fresh_a',61901,False,True),('held_b','fresh_b',61902,False,True),('held_no_slip','fresh_b',61903,False,False)]:
  sub='environment/public' if public else 'tests/cases'
  ns['create'](base/sub/source,root/sub/name,seed,slips=slips)
 rows=[]
 for sub in ['environment/public','tests/cases']:
  for old in sorted((TASK/sub).rglob('*')):
   if not old.is_file():continue
   new=root/old.relative_to(TASK)
   rows.append({'path':str(old.relative_to(TASK)),'match':new.exists() and old.read_bytes()==new.read_bytes(),'frozen_sha256':sha(old),'generated_sha256':sha(new) if new.exists() else None})
 report={'all_byte_identical':all(x['match'] for x in rows),'files':rows,'source_hashes_verified':True}
 print(json.dumps(report,indent=2))
 if '--report' in sys.argv:Path(sys.argv[sys.argv.index('--report')+1]).write_text(json.dumps(report,indent=2))
 assert report['all_byte_identical'],'Generated fixture differs from frozen fixture; inspect report'
