import sys;sys.path.insert(0,'/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/th')
from wsim import *
import collections,math
B=json.load(open(SP+'th/base.json'));P=json.load(open(SP+'th/page.json'))
V=P['variants'];RES={}
def ceil_ok(x): return abs(x-round(x))<1e-9
# ---------- demand (ceil basis) ----------
on=B['round_on']['days']
dem={}
for d in DAYS:
    cells=on[d]['cells'];hg=collections.Counter();hr=collections.Counter();sg=collections.Counter();sr=collections.Counter()
    for h,v in cells.items():
        for sid,x in v.items():
            hg[int(h)]+=x['g'];hr[int(h)]+=x['r'];sg[int(sid)]+=x['g'];sr[int(sid)]+=x['r']
    dem[d]={'total':sum(hg.values())+sum(hr.values()),'going':sum(hg.values()),'ret':sum(hr.values()),
            'hour_g':dict(hg),'hour_r':dict(hr),'stop_g':dict(sg),'stop_r':dict(sr),'web_total':on[d]['total']}
    assert abs(dem[d]['total']-on[d]['total'])<1e-6,(d,dem[d]['total'],on[d]['total'])
off=B['round_off']['days']
RES['unrounded_day_total']={d:off[d]['total'] for d in DAYS}
RES['unrounded_week']=sum(off[d]['total'] for d in DAYS)
RES['demand']=dem
week_h=collections.Counter();week_s=collections.Counter();week_g=collections.Counter();week_r=collections.Counter()
for d in DAYS:
    for h in set(dem[d]['hour_g'])|set(dem[d]['hour_r']): week_h[h]+=dem[d]['hour_g'].get(h,0)+dem[d]['hour_r'].get(h,0)
    for s in set(dem[d]['stop_g'])|set(dem[d]['stop_r']):
        week_s[s]+=dem[d]['stop_g'].get(s,0)+dem[d]['stop_r'].get(s,0);week_g[s]+=dem[d]['stop_g'].get(s,0);week_r[s]+=dem[d]['stop_r'].get(s,0)
RES['week']={'total':sum(dem[d]['total'] for d in DAYS),'hour':dict(week_h),'stop':dict(week_s),'stop_g':dict(week_g),'stop_r':dict(week_r)}
# unrounded hourly (for comparison) by hour, week
uh=collections.Counter()
for d in DAYS:
    for h,v in off[d]['cells'].items():
        for sid,x in v.items(): uh[int(h)]+=x['raw']['goingC']+x['raw']['ret']
RES['week_unrounded_hour']=dict(uh)
# ---------- timetables ----------
tt={}
for d in DAYS:
    rows=on[d]['rows'];c=collections.Counter(r['type'] for r in rows)
    byh=collections.Counter(int(r['t'].split(':')[0]) for r in rows)
    tt[d]={'n':len(rows),'types':dict(c),'by_hour':dict(byh),'max_inservice':max(f['inS'] for f in on[d]['fleet']),'fleet_ok':all(f['ok'] for f in on[d]['fleet'])}
