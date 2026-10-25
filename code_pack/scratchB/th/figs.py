import json,collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch,Rectangle
import numpy as np
SP='/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/th/'
fm.fontManager.addfont('/usr/share/fonts/opentype/tlwg/Loma.otf');fm.fontManager.addfont('/usr/share/fonts/opentype/tlwg/Loma-Bold.otf')
plt.rcParams.update({'font.family':'Loma','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#555','axes.labelcolor':'#222','xtick.color':'#333','ytick.color':'#333','axes.unicode_minus':False})
R=json.load(open(SP+'results.json'));P=json.load(open(SP+'page.json'))
BLUE,ORG,GRN,PUR,GRY='#2B6CB0','#E8710A','#2F855A','#8A4FBF','#8A8F98'
DAYS=['จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์']
def save(fig,n): fig.savefig(SP+'figs/'+n+'.png',dpi=200,bbox_inches='tight',facecolor='white');plt.close(fig)
# ---------- F1 framework ----------
fig,ax=plt.subplots(figsize=(6.6,5.6));ax.set_xlim(0,100);ax.set_ylim(-3,100);ax.axis('off')
def box(x,y,w,h,title,lines,fc,ec):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.3,rounding_size=1.5',fc=fc,ec=ec,lw=1.2))
    ax.text(x+w/2,y+h-3,title,ha='center',va='top',fontsize=9,fontweight='bold',color='#1a1a1a')
    for i,l in enumerate(lines): ax.text(x+w/2,y+h-11-i*6.2,l,ha='center',va='top',fontsize=7.6,color='#222')
W=31;H=36
box(1,62,W,H,'1 ข้อมูลนำเข้า',['ตารางเรียน 4,260 รายการ','ตำแหน่งอาคาร จุดจอด','เส้นทาง (GIS)','ฝูงรถ 21 คัน'],'#EEF4FB',BLUE)
box(34.5,62,W,H,'2 จับคู่อาคารกับจุดจอด',['อาคาร 40 รายการ','จุดจอดที่ใกล้ที่สุด','26 จุด (รวม P0 หอพัก)'],'#EEF4FB',BLUE)
box(68,62,W,H-0,'3 ประมาณความต้องการ',['ขาไป ขากลับ','รายจุดจอดและรายชั่วโมง','ปรับสเกล 561 × 5 วัน','ปัดคนขึ้นเป็นจำนวนเต็ม'],'#EEF4FB',BLUE)
box(68,22,W,H,'4 ออกแบบเที่ยวรถ',['ช่วงกลางวัน: กฎรถวน','ช่วงเช้าและเย็น: CVRP','(Clarke–Wright)','ไม่เพิ่มจำนวนรถ'],'#FDF1E6',ORG)
box(34.5,22,W,H,'5 ประเมินด้วยแบบจำลอง',['จำนวนเที่ยว ที่นั่งที่ใช้','เวลารอเฉลี่ยและ P90','เทียบตารางปัจจุบัน','ของมหาวิทยาลัย'],'#FDF1E6',ORG)
box(1,22,W,H,'6 ทดสอบความไว',['เวลามาถึงจุดขึ้นรถ','ความเร็วและเวลาจอด','พารามิเตอร์กฎรถวน','ขนาดกลุ่มเป้าหมาย'],'#FDF1E6',ORG)
box(34.5,1,W,15,'7 สรุปและข้อเสนอแนะ',[],'#EEF7F1',GRN)
def arr(x1,y1,x2,y2): ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=11,lw=1.3,color='#444'))
arr(32.4,80,34.0,80);arr(65.9,80,67.5,80);arr(83.5,61.6,83.5,58.6);arr(67.5,40,65.9,40);arr(34.0,40,32.4,40);arr(50,21.6,50,16.6)
save(fig,'f1_framework')
# ---------- F2 map ----------
stops={s['id']:(s['x'],s['y']) for s in P['stops']};wk=R['week']['stop'];tot=R['week']['total']
fig,ax=plt.subplots(figsize=(6.4,6.6))
for rd in P['roads']:
    xs=[p[0] for p in rd['points']];ys=[p[1] for p in rd['points']]
    ax.plot(xs,ys,color=('#D64550' if rd['name']=='แดง' else '#E0A100'),lw=3 if rd['name']=='แดง' else 2.4,alpha=.55 if rd['name']=='แดง' else .75,solid_capstyle='round',zorder=1)
