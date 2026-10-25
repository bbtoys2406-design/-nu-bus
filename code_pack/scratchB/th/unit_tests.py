# Unit tests of the wait model (wsim/fullday). Prints a JSON of results and asserts analytic expectations.
import sys,json;sys.path.insert(0,'.')
from wsim import *
import numpy as np
def m(W):
    a=np.array([x[0] for x in W]);w=np.array([x[1] for x in W]);return float((a*w).sum()/w.sum()) if len(W) else None, float(w.sum())
OUT={}
v=[dict(t=15,stops={5:0.0},cap=1000)]
W,l=sim_return(v,{5:100},0,15);OUT['T1']=(*m(W),float(l))
v=[dict(t=15,stops={5:0.0},cap=50),dict(t=20,stops={5:0.0},cap=1000)]
W,l=sim_return(v,{5:100},0,15);OUT['T2']=(*m(W),float(l))
W,l=sim_return(v[:1],{5:100},0,15);OUT['T2b']=(*m(W),float(l))
v=[dict(t=-25,stops={7:5.0},cap=35),dict(t=-10,stops={7:5.0},cap=35)]
W,l=sim_going(v,{7:40},-31,-30,0,step=0.25);OUT['T3']=(*m(W),float(l),max(x[2] for x in W))
v=[dict(t=-25,stops={8:5.0},cap=35)]
W,l=sim_going(v,{7:40},-31,-30,0,step=0.25);OUT['T4']=(None,0.0,float(l))
v=[dict(t=-3,stops={7:5.0},cap=35)]
W,l=sim_going(v,{7:10},-31,-30,0,step=0.25);OUT['T5']=(*m(W),float(l),min(x[2] for x in W))
v=[dict(t=15,stops={1:0.0,2:2.0},cap=35)]
W,l=sim_return(v,{1:30,2:10},0,15);OUT['T6']=(*m(W),float(l))
exp={'T1':(7.5,100,0),'T2':(10.0,100,0),'T2b':(11.25,50,50),'T3':(7.375,40,0),'T4':(None,0,40),'T5':(27.5,10,0),'T6':None}
for k,e in exp.items():
    if e is None: continue
    o=OUT[k]
    assert (o[0] is None and e[0] is None) or abs(o[0]-e[0])<1e-6,(k,o,e)
    assert abs(o[1]-e[1])<1e-6 and abs(o[2]-e[2])<1e-6,(k,o,e)
assert OUT['T3'][3]==0 and OUT['T5'][3]==1
assert abs(OUT['T6'][1]-35)<1e-6 and abs(OUT['T6'][2]-5)<1e-6
json.dump(OUT,open('/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/th/unit_tests.json','w'))
print(json.dumps(OUT))
