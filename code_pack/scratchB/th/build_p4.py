import re,json,sys
sys.path.insert(0,'.')
from p4data import *
CB=json.load(open(SP+'cvrp_board.json'))
def fill(tpl,subs):
    s=open(SP+'md/'+tpl,encoding='utf-8').read()
    for k,v in subs.items(): s=s.replace('{{'+k+'}}',str(v))
    assert '{{' not in s,re.findall(r'\{\{[A-Z0-9_]+\}\}',s)
    return s
# --- hard-coded statements in the template are asserted here
assert eq_h==[17] and over_h==[12] and len(floor_h)==10
assert fl[12]['loop']==5 and loop_trips[12]==10 and all(loop_trips[h]==4 for h in range(8,20) if h!=12)
assert all(x['cap']==35 for d in DAYS for x in on[d]['rows'] if x['type'].startswith('loop'))
assert int(R['week']['hour']['20'])==5 and min(int(h) for h in R['week']['hour'])==7
assert R['tt'][T]['n']==58 and R['struct']['min1']['n']==38 and R['seats']['old_all']==5460
maxloop=max(f['loop'] for d in DAYS for f in on[d]['fleet']);maxin=max(f['inS'] for d in DAYS for f in on[d]['fleet'])
am_b=sum(CB[d]['board_am'] for d in DAYS);am_p=sum(CB[d]['plan_am'] for d in DAYS)
pm_b=sum(CB[d]['board_pm'] for d in DAYS);pm_p=sum(CB[d]['plan_pm'] for d in DAYS)
assert abs(am_b-am_p)<1e-6 and am_p==int(R['week']['hour']['7'])
dm=max(CB[d]['no_pm']['mean']-CB[d]['base']['mean'] for d in DAYS)
assert all(abs(CB[d]['no_pm']['p90']-CB[d]['base']['p90'])<0.01 and abs(CB[d]['no_pm']['left']-CB[d]['base']['left'])<1e-6 for d in DAYS)
import math;dm2=math.ceil(dm*100-1e-9)/100;assert 0<dm<=dm2<=0.04,dm
seats=[sum(x['cap'] for x in on[d]['rows']) for d in DAYS]
subs=dict(TAB14=TAB14.strip(),TAB15=TAB15.strip(),TAB17=TAB17.strip(),MAXIN=maxin,MAXLOOP=maxloop,H20=int(R['week']['hour']['20']),
 N_FLOOR_H=len(floor_h),LOOP_TRIPS_TUE=LOOP_TRIPS_TUE,FLOOR_TRIPS=FLOOR_TRIPS,EXTRA_TRIPS=EXTRA_TRIPS,TUE_TRIPS=R['tt'][T]['n'],MIN1_TRIPS=R['struct']['min1']['n'],
 AM_BOARD=f"{am_b:,.0f}",AM_PLAN=f"{am_p:,.0f}",PM_BOARD=f"{round(pm_b)}",PM_PLAN=f"{pm_p:,.0f}",
 PM_HI=f"{math.ceil(max(CB[d]['board_pm'] for d in DAYS)-1e-9)}",
 PM_PLAN_LO=f"{min(CB[d]['plan_pm'] for d in DAYS):.0f}",PM_PLAN_HI=f"{max(CB[d]['plan_pm'] for d in DAYS):.0f}",
 NOPM_MAX=f"{dm2:.2f}",CARTS=CARTS,SEATS_LO=f"{min(seats):,}",SEATS_HI=f"{max(seats):,}",OLD_SEATS=f"{R['seats']['old_all']:,}")
a=fill('c3_p4a.tpl.md',subs)
open(SP+'md/c3_p4a.md','w',encoding='utf-8').write(a);print(len(a.encode()))

# ================= Part 4b =================
import os
RPJ=json.load(open(SP+'../route_pos.json'))
SD=json.load(open('/root/.claude/uploads/5d08b61f-0d0d-5ed9-b111-61441aa95e91/bcc2fe4d-stop_line_dist.json'))
from pyproj import Transformer
from shapely.geometry import shape
import shapely
road=json.load(open('/mnt/user-data/uploads/road.geojson'));tr=Transformer.from_crs(4326,32647,always_xy=True)
GL={}
for f in road['features']:
    g=shapely.transform(shape(f['geometry']),lambda a:__import__('numpy').column_stack(tr.transform(a[:,0],a[:,1])))
    GL[f['properties']['name']]=g.length