mx=max(wk.values())
for sid,(x,y) in stops.items():
    d=wk.get(str(sid),0)
    if sid==0:
        ax.scatter([x],[y],marker='s',s=110,c='#222',zorder=4);ax.annotate('P0 หอพัก\n(จุดออกรถ)',(x,y),xytext=(8,-18),textcoords='offset points',fontsize=8,fontweight='bold')
        continue
    ax.scatter([x],[y],s=30+700*d/mx,c=ORG,alpha=.8,edgecolors='white',linewidths=.8,zorder=3)
    OFFS={6:(-11,-7),7:(9,6),20:(11,-3),21:(11,-12),22:(-12,5),23:(0,9),25:(10,-9),9:(0,8),10:(0,8),11:(0,8),8:(0,8),12:(-12,0),15:(-12,-6),17:(-12,-4),19:(0,-10)}
    o=OFFS.get(sid,(0,0));small=d/mx<.12
    ax.annotate('P%d'%sid,(x,y),xytext=o if (o!=(0,0) or not small) else (0,10),textcoords='offset points',ha='center',va='center',fontsize=6.8,color='#111',zorder=5,fontweight='bold' if d/mx>.4 else None)
ax.set_aspect('equal');ax.axis('off')
x0,x1=ax.get_xlim();y0,y1=ax.get_ylim()
ax.plot([x0+60,x0+560],[y0+40,y0+40],color='#222',lw=2);ax.text(x0+310,y0+90,'500 เมตร',ha='center',fontsize=8)
ax.annotate('',xy=(x1-60,y1-30),xytext=(x1-60,y1-230),arrowprops=dict(arrowstyle='-|>',color='#222',lw=1.5));ax.text(x1-60,y1+10,'N',ha='center',fontsize=10,fontweight='bold')
from matplotlib.lines import Line2D
h=[Line2D([0],[0],color='#D64550',lw=3,alpha=.6),Line2D([0],[0],color='#E0A100',lw=2.4,alpha=.8)]
for k in (250,600,1200):
    h.append(Line2D([0],[0],marker='o',ls='',color=ORG,alpha=.8,markersize=(30+700*k/mx)**.5,markeredgecolor='white'))
ax.legend(h,['สายสีแดง','สายสีเหลือง','250 เที่ยวคน','600 เที่ยวคน','1,200 เที่ยวคน'],loc='center left',bbox_to_anchor=(1.0,0.5),frameon=False,fontsize=8,title='ความต้องการรวม 5 วัน (เที่ยวคน)',title_fontsize=8,labelspacing=1.6,borderpad=1)
save(fig,'f2_map')
# ---------- F3 hourly demand (week sum, going/return) ----------
hg=collections.Counter();hr=collections.Counter()
for d in DAYS:
    for h,v in R['demand'][d]['hour_g'].items(): hg[int(h)]+=v
    for h,v in R['demand'][d]['hour_r'].items(): hr[int(h)]+=v
hs=list(range(7,21));fig,ax=plt.subplots(figsize=(6.6,3.5))
ax.bar(hs,[hg[h] for h in hs],color=GRN,width=.68,label='ขาไป (นับที่ชั่วโมงที่มาถึงจุดขึ้นรถ)',edgecolor='white',lw=.8)
ax.bar(hs,[hr[h] for h in hs],bottom=[hg[h] for h in hs],color=PUR,width=.68,label='ขากลับ (นับที่ชั่วโมงที่มาถึงจุดจอด)',edgecolor='white',lw=.8,hatch='///')
for h in hs:
    t=hg[h]+hr[h]
    if t>=60: ax.text(h,t+8,str(int(t)),ha='center',fontsize=8)
ax.set_ylim(0,1350);ax.set_xticks(hs);ax.set_xticklabels(['%02d'%h for h in hs]);ax.set_xlabel('ชั่วโมง (น.)');ax.set_ylabel('เที่ยวคน รวม 5 วัน');ax.legend(frameon=False,fontsize=8,loc='upper right')
ax.yaxis.grid(True,color='#ddd',lw=.6);ax.set_axisbelow(True);save(fig,'f3_hourly')
# ---------- F4 Tue trips vs demand ----------
hrs=list(range(7,20));dem=[R['tue_hour_dem'].get(str(h),0) for h in hrs]
old=[R['old_by_hour'].get(str(h),0) for h in hrs];new=[R['tt']['อังคาร']['by_hour'].get(str(h),0) for h in hrs]
fig,(a1,a2)=plt.subplots(2,1,figsize=(6.6,5.2),sharex=True,gridspec_kw={'height_ratios':[1,1.15]})
a1.bar(hrs,dem,color=GRY,width=.68);a1.set_ylabel('ความต้องการ\n(เที่ยวคน)')
for h,v in zip(hrs,dem):
    if v>=20: a1.text(h,v+6,str(int(v)),ha='center',fontsize=8)
