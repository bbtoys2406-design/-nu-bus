import re,json,sys,math
sys.path.insert(0,'.')
from p4data import *          # R,X,B,DAYS,on,T,md_table,... (SP = .../th/)
from wsim import veh_row, old35
CB=json.load(open(SP+'cvrp_board.json'))
MC=json.load(open(SP+'../mc_check.json'))
UT=json.load(open(SP+'unit_tests.json'))
GR=json.load(open(SP+'geo_res.json'))
PG=json.load(open(SP+'page.json'))
XC=open(SP+'xc_out.txt',encoding='utf-8').read()
GO=open(SP+'geo_out.txt',encoding='utf-8').read()
def fill(tpl,subs):
    s=open(SP+'md/'+tpl,encoding='utf-8').read()
    for k,v in subs.items(): s=s.replace('{{'+k+'}}',str(v))
    assert '{{' not in s,re.findall(r'\{\{[A-Z0-9_]+\}\}',s)
    return s
def num(pat,txt,cast=float):
    m=re.search(pat,txt); assert m,pat
    return cast(m.group(1).replace(',',''))
# ---------- xc.py output ----------
RECS=num(r'records (\d+)',XC,int);SEGS=num(r'segments (\d+)',XC,int)
WKSEGS=num(r'weekday segs (\d+)',XC,int)
m=re.search(r'matched weekday (\d+) of (\d+) ([\d.]+) \| seats (\d+) of (\d+) ([\d.]+)',XC);assert m
MATCHED,WKT,MATCH_PCT,SEAT_M,SEAT_T,SEAT_PCT=int(m[1]),int(m[2]),float(m[3]),int(m[4]),int(m[5]),float(m[6])
assert WKT==WKSEGS==5225 and RECS==4260 and SEGS==5263 and MATCHED==4634
RAW_TOT=num(r'RAW ([\d.]+)',XC,float);K=num(r' k ([\d.e-]+)',XC)
CH_G=num(r'chained going excluded (\d+)',XC,int);CH_R=num(r'chained return excluded (\d+)',XC,int)
m=re.search(r'python ceil total (\d+) unrounded ([\d.]+) cell mismatches (\d+)',XC);assert m
WEEK_RND,WEEK_UNR,MISMATCH=int(m[1]),float(m[2]),int(m[3])
N_CELLS=num(r'nonzero raw cells (\d+)',XC,int)
assert MISMATCH==0 and N_CELLS==751 and WEEK_RND==3202 and WEEK_UNR==2805.0
assert abs(RAW_TOT-305158)<1e-6 and abs(K-561*5/RAW_TOT)<1e-12
assert (CH_G,CH_R)==(1391,1385)
assert int(R['week']['total'])==WEEK_RND and abs(R['unrounded_week']-WEEK_UNR)<1e-6
assert abs(sum(len(v['cells']) for v in [])+0)==0  # placeholder no-op
# ---------- geo ----------
GEO_NAMES=num(r'names in geojson (\d+) rows (\d+)',GO,int);GEO_SHAPES=int(re.search(r'rows (\d+)',GO)[1])
GEO_CMP=num(r'matched names compared (\d+)',GO,int)
m=re.search(r'median (\d+) min (\d+) max (\d+)',GO);GEO_MED,GEO_MIN,GEO_MAX=int(m[1]),int(m[2]),int(m[3])
GEO_CLOSE=num(r'second within 20 m: (\d+)',GO,int)
b2s=PG['b2s'];skip=('หอใน','จุดเริิ่มเส้นทาง')
diff=[n for n,s in b2s.items() if n in GR and n not in skip and GR[n]['near']!=s]
GEO_MATCH=GEO_CMP-len(diff)
assert diff==['สนามฟุตบอล'] and GEO_CMP==38 and GEO_MATCH==37 and GEO_NAMES==40 and GEO_SHAPES==54 and GEO_CLOSE==11
fb=GR['สนามฟุตบอล'];assert b2s['สนามฟุตบอล']==22 and fb['near']==20 and fb['second']==22
FB_D1,FB_D2=round(fb['d1']),round(fb['d2']);FB_DIFF=round(fb['d2']-fb['d1'])
assert (FB_D1,FB_D2)==(127,129)
# unmatched seats share
UNM=1-SEAT_M/SEAT_T;UNM_PCT=f"{UNM*100:.1f}%"
assert UNM_PCT=='11.6%'
# ---------- unit tests ----------
N_UT=len(UT);assert N_UT==7
# ---------- fleet ----------
maxin=max(f['inS'] for d in DAYS for f in on[d]['fleet']);assert maxin==5
# ---------- MC table ----------
rows=[];dmean=0;dp90=0;inside=0;ncomp=0;eq_left=0
late_f=0;late_m=0;go_n=0
for d in DAYS:
    w=R['wait5'][d];lt=X['late'][d]
    for key,lab in (('old','เดิม'),('new','เสนอ')):
        fa=w[key]['all'];mc=MC[d][key];assert mc['reps']==200
        dmean=max(dmean,abs(fa['mean']-mc['mean']));dp90=max(dp90,abs(fa['p90']-mc['p90']))
        ncomp+=1;inside+=int(mc['mean_lo']<=fa['mean']<=mc['mean_hi'])
        assert abs(fa['left']-mc['left'])<1e-9 and abs(mc['left']-round(mc['left']))<1e-9;eq_left+=1
        assert abs(lt[key]['go_n']-mc['go_n'])<1e-9
        lf=lt[key]['late_people'];lm=mc['late_mean'];gn=lt[key]['go_n']
        if key=='new': late_f+=lf;late_m+=lm;go_n+=gn
        else: assert lf==0 and lm==0
        rows.append([d,lab,f"{fa['mean']:.2f}",f"{mc['mean']:.2f} ({mc['mean_lo']:.2f}–{mc['mean_hi']:.2f})",f"{fa['p90']:.2f}",f"{mc['p90']:.2f}",
                     f"{int(round(fa['left']))} / {int(round(mc['left']))}",f"{lf/gn*100:.1f} / {lm/gn*100:.1f}"])
