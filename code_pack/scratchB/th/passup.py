# passup.py - "pass-up" measure: share of passengers who were at a stop when a vehicle that serves the stop left full (so they could not board that vehicle).
# Same queue logic as fullday.sim_return / sim_going (copied, with extra bookkeeping); results are asserted equal to the original simulator.
import os,sys
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
from wsim import *
import fullday as F
def ret_pass(veh,dem,w0,w1,step=0.5):
    q={s:[] for s in dem};n=int(round((w1-w0)/step))
    for s,m in dem.items():
        for i in range(n):q[s].append([w0+(i+.5)*step,m/n,False])
    ev=sorted((v['t']+o,vi,s) for vi,v in enumerate(veh) for s,o in v['stops'].items() if s in dem)
    onb={};ptr={s:0 for s in dem};W=[];passed=0.0;ps={s:0.0 for s in dem}
    for t,vi,s in ev:
        free=veh[vi]['cap']-onb.get(vi,0)
        while free>1e-9 and ptr[s]<len(q[s]) and q[s][ptr[s]][0]<=t:
            a,m,_=q[s][ptr[s]];take=min(m,free);W.append((t-a,take,0));free-=take;onb[vi]=onb.get(vi,0)+take
            if take<m-1e-12:q[s][ptr[s]][1]=m-take
            else:ptr[s]+=1
        if free<=1e-9:
            for c in q[s][ptr[s]:]:
                if c[0]>t:break
                if not c[2]:c[2]=True;passed+=c[1];ps[s]+=c[1]
    left=sum(c[1] for s in q for c in q[s][ptr[s]:]);return W,left,passed,ps
def go_pass(veh,dem,w0,w1,start,step=0.25):
    n=int(round((w1-w0)/step));P=[]
    for s,m in dem.items():
        for i in range(n):P.append([w0+(i+.5)*step,s,m/n,False])
    P.sort(key=lambda x:x[0]);W=[];passed=0.0;ps={s:0.0 for s in dem}
    for vi,v in sorted(enumerate(veh),key=lambda x:x[1]['t']):
        free=v['cap']
        for p in P:
            if free<=1e-9:break
            if p[0]>v['t'] or p[2]<=1e-12 or p[1] not in v['stops']:continue
            take=min(p[2],free);late=1 if v['t']+v['stops'][p[1]]>start else 0
            W.append((v['t']-p[0],take,late));p[2]-=take;free-=take
        if free<=1e-9:
            for p in P:
                if p[0]>v['t']:break
                if p[2]>1e-12 and p[1] in v['stops'] and not p[3]:p[3]=True;passed+=p[2];ps[p[1]]+=p[2]
    left=sum(p[2] for p in P);return W,left,passed,ps
def pass_eval(veh,D,hi=31,lo=30,detail=False):
    """returns {'ret':[served,passed],'go':[served,passed]} and per-cell dict; asserts waits equal the original simulator"""
    tot={'ret':[0.0,0.0],'go':[0.0,0.0]};cells={};stops={}
    for h,(g,r) in D.items():
        if h<7 or h>21:continue
        if r:
            W,l,ps,pst=ret_pass(veh,r,h*60,h*60+15);W0,l0=F.sim_return(veh,r,h*60,h*60+15)
            assert abs(sum(a*m for a,m,_ in W)-sum(a*m for a,m,_ in W0))<1e-6 and abs(l-l0)<1e-9
            sv=sum(m for _,m,_ in W);tot['ret'][0]+=sv;tot['ret'][1]+=ps;cells[f'ret{h:02d}']=[sv,ps]
            for st,m in r.items():stops[f'ret{h:02d}_P{st}']=[m,pst[st]]
        if g:
            W,l,ps,pst=go_pass(veh,g,h*60-hi,h*60-lo,h*60);W0,l0=F.sim_going(veh,g,h*60-hi,h*60-lo,h*60,step=0.25)
            assert abs(sum(a*m for a,m,_ in W)-sum(a*m for a,m,_ in W0))<1e-6 and abs(l-l0)<1e-9
            sv=sum(m for _,m,_ in W);tot['go'][0]+=sv;tot['go'][1]+=ps;cells[f'go{h:02d}']=[sv,ps]
            for st,m in g.items():stops[f'go{h:02d}_P{st}']=[m,pst[st]]
    return (tot,cells,stops) if detail else (tot,cells)