assert round(GL['แดง'])==5287 and round(GL['เหลือง'])==5716
CL={l:RPJ[l]['length'] for l in RPJ};assert round(CL['แดง'])==5311 and round(CL['เหลือง'])==5739
gaps=[CL[l]-GL[l] for l in CL];assert all(22.5<g<23.5 for g in gaps)
V=40000/60;DW=20/60
def pk(l,s):
    L=CL[l];p0=RPJ[l]['pos']['0'][1]
    st=sorted([x for x in range(1,27) if str(x) in SD and SD[str(x)][l]<=30],key=lambda x:(RPJ[l]['pos'][str(x)][1]-p0)%L)
    k=st.index(s)+1;Lk=(RPJ[l]['pos'][str(s)][1]-p0)%L;t=Lk/V+(k-1)*DW
    assert abs(round(t,1)-R['loff'][l][str(s)])<0.051
    return k,Lk,t
kr,Lr,tr_=pk('แดง',16);ky,Ly,ty=pk('เหลือง',16)
# --- Table 3.21 threshold table
wk=R['week']['stop'];WEEK_T=int(R['week']['total'])
t21=[];shares={}
for thr in (10,20,30,50,75):
    red=[s for s in range(1,27) if str(s) in SD and SD[str(s)]['แดง']<=thr and SD[str(s)]['เหลือง']>thr]
    yel=[s for s in range(1,27) if str(s) in SD and SD[str(s)]['เหลือง']<=thr and SD[str(s)]['แดง']>thr]
    both=[s for s in range(1,27) if str(s) in SD and SD[str(s)]['แดง']<=thr and SD[str(s)]['เหลือง']<=thr]
    none=[s for s in range(1,27) if str(s) in SD and SD[str(s)]['แดง']>thr and SD[str(s)]['เหลือง']>thr]
    assert len(red)+len(yel)+len(both)+len(none)==25 and not none
    d=sum(wk.get(str(s),0) for s in both);shares[thr]=d/WEEK_T*100
    t21.append([f"{thr}"+(' (ฐาน)' if thr==30 else ''),str(len(both)),', '.join('P'+str(s) for s in red) or '—',', '.join('P'+str(s) for s in yel) or '—',f"{int(d):,}",f"{d/WEEK_T*100:.1f}%"])
    if thr==30: assert (len(both),red,yel)==(18,[15,23,24],[6,7,18,19]) and int(d)==int(R['split']['both'])
