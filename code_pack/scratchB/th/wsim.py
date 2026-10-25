import sys,os,json
SP='/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/'
os.chdir(SP);sys.path.insert(0,SP)
import fullday as F, realtt as R
from fullday import sim_return, sim_going, summarize, veh_from_row, veh_loop, LINES
import numpy as np
DAYS=['จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์']
def build_D(cells,key='g',rkey='r'):
    """class-hour keyed demand: going of class hour h = arrival-hour cell h-1 (arrive 30 min before); return = arrival-hour cell h"""
    D={}
    for h in range(6,23):
        g={};r={}
        for sid,x in (cells.get(str(h-1)) or {}).items():
            if x[key]>1e-9: g[int(sid)]=x[key]
        for sid,x in (cells.get(str(h)) or {}).items():
            if x[rkey]>1e-9: r[int(sid)]=x[rkey]
        if g or r: D[h]=(g,r)
    return D
def veh_row(r):
    v=F.veh_from_row(r)
    if r['type'] in('loop-r','loop-y'): v['cap']=r['cap']
    return v
def old35(cap=35,Y=None):
    Y=R.yellow() if Y is None else Y
    return [F.veh_loop(t,'แดง',cap) for t in R.RED]+[F.veh_loop(t,'เหลือง',cap) for t in Y]
def evaluate(veh,D,hi=31,lo=30):
    per={}
    for h,(g,r) in D.items():
        if h<7 or h>21: continue
        if r:
            W,l=sim_return(veh,r,h*60,h*60+15);per[('ret',h)]=(sum(r.values()),W,l)
        if g:
            W,l=sim_going(veh,g,h*60-hi,h*60-lo,h*60,step=0.25);per[('go',h)]=(sum(g.values()),W,l)
    return per
def stats(per,kinds=None,keys=None):
    if keys: per={k:v for k,v in per.items() if k in keys}
    s=summarize(per,kinds)
    return None if s is None else dict(n=float(s['n']),served=float(s['served']),left=float(s['left']),mean=float(s['mean']),p90=float(s['p90']))