assert ncomp==10 and eq_left==10
MC_ROWS='\n'.join('| '+' | '.join(r)+' |' for r in rows)
assert go_n==1598==int(R['week']['total']-R['demand']['จันทร์']['total']*0)-1604 or go_n==1598
LATE_FP=f"{late_f/go_n*100:.1f}";LATE_MP=f"{late_m/go_n*100:.1f}"
assert (LATE_FP,LATE_MP)==('1.0','1.4'),(LATE_FP,LATE_MP)
assert inside==10
# ---------- CVRP board ----------
am_b=sum(CB[d]['board_am'] for d in DAYS);am_p=sum(CB[d]['plan_am'] for d in DAYS)
pm_b=sum(CB[d]['board_pm'] for d in DAYS);pm_p=sum(CB[d]['plan_pm'] for d in DAYS)
assert abs(am_b-am_p)<1e-6 and am_p==int(R['week']['hour']['7'])==424 and pm_p==167 and round(pm_b)==6
dm=max(CB[d]['no_pm']['mean']-CB[d]['base']['mean'] for d in DAYS);dm2=math.ceil(dm*100-1e-9)/100;assert 0<dm<=dm2<=0.04
assert all(abs(CB[d]['no_pm']['p90']-CB[d]['base']['p90'])<0.01 and abs(CB[d]['no_pm']['left']-CB[d]['base']['left'])<1e-6 for d in DAYS)
# PM CVRP pass times
tmin=1e9;tmax=-1e9
for d in DAYS:
    for r in on[d]['rows']:
        if r['type'] in('cvrp','express') and r['label'].startswith('P0 ←'):
            v=veh_row(r)
            for s,o in v['stops'].items():
                t=v['t']+o;tmin=min(tmin,t);tmax=max(tmax,t)
hm=lambda t:f"{int(t//60):02d}:{int(t%60):02d}"
PM_T0,PM_T1=hm(round(tmin)),hm(round(tmax))
print('PM CVRP pass times',tmin,tmax,PM_T0,PM_T1)
# ---------- constants ----------
SEATS_ALL=35*16+11*5;assert SEATS_ALL==615
V=40;assert abs(V*1000/60-666.7)<0.05
OLD_N=int(R['old_n']);assert OLD_N==156
import platform
subs=dict(N_DORM='1,696',N_MC='1,135',N_USERS=561,WEEK_UNR=f"{WEEK_UNR:,.0f}",WEEK_RND=f"{WEEK_RND:,}",RAW_TOT=f"{RAW_TOT:,.0f}",K_VAL=f"{K:.7f}".rstrip('0') if False else f"{K:.7f}",
  MAX_IN=maxin,SEATS_ALL=SEATS_ALL,SPEED=V,DWELL=20,OLD_N=OLD_N,SEAT_PCT=f"{SEAT_PCT:.1f}%",GEO_MATCH=GEO_MATCH,GEO_CMP=GEO_CMP,GEO_CLOSE=GEO_CLOSE,
  N_CELLS=N_CELLS,N_UT=N_UT,SEGS=f"{SEGS:,}",WKSEGS=f"{WKSEGS:,}",MATCHED=f"{MATCHED:,}",MISMATCH=MISMATCH,MC_REPS=200,
  RECS=f"{RECS:,}",MATCH_PCT=f"{MATCH_PCT:.1f}%",SEAT_M=f"{SEAT_M:,}",SEAT_T=f"{SEAT_T:,}",CH_G=f"{CH_G:,}",CH_R=f"{CH_R:,}",
  GEO_SHAPES=GEO_SHAPES,GEO_NAMES=GEO_NAMES,FB_D1=FB_D1,FB_D2=FB_D2,FB_DIFF=FB_DIFF,GEO_MED=GEO_MED,GEO_MIN=GEO_MIN,GEO_MAX=GEO_MAX,
  MC_ROWS=MC_ROWS,MC_DMEAN=f"{math.ceil(dmean*10-1e-9)/10:.1f}",MC_DP90=f"{math.ceil(dp90*10-1e-9)/10:.1f}",MC_IN=inside,MC_N=ncomp,
  GO_N=f"{go_n:,.0f}",LATE_FP=LATE_FP,LATE_MP=LATE_MP,
  AM_PLAN=f"{am_p:,.0f}",PM_PLAN=f"{pm_p:,.0f}",PM_BOARD=f"{round(pm_b)}",PM_T0=PM_T0,PM_T1=PM_T1,PM_DMEAN=f"{dm2:.2f}",
  PYV='.'.join(platform.python_version().split('.')[:2]),UNM_PCT=UNM_PCT)
# statements in templates asserted
assert subs['K_VAL']=='0.0091920',subs['K_VAL']
assert subs['MC_DMEAN'] and float(subs['MC_DMEAN'])<=0.1+1e-9,subs['MC_DMEAN']
a=fill('c3_p5a.tpl.md',subs);open(SP+'md/c3_p5a.md','w',encoding='utf-8').write(a)
b=fill('c3_p5b.tpl.md',subs);open(SP+'md/c3_p5b.md','w',encoding='utf-8').write(b)
print('5a bytes',len(a.encode()),'5b bytes',len(b.encode()))
print('dmean',dmean,'dp90',dp90,'late',late_f,late_m,go_n)
