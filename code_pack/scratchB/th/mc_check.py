# Independent per-person Monte Carlo check of the wait model (own queue logic; shares only vehicle/stop-offset inputs and the demand cells).
import sys,json,random,math;sys.path.insert(0,'.')
from wsim import build_D,veh_row,old35,SP
import numpy as np
B=json.load(open(SP+'th/base.json'))
D=None
def run(veh,rng,D):
    W=[];left=0;late=0;gon=0
    for h,(g,r) in D.items():
        if h<7 or h>21: continue
        # ---- return: persons walk to their stop in [h:00,h:15); a vehicle reaching the stop later takes them FIFO while seats remain
        if r:
            q={s:sorted(rng.uniform(h*60,h*60+15) for _ in range(int(round(m)))) for s,m in r.items()}
            ptr={s:0 for s in q};used={}
            ev=sorted((v['t']+o,i,s) for i,v in enumerate(veh) for s,o in v['stops'].items() if s in q)
            for t,i,s in ev:
                while ptr[s]<len(q[s]) and q[s][ptr[s]]<=t and used.get(i,0)<veh[i]['cap']:
                    W.append(t-q[s][ptr[s]]);used[i]=used.get(i,0)+1;ptr[s]+=1
            left+=sum(len(q[s])-ptr[s] for s in q)
        # ---- going: persons reach P0 in [h*60-31,h*60-30); each vehicle leaving later takes them FIFO if it serves their stop
        if g:
            P=sorted((rng.uniform(h*60-31,h*60-30),s) for s,m in g.items() for _ in range(int(round(m))))
            alive=[True]*len(P);gon+=len(P)
            for v in sorted(veh,key=lambda x:x['t']):
                free=v['cap']
                for k,(a,s) in enumerate(P):
                    if free<=0:break
                    if alive[k] and a<=v['t'] and s in v['stops']:
                        W.append(v['t']-a);alive[k]=False;free-=1
                        if v['t']+v['stops'][s]>h*60: late+=1
            left+=sum(alive)
    W=np.array(W);return W.mean(),np.percentile(W,90),left,late,gon
res={}
for day in ['จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์']:
    cells=B['round_on']['days'][day]['cells'];rows=B['round_on']['days'][day]['rows']
    Dd=build_D(cells)
    for h,(g,r) in Dd.items():
        for v in list(g.values())+list(r.values()): assert abs(v-round(v))<1e-9
    NEW=[veh_row(r) for r in rows];OLD=old35()
    res[day]={}
    for name,veh in (('old',OLD),('new',NEW)):
        rng=random.Random(20260101);R=[run(veh,rng,Dd) for _ in range(200)]
        A=np.array([x[:3] for x in R])
        res[day][name]=dict(mean=float(A[:,0].mean()),mean_lo=float(np.percentile(A[:,0],2.5)),mean_hi=float(np.percentile(A[:,0],97.5)),
                   p90=float(A[:,1].mean()),p90_lo=float(np.percentile(A[:,1],2.5)),p90_hi=float(np.percentile(A[:,1],97.5)),
                   left=float(A[:,2].mean()),reps=len(R),late_mean=float(np.mean([x[3] for x in R])),go_n=R[0][4])
json.dump(res,open('mc_check.json','w'),ensure_ascii=False,indent=1)
for d,v in res.items(): print(d,{k:(round(x['mean'],2),round(x['p90'],1),round(x['left'],1),round(x['late_mean'],2),x['go_n']) for k,x in v.items()})
