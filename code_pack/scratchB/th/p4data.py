# Data layer for chapter-3 part 4 (all numbers derived from base.json / results.json / results_extra.json / scripts)
import json,math,collections,sys,re,io,contextlib
sys.path.insert(0,'.')
SP='/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/th/'
R=json.load(open(SP+'results.json'));X=json.load(open(SP+'results_extra.json'));B=json.load(open(SP+'base.json'))
DAYS=['จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์']
on=B['round_on']['days']
from tdat import md_table
def f1(x): return f"{x:,.1f}"
def i0(x): return f"{int(round(x)):,}"
T='อังคาร'
# ---------- Tuesday loop-rule table ----------
dem=R['demand'][T];hg=dem['hour_g'];hr=dem['hour_r']
rows=on[T]['rows'];fl={f['h']:f for f in on[T]['fleet']}
def Dh(h): return hg.get(str(h),0)+hr.get(str(h),0)
am=[x for x in rows if x['type'] in('cvrp','express') and x['label'].startswith('P0 →')]
pm=[x for x in rows if x['type'] in('cvrp','express') and x['label'].startswith('P0 ←')]
AM_LOAD=sum(x['load'] for x in am);PM_LOAD=sum(x['load'] for x in pm)
assert abs(AM_LOAD-hg['7'])<1e-9 and abs(PM_LOAD-hr['16'])<1e-9,(AM_LOAD,hg['7'],PM_LOAD,hr['16'])
C=35*2*0.85
loop_trips=collections.Counter(int(x['t'].split(':')[0]) for x in rows if x['type'].startswith('loop'))
tab14=[];sumD=0;sumL=0;sumT=0;floor_h=[];eq_h=[];over_h=[]
for h in range(7,20):
    D=Dh(h);cv=AM_LOAD if h==7 else (PM_LOAD if h==16 else 0)
    if h==7:
        tab14.append([f"{h:02d}:00",i0(D),i0(cv),'—','—','—','—']);sumD+=D;continue
    DL=D-cv;need=math.ceil(DL/C-1e-9);n=fl[h]['loop'];t=loop_trips[h]
    assert n==min(21,max(2,need)) and t==2*n,(h,n,need,t)
    (floor_h if need<2 else eq_h if need==2 else over_h).append(h)
    tab14.append([f"{h:02d}:00",i0(D),i0(cv),i0(DL),str(need),str(n),str(t)]);sumD+=D;sumL+=DL;sumT+=t
assert abs(sumD-dem['total'])<1e-9,(sumD,dem['total'])
tab14.append(['รวม',i0(sumD),i0(AM_LOAD+PM_LOAD),i0(sumL),'','—',str(sumT)])
TAB14=md_table(['ชั่วโมงที่นับ','ความต้องการรวม D (เที่ยวคน)','รับโดย CVRP','ส่วนที่ใช้กฎรถวน','⌈D ÷ 59.5⌉','n(h) (คัน)','เที่ยวรถวน'],tab14)
LOOP_TRIPS_TUE=sumT;FLOOR_TRIPS=2*2*len(range(8,20));EXTRA_TRIPS=LOOP_TRIPS_TUE-FLOOR_TRIPS
assert LOOP_TRIPS_TUE+len(am)+len(pm)==len(rows)==R['tt'][T]['n']
# ---------- CVRP table (Tuesday) ----------
import os;os.chdir(SP+'..');sys.path.insert(0,SP+'..');import fullday as F;os.chdir(SP)
def travel(label):
    st=[int(s) for s in re.findall(r'P(\d+)',label) if int(s)!=0]
    return st if '→' in label else st[::-1]
sg={'blue':'น้ำเงิน','red':'แดง','yellow':'เหลือง'}
tab15=[]
for k,x in enumerate(am+pm,1):
    st=travel(x['label']);off=F.seq_off(st)
    tab15.append([str(k),x['t']+' น.','ขาไป (รอบเช้า)' if x['label'].startswith('P0 →') else 'ขากลับ (รอบบ่าย)',' → '.join('P'+str(s) for s in st),str(int(x['load'])),str(x['cap']),f"{off[st[-1]]:.1f}",sg[x['sign']]])
TAB15=md_table(['เที่ยว','เวลาออกจาก P0','ทิศทาง','ลำดับจุดจอดตามการเดินทาง','โหลด (คน)','ที่นั่งของรถ','เวลาถึงจุดสุดท้ายหลังออก (นาที)','ป้ายสี'],tab15)
# ---------- sign rule counts + per-day table ----------
tab17=[];W=collections.Counter()
for d in DAYS:
    rr=on[d]['rows'];c=collections.Counter(x['type'] for x in rr)
    loop=c['loop-r']+c['loop-y'];cv=c['cvrp']+c['express'];blue=sum(1 for x in rr if x.get('sign')=='blue')
    seats=sum(x['cap'] for x in rr);mx=max(f['inS'] for f in on[d]['fleet']);ok=all(f['ok'] for f in on[d]['fleet'])
    assert len(rr)==loop+cv==R['tt'][d]['n'] and seats==(R['seats']['new_all'] if d==T else seats)
    tab17.append([d,str(len(rr)),str(loop),str(cv),str(blue),f"{seats:,}",str(mx),'ผ่าน' if ok else 'ไม่ผ่าน']);W.update(trips=len(rr),loop=loop,cv=cv,blue=blue,seats=seats)