RES['tt']=tt;RES['tt_tue_rows']=on['อังคาร']['rows'];RES['fleet_tue']=on['อังคาร']['fleet']
old_by=collections.Counter(t//60 for t in R.RED+R.yellow())
RES['old_by_hour']=dict(old_by);RES['old_n']=len(R.RED)+len(R.yellow())
# ---------- wait: five days ----------
def run(veh,Dd,hi=31,lo=30):
    per=evaluate(veh,Dd,hi,lo);return per
def pack(per):
    o={'all':stats(per,('ret','go')),'ret':stats(per,('ret',)),'go':stats(per,('go',))}
    for k in (('go',8),('ret',12),('go',13),('ret',17)):
        o['%s%02d'%k]=stats(per,keys=[k])
    o['hours']={'%s%02d'%k:stats(per,keys=[k]) for k in per if per[k][0]>=1}
    return o
W5={}
for d in DAYS:
    Dd=build_D(on[d]['cells'])
    new=[veh_row(r) for r in on[d]['rows']]
    W5[d]={'old':pack(run(old35(),Dd)),'new':pack(run(new,Dd)),'n_new':len(new)}
RES['wait5']=W5
Dt=build_D(on['อังคาร']['cells']);newt=[veh_row(r) for r in on['อังคาร']['rows']];oldt=old35()
# ---------- sensitivity: windows ----------
RES['win']={}
for hi,lo in ((31,30),(45,30),(40,30),(30,15)):
    RES['win'][f'{hi}-{lo}']={'old':stats(run(oldt,Dt,hi,lo),('ret','go')),'new':stats(run(newt,Dt,hi,lo),('ret','go'))}
# ---------- speed/dwell ----------
RES['speed']={}
for v_kmh,dw in ((40,20),(30,20),(50,20),(40,40),(40,0),(30,40),(50,0)):
    F.V=v_kmh*1000/60.0;F.DW=dw/60.0;F.LOFF={l:F.loop_off(l) for l in LINES}
    o=old35();n=[veh_row(r) for r in on['อังคาร']['rows']]
    RES['speed'][f'{v_kmh}/{dw}']={'old':stats(run(o,Dt),('ret','go')),'new':stats(run(n,Dt),('ret','go'))}
F.V=40000/60.0;F.DW=20/60.0;F.LOFF={l:F.loop_off(l) for l in LINES}
# ---------- direction reversed ----------
LREV={l:F.loop_off(l,True) for l in LINES}
def rev_new():
    out=[]
    for r in on['อังคาร']['rows']:
        v=veh_row(r)
        if r['type'] in('loop-r','loop-y'): v['stops']=dict(LREV['แดง' if r['type']=='loop-r' else 'เหลือง'])
        out.append(v)
    return out
def rev_old():
    vs=[]
    for t in R.RED: v=F.veh_loop(t,'แดง',35);v['stops']=dict(LREV['แดง']);vs.append(v)
    for t in R.yellow(): v=F.veh_loop(t,'เหลือง',35);v['stops']=dict(LREV['เหลือง']);vs.append(v)
    return vs
RES['reversed']={'old':stats(run(rev_old(),Dt),('ret','go')),'new':stats(run(rev_new(),Dt),('ret','go'))}
# ---------- typo in university timetable ----------
base_y=R.yellow()
RES['typo']={'twice':stats(run(old35(Y=sorted([t for t in base_y if t!=495]+[485])),Dt),('ret','go')),
             'once':stats(run(old35(Y=[t for t in base_y if t!=495]),Dt),('ret','go')),'asread':stats(run(oldt,Dt),('ret','go'))}
# ---------- structural variants / upper bound / mismatch design ----------
RES['struct']={}
for k in ('base','upper','rounds4','rounds1','cvrp_off','min1','min3','lf100','lf70','lead0','lead15'):
    rows=V[k]['rows'];veh=[veh_row(r) for r in rows]
    RES['struct'][k]={'n':len(rows),'types':dict(collections.Counter(r['type'] for r in rows)),'wait':stats(run(veh,Dt),('ret','go')),
                      'seats':sum(r['cap'] for r in rows)}
Dup=Dt
RES['upper_old']={'cap40':stats(run(old35(cap=40),Dt),('ret','go')),'seats35':156*35,'seats40':156*40}
# ---------- population sensitivity ----------
RES['pop']={}
for k,pc in (('pct30',30),('pct50',50),('pct70',70),('pct80',80),('base',100)):
    cells=V[k]['cells'];Dd=build_D(cells)
    veh=[veh_row(r) for r in V[k]['rows']]
    tot=sum(sum(g.values())+sum(r.values()) for g,r in Dd.values())
    RES['pop'][pc]={'pop':round(1122*pc/100),'total':tot,'n':len(veh),'old':stats(run(old35(),Dd),('ret','go')),'new':stats(run(veh,Dd),('ret','go')),
                    'types':dict(collections.Counter(r['type'] for r in V[k]['rows']))}
# ---------- stop offsets ----------
RES['loff']={l:{str(s):round(o,1) for s,o in F.LOFF[l].items()} for l in LINES}
# ---------- red/yellow exclusivity ----------
RED_ONLY={15,23,24};YEL_ONLY={6,7,18,19}
tot=RES['week']['total']
rs=sum(week_s[s] for s in RED_ONLY);ys=sum(week_s[s] for s in YEL_ONLY);both=tot-rs-ys
RES['split']={'red_only':rs,'yellow_only':ys,'both':both,'total':tot}
# ---------- seats / utilisation (Tuesday) ----------
hr_dem={h:dem['อังคาร']['hour_g'].get(h,0)+dem['อังคาร']['hour_r'].get(h,0) for h in range(6,23)}
RES['tue_hour_dem']=hr_dem
RES['seats']={'old_all':156*35,'new_all':sum(r['cap'] for r in on['อังคาร']['rows'])}
json.dump(RES,open(SP+'th/results.json','w'),ensure_ascii=False,default=lambda o:float(o) if hasattr(o,'item') else str(o))
print('week total',RES['week']['total'],'unrounded',round(RES['unrounded_week'],1))
for d in DAYS: print(d,'dem',dem[d]['total'],'g/r',dem[d]['going'],dem[d]['ret'],'trips',tt[d]['n'],tt[d]['types'],'old',round(W5[d]['old']['all']['mean'],2),round(W5[d]['old']['all']['p90'],1),'new',round(W5[d]['new']['all']['mean'],2),round(W5[d]['new']['all']['p90'],1),'left',W5[d]['old']['all']['left'],W5[d]['new']['all']['left'])
print('win',{k:(round(v['old']['mean'],1),round(v['new']['mean'],1)) for k,v in RES['win'].items()})
print('speed',{k:(round(v['old']['mean'],1),round(v['new']['mean'],1)) for k,v in RES['speed'].items()})
print('rev',RES['reversed']['old']['mean'],RES['reversed']['new']['mean'])
print('typo',{k:round(v['mean'],2) for k,v in RES['typo'].items()})
for k,v in RES['struct'].items(): print(k,v['n'],round(v['wait']['mean'],1),round(v['wait']['p90'],1),v['types'])
print('upper old cap40',RES['upper_old']['cap40']['mean'],RES['upper_old']['cap40']['p90'])
for k,v in RES['pop'].items(): print('pop',k,v['pop'],v['total'],v['n'],round(v['old']['mean'],1),round(v['new']['mean'],1))
print('split',RES['split'])
