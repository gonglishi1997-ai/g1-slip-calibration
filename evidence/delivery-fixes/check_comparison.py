import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1])/'tools/truth-audit'))
from numeric_compare import equivalent
cases=[('reported_roundoff',699.9486180216911,699.948618021691,True),('above_tolerance',1.,1.+1e-8,False),('integer_identity',1,2,False),('integer_vs_float',1,1.,False),('boolean_vs_integer',True,1,False),('missing_key',{'a':1},{},False),('label_change','left:1','left:2',False),('reordered_array',[1,2],[2,1],False),('nonfinite',float('nan'),float('nan'),False)]
rows=[]
for name,a,b,want in cases:
 actual=equivalent(a,b);assert actual==want;rows.append(dict(name=name,accepted=actual,expected=want))
print(json.dumps(rows,indent=2))
