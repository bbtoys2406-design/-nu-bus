# Planned vs. boarded load of CVRP trips in the fluid wait model, and effect of dropping the PM CVRP trip (all 5 days)
import sys,json;sys.path.insert(0,'.')
from wsim import *
from p4data import board_mass,on,DAYS
def sim_going_board(veh,dem,w0,w1,start,step=0.25):
    n=int(round((w1-w0)/step));P=[]
    for s,m in dem.items():
        for i in range(n):P.append([w0+(i+.5)*step,s,m/n])
    P.sort(key=lambda x:x[0]);onb={}
    for vi,v in sorted(enumerate(veh),key=lambda x:x[1]['t']):
        free=v['cap']
        for p in P:
            if free<=1e-9:break
            if p[0]>v['t'] or p[2]<=1e-12 or p[1] not in v['stops']:continue
            take=min(p[2],free);p[2]-=take;free-=take;onb[vi]=onb.get(vi,0)+take
    return onb
OUT={}
for d in DAYS:
    rows=on[d]['rows'];veh=[veh_row(r) for r in rows];Dd=build_D(on[d]['cells'])
    am=[i for i,r in enumerate(rows) if r['type'] in('cvrp','express') and r['label'].startswith('P0 →')]
    pm=[i for i,r in enumerate(rows) if r['type'] in('cvrp','express') and r['label'].startswith('P0 ←')]
    g7=Dd[8][0];onb_am=sim_going_board(veh,g7,8*60-31,8*60-30,8*60)   # going of class-hour 8 = arrival cell 7
    onb_pm=board_mass(veh,Dd[16][1],16*60,16*60+15)
    plan_am=sum(rows[i]['load'] for i in am);plan_pm=sum(rows[i]['load'] for i in pm)
    b_am=sum(onb_am.get(i,0) for i in am);b_pm=sum(onb_pm.get(i,0) for i in pm)
    base=stats(evaluate(veh,Dd),('ret','go'))
    veh2=[v for i,v in enumerate(veh) if i not in pm];no_pm=stats(evaluate(veh2,Dd),('ret','go'))
    OUT[d]=dict(plan_am=plan_am,board_am=b_am,plan_pm=plan_pm,board_pm=b_pm,n_pm=len(pm),base=base,no_pm=no_pm)
    print(d,'AM plan',plan_am,'board',round(b_am,2),'| PM plan',plan_pm,'board',round(b_pm,2),'| mean',round(base['mean'],3),'->',round(no_pm['mean'],3),'p90',round(base['p90'],2),'->',round(no_pm['p90'],2),'left',round(base['left'],2),'->',round(no_pm['left'],2))
json.dump(OUT,open('cvrp_board.json','w'),ensure_ascii=False)