a1.yaxis.grid(True,color='#ddd',lw=.6);a1.set_axisbelow(True)
w=.36;a2.bar([h-w/2 for h in hrs],old,width=w,color=BLUE,label='ตารางปัจจุบัน (156 เที่ยว)');a2.bar([h+w/2 for h in hrs],new,width=w,color=ORG,hatch='///',edgecolor='white',label='ตารางใหม่ (58 เที่ยว)')
for h,o,n in zip(hrs,old,new):
    a2.text(h-w/2,o+.3,str(o),ha='center',fontsize=7);a2.text(h+w/2,n+.3,str(n),ha='center',fontsize=7)
a2.set_ylabel('เที่ยวรถ ต่อชั่วโมง');a2.set_xticks(hrs);a2.set_xticklabels(['%02d'%h for h in hrs]);a2.set_xlabel('ชั่วโมง (น.) วันอังคาร');a2.legend(frameon=False,fontsize=8,loc='upper right')
a2.yaxis.grid(True,color='#ddd',lw=.6);a2.set_axisbelow(True);fig.tight_layout();save(fig,'f4_trips')
# ---------- F5 wait by segment ----------
W=R['wait5']['อังคาร'];seg=[('all','ทั้งวัน'),('go08','ขาไป\nคาบ 08:00'),('ret12','ขากลับ\n12:00'),('go13','ขาไป\nคาบ 13:00'),('ret17','ขากลับ\n17:00')]
fig,ax=plt.subplots(figsize=(6.6,3.6));x=np.arange(len(seg));w=.36
mo=[W['old'][k]['mean'] for k,_ in seg];mn=[W['new'][k]['mean'] for k,_ in seg]
ax.bar(x-w/2,mo,w,color=BLUE,label='ตารางปัจจุบัน');ax.bar(x+w/2,mn,w,color=ORG,hatch='///',edgecolor='white',label='ตารางใหม่')
for i,(a,b) in enumerate(zip(mo,mn)):
    ax.text(i-w/2,a+.25,'%.1f'%a,ha='center',fontsize=8);ax.text(i+w/2,b+.25,'%.1f'%b,ha='center',fontsize=8)
ax.set_xticks(x);ax.set_xticklabels([s for _,s in seg]);ax.set_ylabel('เวลารอเฉลี่ย (นาที)');ax.legend(frameon=False,fontsize=8,loc='upper left')
ax.yaxis.grid(True,color='#ddd',lw=.6);ax.set_axisbelow(True);save(fig,'f5_wait')
# ---------- F6 trade-off ----------
S=R['struct'];pts=[('rounds1','1 รอบ/ชม.'),('min1','รถขั้นต่ำ 1'),('base','ค่าตั้งต้น'),('min3','รถขั้นต่ำ 3'),('rounds4','4 รอบ/ชม.')]
fig,ax=plt.subplots(figsize=(6.6,3.8))
xs=[S[k]['n'] for k,_ in pts];ys=[S[k]['wait']['mean'] for k,_ in pts]
ax.plot(xs,ys,color=ORG,lw=1.2,alpha=.7,zorder=1);ax.scatter(xs,ys,s=45,color=ORG,zorder=3,label='ตารางที่ออกแบบด้วยกฎรถวนและ CVRP')
off={'rounds1':(8,-3),'min1':(8,-4),'base':(8,6),'min3':(8,-14),'rounds4':(8,-13)}
for (k,l),x_,y_ in zip(pts,xs,ys): ax.annotate('%s (%d เที่ยว, %.1f นาที)'%(l,x_,y_),(x_,y_),xytext=off[k],textcoords='offset points',fontsize=7.5)
o=R['wait5']['อังคาร']['old']['all']['mean'];ax.scatter([156],[o],s=60,color=BLUE,marker='s',zorder=3,label='ตารางปัจจุบันของมหาวิทยาลัย');ax.annotate('ตารางปัจจุบัน (156 เที่ยว, %.1f นาที)'%o,(156,o),xytext=(-150,-14),textcoords='offset points',fontsize=7.5)
ax.set_xlim(20,175);ax.set_ylim(0,12);ax.set_xlabel('จำนวนเที่ยวรถต่อวัน (วันอังคาร)');ax.set_ylabel('เวลารอเฉลี่ยทั้งวัน (นาที)');ax.legend(frameon=False,fontsize=8,loc='upper right')
ax.yaxis.grid(True,color='#ddd',lw=.6);ax.set_axisbelow(True);save(fig,'f6_tradeoff')
print('ok')