TAB21=md_table(['เกณฑ์ระยะห่าง (เมตร)','จุดใกล้ทั้งสองสาย (จุด)','จุดใกล้สายสีแดงอย่างเดียว','จุดใกล้สายสีเหลืองอย่างเดียว','เที่ยวคนที่จุดร่วม (สัปดาห์)','สัดส่วนของ 3,202'],t21)
assert WEEK_T==3202
# --- Table 3.20 design table
P=R['pop'];pops=[f"{P[k]['pop']}" for k in ('30','50','70','80')]
assert pops==['168','280','393','449'] and set(R['win'])=={'31-30','45-30','40-30','30-15'}
assert set(R['speed'])=={'40/20','30/20','50/20','40/40','40/0','30/40','50/0'} and set(R['typo'])=={'twice','once','asread'}
for k in ('upper','rounds4','rounds1','cvrp_off','min1','min3','lf100','lf70','lead0','lead15'): assert k in R['struct']
assert 'round_off_tue' in X and 'chain_sens' in X
t20=[
 ['ความต้องการ','คาบต่อเนื่องห้องเดียวกัน (หัวข้อ 3.6.5)','ตัดขากลับของคาบแรกและขาไปของคาบหลัง','ไม่ตัด','การกระจายความต้องการตามชั่วโมงและจุดจอด (ไม่รันเวลารอ)','5 วัน'],
 ['ความต้องการ','การปัดเศษขึ้น (หัวข้อ 3.6.6)','ปัดขึ้นรายเซลล์','ไม่ปัด (ใช้ทศนิยม)','ความต้องการ ตารางที่เสนอ และเวลารอของทั้งสองตาราง','5 วัน (ความต้องการ) อังคาร (เวลารอ)'],
 ['ความต้องการ','ขนาดกลุ่มผู้ใช้','561 คน','ร้อยละ 30, 50, 70 และ 80 ของ 561 คน ('+', '.join(pops)+' คน)','ตารางที่เสนอสร้างใหม่ และเวลารอของทั้งสองตาราง','อังคาร ไม่ทดสอบกรณีมากกว่า 561 คน'],
 ['กฎเที่ยวรถ','จำนวนรอบต่อคันต่อชั่วโมง r','2','1 และ 4','ตารางที่เสนอสร้างใหม่ และเวลารอ','อังคาร'],
 ['กฎเที่ยวรถ','สัดส่วนการใช้ที่นั่งเป้าหมาย LF','0.85','0.70 และ 1.00','เช่นเดียวกัน','อังคาร'],
 ['กฎเที่ยวรถ','จำนวนรถขั้นต่ำต่อชั่วโมง n_min','2','1 และ 3','เช่นเดียวกัน','อังคาร'],
 ['กฎเที่ยวรถ','การใช้ CVRP','ใช้ในรอบเช้าและรอบบ่าย','ไม่ใช้ (ทุกชั่วโมง 07:00–19:59 น. ใช้รถวน)','เช่นเดียวกัน','อังคาร'],
 ['กฎเที่ยวรถ','ที่นั่งต่อคัน','35 (รถส้ม) และ 11 (รถกอล์ฟ)','40 และ 14','ตารางที่เสนอสร้างใหม่ ตารางปัจจุบันคิดเป็นรถ 40 ที่นั่ง และเวลารอ','อังคาร'],
 ['กฎเที่ยวรถ','เวลามาถึง P0 ก่อนคาบที่ใช้ออกแบบตาราง','30 นาที','15 และ 0 นาที (สร้างตารางตามสมมติฐานนั้น แล้วประเมินกับผู้โดยสารที่มาถึง 30 นาทีก่อนคาบ)','ตารางที่เสนอสร้างใหม่ และเวลารอ','อังคาร'],
 ['แบบจำลองเวลารอ','ช่วงมาถึง P0 ของขาไป (นาทีก่อนต้นชั่วโมงของคาบ)','31–30','45–30, 40–30 และ 30–15','เวลารอของทั้งสองตาราง','อังคาร'],
 ['แบบจำลองเวลารอ','ความเร็วและเวลาจอด','40 กม./ชม. และ 20 วินาที','30/20, 50/20, 40/40, 40/0, 30/40 และ 50/0 (กม./ชม. / วินาที)','เวลารอของทั้งสองตาราง','อังคาร'],
 ['แบบจำลองเวลารอ','ทิศทางการวนของรถ','ทิศของวงปิดที่ต่อจากไฟล์เส้นทาง','ทิศกลับ','เวลารอของทั้งสองตาราง','อังคาร'],
 ['การอ่านตารางปัจจุบัน','เวลาออกสายสีเหลืองที่พิมพ์ 08:05 ซ้ำ','อ่านเป็น 08:15','08:05 สองครั้ง และ 08:05 ครั้งเดียว','เวลารอของตารางปัจจุบัน','อังคาร'],
 ['การออกแบบตาราง','เที่ยว CVRP รอบบ่าย (หัวข้อ 3.6.8)','มี','ตัดออก','เวลารอของตารางที่เสนอ','5 วัน']]
TAB20=md_table(['กลุ่ม','ตัวแปร','ค่าฐาน','ค่าที่ทดสอบ','ส่วนที่คำนวณซ้ำ','ขอบเขต'],t20)
tpls=dict(RED_CLOSED=f"{CL['แดง']:,.0f}",YEL_CLOSED=f"{CL['เหลือง']:,.0f}",RED_GEOM=f"{GL['แดง']:,.0f}",YEL_GEOM=f"{GL['เหลือง']:,.0f}",GAP=f"{sum(gaps)/2:.0f}",
 P16_K_RED=kr,P16_L_RED=f"{Lr:,.0f}",P16_T_RED=f"{tr_:.1f}",P16_K_YEL=ky,P16_L_YEL=f"{Ly:,.0f}",P16_T_YEL=f"{ty:.1f}",
 TAB19=TAB19.strip(),TAB20=TAB20.strip(),TAB21=TAB21.strip(),
 SPLIT_RED=f"{int(R['split']['red_only']):,}",SPLIT_YEL=f"{int(R['split']['yellow_only']):,}",SPLIT_BOTH=f"{int(R['split']['both']):,}",SPLIT_BOTH_PCT=f"{R['split']['both']/WEEK_T*100:.1f}",WEEK=f"{WEEK_T:,}",
 THR_LO=10,THR_HI=50,SH_LO=f"{min(shares[t] for t in (10,20,30,50)):.1f}",SH_HI=f"{max(shares[t] for t in (10,20,30,50)):.1f}",THR_BIG=75,SH_BIG=f"{shares[75]:.1f}")
# statements in the template asserted
assert abs(Lr+0)>0 and R['split']['red_only']==199 and R['split']['yellow_only']==272
b=fill('c3_p4b.tpl.md',tpls)
open(SP+'md/c3_p4b.md','w',encoding='utf-8').write(b);print('4b bytes',len(b.encode()))
