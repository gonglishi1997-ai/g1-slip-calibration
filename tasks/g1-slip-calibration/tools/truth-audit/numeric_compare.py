"""Strict structure/integer comparison; absolute tolerance only for finite floats."""
import math

def equivalent(a,b,atol=1e-10):
    if type(a) is not type(b):
        return False
    if isinstance(a,dict):
        return a.keys()==b.keys() and all(equivalent(a[k],b[k],atol) for k in a)
    if isinstance(a,list):
        return len(a)==len(b) and all(equivalent(x,y,atol) for x,y in zip(a,b))
    if isinstance(a,float):
        return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=atol
    return a==b