tab17.append(['รวม 5 วัน',str(W['trips']),str(W['loop']),str(W['cv']),str(W['blue']),f"{W['seats']:,}",'—','—'])
TAB17=md_table(['วัน','เที่ยวรถรวม','เที่ยวรถวน','เที่ยว CVRP และเที่ยวด่วน','ป้ายน้ำเงิน','ที่นั่งที่เสนอ','รถใช้งานพร้อมกันสูงสุด (คัน)','การตรวจฝูงรถ 21 คัน'],tab17)
CARTS=sum(1 for d in DAYS for x in on[d]['rows'] if x['cap']==11)
# ---------- unit tests ----------
U=json.load(open(SP+'unit_tests.json'))
def u(k): return U[k]
tab19=[
 ['T1','ขากลับ: 100 คนมาถึงสม่ำเสมอใน 15 นาที รถคันเดียว (ที่นั่งไม่จำกัด) ถึงจุดจอดเมื่อสิ้นสุดช่วงมาถึง','7.50 นาที','7.50 นาที ไม่เหลือผู้โดยสาร'],
 ['T2','เหมือน T1 แต่คันแรกมี 50 ที่นั่ง คันที่สองถึงจุดจอดหลังคันแรก 5 นาที','10.00 นาที (50 คนแรกรอเฉลี่ย 11.25 และ 50 คนหลังรอเฉลี่ย 8.75)',f"{u('T2')[0]:.2f} นาที ไม่เหลือผู้โดยสาร"],
 ['T2b','เหมือน T2 แต่มีเฉพาะคันแรก','11.25 นาที และเหลือ 50 คน',f"{u('T2b')[0]:.2f} นาที เหลือ {u('T2b')[2]:.0f} คน"],
 ['T3','ขาไป: 40 คนมาถึง P0 ใน 1 นาที (ก้าว 0.25 นาที) รถ 35 ที่นั่งออกจาก P0 หลังสิ้นสุดช่วงมาถึง 5 นาที รถคันที่สองออกหลังคันแรก 15 นาที','7.375 นาที (คำนวณมือจากเวลามาถึงทั้ง 4 ก้าว)',f"{u('T3')[0]:.3f} นาที ไม่เหลือผู้โดยสาร"],
 ['T4','ขาไป: รถไม่จอดที่จุดปลายทางของผู้โดยสาร','ไม่มีผู้ขึ้นรถ เหลือ 40 คน',f"ไม่มีผู้ขึ้นรถ เหลือ {u('T4')[2]:.0f} คน"],
 ['T5','ขาไป: รถถึงจุดปลายทางหลังเวลาเริ่มคาบ','รอเฉลี่ย 27.5 นาที และถูกนับว่าไม่ทันคาบ',f"{u('T5')[0]:.1f} นาที ตัวบ่งชี้ไม่ทันคาบ = {u('T5')[3]}"],
 ['T6','ขากลับ: รถ 35 ที่นั่งจอด 2 จุด จุดแรกมี 30 คน จุดที่สองมี 10 คน','ขึ้นรถ 35 คน (30 และ 5) เหลือ 5 คน ที่นั่งใช้ร่วมกันตามเส้นทาง',f"ขึ้นรถ {u('T6')[1]:.0f} คน เหลือ {u('T6')[2]:.0f} คน"]]
assert abs(u('T1')[0]-7.5)<1e-6
TAB19=md_table(['รหัส','สถานการณ์ทดสอบ','ค่าที่คำนวณด้วยมือ','ผลจากแบบจำลอง'],tab19)
if __name__=='__main__':
    print(TAB14);print(TAB15);print(TAB17);print('floor',floor_h,'eq',eq_h,'over',over_h,'loop trips',LOOP_TRIPS_TUE,'floor trips',FLOOR_TRIPS,'extra',EXTRA_TRIPS,'carts',CARTS)
    print(TAB19)

# ---------- who actually boards the PM CVRP trip in the fluid wait model (Tuesday, hour-16 returns) ----------
from wsim import build_D,veh_row
def board_mass(veh,dem,w0,w1,step=0.5):
    q={s:[] for s in dem};n=int(round((w1-w0)/step))
    for s,m in dem.items():
        for i in range(n):q[s].append([w0+(i+.5)*step,m/n])
    ev=sorted((v['t']+o,vi,s) for vi,v in enumerate(veh) for s,o in v['stops'].items() if s in dem)
    onb={};ptr={s:0 for s in dem}
    for t,vi,s in ev:
        free=veh[vi]['cap']-onb.get(vi,0)
        while free>1e-9 and ptr[s]<len(q[s]) and q[s][ptr[s]][0]<=t:
            a,m=q[s][ptr[s]];take=min(m,free);free-=take;onb[vi]=onb.get(vi,0)+take
            if take<m-1e-12:q[s][ptr[s]][1]=m-take
            else:ptr[s]+=1
    return onb
_D=build_D(on[T]['cells']);_veh=[veh_row(r) for r in rows]
_pm_idx=[i for i,r in enumerate(rows) if r['type'] in('cvrp','express') and r['label'].startswith('P0 ←')]
assert len(_pm_idx)>=1
_onb=board_mass(_veh,_D[16][1],16*60,16*60+15)
PM_BOARD=sum(_onb.get(i,0.0) for i in _pm_idx);PM_PLAN=sum(x['load'] for x in pm)
if __name__=='__main__': print('PM CVRP planned',PM_PLAN,'boards in model',round(PM_BOARD,2),'of',sum(_D[16][1].values()))
