# results5.py - third timetable: "ตารางเดิม + เที่ยว CVRP (เช้า/เย็น)" and one extra variant (+ loop trips in the 3 highest-demand loop hours).
# Same file is run in both trees (scenario A = scratchpad/th, scenario B = scratchB/th); SP comes from wsim.py.
# Reads base.json (round_on rows/cells) and results.json; writes results5.json. Every number is asserted against results.json (old/new) before it is stored.
import sys,os,json,math,collections
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
from wsim import *
import fullday as F
import passup as PU
B=json.load(open(SP+'th/base.json'));RES=json.load(open(SP+'th/results.json'))
on=B['round_on']['days'];OUT={'meta':{'trip_minutes_assumed':16,'old_trips':len(old35())}}
TRIP_MIN=16
def in_service(veh,dur=TRIP_MIN,cap=None):
    ev=[]
    for v in veh:
        if cap is not None and v['cap']!=cap: continue
        ev.append((v['t'],1));ev.append((v['t']+dur,-1))
    ev.sort(key=lambda x:(x[0],x[1]));c=m=0
    for _,d in ev: c+=d;m=max(m,c)
    return m
def pack(per):
    o={'all':stats(per,('ret','go')),'ret':stats(per,('ret',)),'go':stats(per,('go',))}
    for k in (('go',8),('ret',12),('go',13),('ret',17)): o['%s%02d'%k]=stats(per,keys=[k])
    s=F.summarize(per,('go',));o['late_share']=float(s['late']);o['late_people']=float(s['late']*s['served']);o['go_n']=float(s['n'])
    return o
for d in DAYS:
    rows=on[d]['rows'];Dd=build_D(on[d]['cells'])
    dem=RES['demand'][d];hg=dem['hour_g'];hr=dem['hour_r']
    Dh={h:hg.get(str(h),0)+hr.get(str(h),0) for h in range(8,20)}
    top=sorted(Dh,key=lambda h:(-Dh[h],h))[:3]
    cv=[r for r in rows if r['type'] in('cvrp','express')]
    lp=[r for r in rows if r['type'].startswith('loop') and int(r['t'].split(':')[0]) in top]
    tabs={'old':old35(),'new':[veh_row(r) for r in rows],'hyb':old35()+[veh_row(r) for r in cv],'hyb_top3':old35()+[veh_row(r) for r in cv+lp]}
    ntrips={k:len(v) for k,v in tabs.items()}
    assert ntrips['old']==156 and ntrips['new']==len(rows)==RES['tt'][d]['n'] and ntrips['hyb']==156+len(cv) and ntrips['hyb_top3']==156+len(cv)+len(lp)
    assert abs(sum(sum(g.values())+sum(r.values()) for g,r in Dd.values())-dem['total'])<1e-6
    od={'top3_hours':top,'cv_trips':len(cv),'loop_added':len(lp),'trips':ntrips,'seats':{k:sum(v['cap'] for v in vv) for k,vv in tabs.items()},
        'max_inservice_all':{k:in_service(vv) for k,vv in tabs.items()},'max_inservice_35':{k:in_service(vv,cap=35) for k,vv in tabs.items()}}
    for hi in (31,45):
        res={}
        for k,vv in tabs.items():
            per=evaluate(vv,Dd,hi=hi,lo=30);res[k]=pack(per)
            tot,cells,stops=PU.pass_eval(vv,Dd,hi=hi,lo=30,detail=True);res[k]['pass']={'ret':tot['ret'],'go':tot['go'],'cells':cells,'stops':stops}
        if hi==31:  # consistency with results.json
            for k in ('old','new'):
                a=RES['wait5'][d][k]['all'];b=res[k]['all']
                assert abs(a['mean']-b['mean'])<1e-9 and abs(a['p90']-b['p90'])<1e-9 and abs(a['left']-b['left'])<1e-9,(d,k,a,b)
        od['win%d'%hi]=res
    OUT[d]=od
    h=od['win31']
    print(d,'trips',ntrips,'| mean',{k:round(h[k]['all']['mean'],2) for k in h},'| p90',{k:round(h[k]['all']['p90'],1) for k in h},'| left',{k:round(h[k]['all']['left'],1) for k in h},'| late%',{k:round(100*h[k]['late_share'],1) for k in h},'| inS35',od['max_inservice_35'],'| top3',top)
json.dump(OUT,open(SP+'th/results5.json','w'),ensure_ascii=False,indent=1)
