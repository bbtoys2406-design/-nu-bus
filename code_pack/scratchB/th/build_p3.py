import re,json,math,collections,sys
sys.path.insert(0,'.')
from tdat import md_table
SP='/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/th/'
TABS=open(SP+'tabs.txt',encoding='utf-8').read()
def sec(k):
    m=re.search(r'### '+k+r'[^\n]*\n(.*?)(?=\n\n|\Z)',TABS,re.S);return m.group(1).strip()
# --- example table from the parser
import io,contextlib
with contextlib.redirect_stdout(io.StringIO()):
    exec(open(SP+'xc.py').read().split("RAW=sum(raw.values())")[0])
recs=sorted(byDR[('อังคาร','NUIC203')],key=lambda r:r['st'])
assert [(r['st'],r['en'],r['enr'],r['stop']) for r in recs]==[(480,590,66,16),(600,710,61,16),(780,950,29,16)]
def hm(m): return f"{m//60:02d}:{m%60:02d}"
rows=[];en=[r['en'] for r in recs];st=[r['st'] for r in recs]
for r in recs:
    g_ch=any(0<r['st']-e<=10 for e in en);r_ch=any(0<s-r['en']<=10 for s in st)
    g=("ไม่นับ (คาบต่อเนื่อง)" if g_ch else f"ชั่วโมง {(r['st']-30)//60} ที่ P{r['stop']}: {r['enr']}")
    rr=("ไม่นับ (คาบต่อเนื่อง)" if r_ch else f"ชั่วโมง {(r['en']+10)//60} ที่ P{r['stop']}: {r['enr']}")
    rows.append([f"{hm(r['st'])}–{hm(r['en'])} น.",str(r['enr']),g,rr])
EX=md_table(['ช่วงเรียน','ผู้ลงทะเบียน (คน)','ขาไป (ชั่วโมง จุดจอด: จำนวน)','ขากลับ (ชั่วโมง จุดจอด: จำนวน)'],rows)
# --- bands table
B=json.load(open(SP+'base.json'));off=B['round_off']['days'];on=B['round_on']['days']
cells=[]
for d in off:
    for h,v in off[d]['cells'].items():
        for s,c in v.items():
            for k in ('g','r'):
                if c[k]>1e-9: cells.append((c[k],on[d]['cells'][h][s][k]))
assert len(cells)==751 and sum(c[1] for c in cells)==3202 and abs(sum(c[0] for c in cells)-2805)<1e-6
bands=[('น้อยกว่า 1',0,1),('1 ถึงน้อยกว่า 2',1,2),('2 ถึงน้อยกว่า 5',2,5),('5 ถึงน้อยกว่า 10',5,10),('10 ขึ้นไป',10,1e9)]
brow=[];tc=tu=ta=0
for name,lo,hi in bands:
    cc=[c for c in cells if lo<=c[0]<hi];n=len(cc);u=sum(c[0] for c in cc);r=sum(c[1] for c in cc)
    brow.append([name,f"{n:,}",f"{u:,.1f}",f"{r:,.0f}",f"{r-u:,.1f}",f"{(r-u)/(397)*100:.1f}%"]);tc+=n;tu+=u;ta+=r-u
brow.append(['รวม',f"{tc:,}",f"{tu:,.1f}",f"{sum(c[1] for c in cells):,}",f"{ta:,.1f}",'100.0%'])
BANDS=md_table(['ขนาดเซลล์ก่อนปัดเศษ (คน)','จำนวนเซลล์','ผลรวมก่อนปัดเศษ','ผลรวมหลังปัดเศษ','ส่วนที่เพิ่ม','สัดส่วนของส่วนที่เพิ่มทั้งหมด'],brow)
assert brow[0][1]=='257' and brow[0][4]=='130.0'
g=sum(c['g'] for d in on for h in on[d]['cells'] for c in on[d]['cells'][h].values());r_=sum(c['r'] for d in on for h in on[d]['cells'] for c in on[d]['cells'][h].values())
assert (round(g),round(r_))==(1598,1604),(g,r_)
def fill(tpl,subs):
    s=open(SP+'md/'+tpl,encoding='utf-8').read()
    for k,v in subs.items(): s=s.replace('{{'+k+'}}',v)
    assert '{{' not in s
    return s
a=fill('c3_p3a.tpl.md',{'B2S':sec('B2S')})
b=fill('c3_p3b.tpl.md',{'EXAMPLE':EX,'ROUNDING':sec('ROUNDING'),'BANDS':BANDS})
open(SP+'md/c3_p3a.md','w',encoding='utf-8').write(a);open(SP+'md/c3_p3b.md','w',encoding='utf-8').write(b)
print(len(a.encode()),len(b.encode()));print(EX);print(BANDS)
