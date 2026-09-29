from pathlib import Path
import shutil,tempfile,subprocess,json,os
rows=[]
with tempfile.TemporaryDirectory() as td:
 t=Path(td);inp=t/'input';shutil.copytree('/source/tests/cases/held_a',inp)
 rec=json.loads((inp/'campaign.json').read_text())['records'][-1];p=inp/rec/'camera.bin';b=bytearray(p.read_bytes());b[:4]=b'NOPE';p.write_bytes(b)
 for name,program in [('before','/audit/reference_before.py'),('after','/source/solution/calibrate.py')]:
  out=t/'result.json';out.write_text('old result');run=subprocess.run(['python',program,str(inp),str(out)],capture_output=True,env=dict(os.environ,PYTHONPATH='/app'))
  rows.append(dict(version=name,exit_code=run.returncode,stale_output_exists=out.exists()))
assert rows[0]['exit_code']!=0 and rows[0]['stale_output_exists']
assert rows[1]['exit_code']!=0 and not rows[1]['stale_output_exists']
Path('/audit/stale-probe.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows))
