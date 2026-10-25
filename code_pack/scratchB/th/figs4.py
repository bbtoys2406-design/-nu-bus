# figs4.py - figures of chapter 4 (base demand 1,122 boardings/day). Reads results.json, results5.json, results6.json and results6_low.json (levels 168-449).
import json,collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.lines import Line2D
import numpy as np
ROOT='/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/'
SPB=ROOT+'scratchB/th/'
fm.fontManager.addfont('/usr/share/fonts/opentype/tlwg/Loma.otf');fm.fontManager.addfont('/usr/share/fonts/opentype/tlwg/Loma-Bold.otf')
plt.rcParams.update({'font.family':'Loma','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#555','axes.labelcolor':'#222','xtick.color':'#333','ytick.color':'#333','axes.unicode_minus':False})
J=lambda p:json.load(open(p))
RB=J(SPB+'results.json');R5B=J(SPB+'results5.json');R6A,R6B=J(SPB+'results6_low.json'),J(SPB+'results6.json')
BLUE,ORG,GRN,PUR,GRY='#2B6CB0','#E8710A','#2F855A','#8A4FBF','#8A8F98'
DAYS=['จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์'];T='อังคาร'
def save(fig,n): fig.savefig(SPB+'figs/'+n+'.png',dpi=200,bbox_inches='tight',facecolor='white');plt.close(fig)
# ---------- 4.1 hourly demand A | B ----------
def hourly(R):
    hg=collections.Counter();hr=collections.Counter()
    for d in DAYS:
        for h,v in R['demand'][d]['hour_g'].items(): hg[int(h)]+=v
        for h,v in R['demand'][d]['hour_r'].items(): hr[int(h)]+=v
    return hg,hr
hs=list(range(7,21));fig,ax=plt.subplots(figsize=(6.6,3.5))
hg,hr=hourly(RB)
ax.bar(hs,[hg[h] for h in hs],color=GRN,width=.72,edgecolor='white',lw=.6,label='ขาไป')
ax.bar(hs,[hr[h] for h in hs],bottom=[hg[h] for h in hs],color=PUR,width=.72,edgecolor='white',lw=.6,hatch='///',label='ขากลับ')
top=max(hg[h]+hr[h] for h in hs);ax.set_ylim(0,top*1.15)
for h in hs:
    t=hg[h]+hr[h]
    if t>=0.1*top: ax.text(h,t+top*0.015,str(int(t)),ha='center',fontsize=8)
ax.set_xticks(hs);ax.set_xticklabels(['%02d'%h for h in hs]);ax.set_xlabel('ชั่วโมงที่นับ (น.)')
ax.yaxis.grid(True,color='#ddd',lw=.6);ax.set_axisbelow(True);ax.set_ylabel('เที่ยวคน รวม 5 วัน');ax.legend(frameon=False,fontsize=8,loc='upper right')
fig.tight_layout();save(fig,'f43_hourly')
# ---------- 4.3 Tuesday trips ----------
hrs=list(range(7,20));fig,(a1,a2)=plt.subplots(2,1,figsize=(6.8,5.6),sharex=True,gridspec_kw={'height_ratios':[1,1.2]})
a1.bar(hrs,[RB['tue_hour_dem'].get(str(h),0) for h in hrs],.6,color=PUR,alpha=.85)
a1.set_ylabel('ความต้องการ\n(เที่ยวคน)');a1.yaxis.grid(True,color='#ddd',lw=.6);a1.set_axisbelow(True)
w=.38
old=[RB['old_by_hour'].get(str(h),0) for h in hrs];nB=[RB['tt'][T]['by_hour'].get(str(h),0) for h in hrs]
a2.bar([h-w/2 for h in hrs],old,w,color=BLUE,label='ตารางปัจจุบัน (156 เที่ยว)')
a2.bar([h+w/2 for h in hrs],nB,w,color=ORG,hatch='///',edgecolor='white',label='ตารางที่เสนอ (%d เที่ยว)'%RB['tt'][T]['n'])
a2.set_ylabel('เที่ยวรถต่อชั่วโมง');a2.set_xticks(hrs);a2.set_xticklabels(['%02d'%h for h in hrs]);a2.set_xlabel('ชั่วโมง (น.) วันอังคาร');a2.legend(frameon=False,fontsize=8,loc='upper right')
a2.yaxis.grid(True,color='#ddd',lw=.6);a2.set_axisbelow(True);fig.tight_layout();save(fig,'f45_trips')
# ---------- 4.4 wait by period, 3 timetables, A | B ----------
seg=[('all','ทั้งวัน'),('go08','ขาไป\nคาบ 08:00'),('ret12','ขากลับ\n12:00'),('go13','ขาไป\nคาบ 13:00'),('ret17','ขากลับ\n17:00')]
fig,ax=plt.subplots(figsize=(6.8,3.7));x=np.arange(len(seg));w=.27
for j,(k,lab,c,hat) in enumerate((('old','ตารางปัจจุบัน',BLUE,None),('new','ตารางที่เสนอ',ORG,'///'),('hyb','ปัจจุบัน + CVRP',GRN,'...'))):
    v=[R5B[T]['win31'][k][s_]['mean'] if s_!='all' else R5B[T]['win31'][k]['all']['mean'] for s_,_ in seg]
    ax.bar(x+(j-1)*w,v,w,color=c,hatch=hat,edgecolor='white',label=lab)
    for i,b_ in enumerate(v): ax.text(i+(j-1)*w,b_+.25,'%.1f'%b_,ha='center',fontsize=7)
ax.set_xticks(x);ax.set_xticklabels([s_ for _,s_ in seg],fontsize=8);ax.yaxis.grid(True,color='#ddd',lw=.6);ax.set_axisbelow(True)
ax.set_ylabel('เวลารอเฉลี่ย (นาที)');ax.legend(frameon=False,fontsize=8,loc='upper left')
fig.tight_layout();save(fig,'f47_wait')
# ---------- 4.5 trade-off ----------
fig,ax=plt.subplots(figsize=(6.8,4.2))
pts=['rounds1','min1','base','min3','rounds4']
for R,R5,col,mk in ((RB,R5B,PUR,'D'),):
    S=R['struct'];xs=[S[k]['n'] for k in pts];ys=[S[k]['wait']['mean'] for k in pts]
    ax.plot(xs,ys,color=col,lw=1.1,alpha=.7);ax.scatter(xs,ys,s=40,color=col,marker=mk,zorder=3)
    ax.scatter([S['base']['n']],[S['base']['wait']['mean']],s=130,facecolors='none',edgecolors=col,lw=1.5,zorder=4)
    d=R5[T]['win31']
    ax.scatter([156],[d['old']['all']['mean']],s=70,color=col,marker='s',zorder=3)
    ax.scatter([R5[T]['trips']['hyb']],[d['hyb']['all']['mean']],s=70,color=col,marker='^',zorder=3)
    ax.scatter([R5[T]['trips']['hyb_top3']],[d['hyb_top3']['all']['mean']],s=90,color=col,marker='*',zorder=3)
ax.set_xlim(20,205);ax.set_ylim(0,13);ax.set_xlabel('จำนวนเที่ยวรถต่อวัน (วันอังคาร)');ax.set_ylabel('เวลารอเฉลี่ยทั้งวัน (นาที)')
h=[Line2D([0],[0],color=PUR,marker='D',lw=1.1),Line2D([0],[0],ls='',marker='o',mfc='none',mec='#333',ms=10),Line2D([0],[0],ls='',marker='s',color='#555'),Line2D([0],[0],ls='',marker='^',color='#555'),Line2D([0],[0],ls='',marker='*',color='#555',ms=10)]
ax.legend(h,['ตารางที่เสนอ (ปรับพารามิเตอร์)','ค่าตั้งต้น','ตารางปัจจุบัน','ปัจจุบัน + CVRP','ปัจจุบัน + CVRP + รถวนใน 3 ชั่วโมงสูงสุด'],frameon=False,fontsize=7.5,loc='upper right')
ax.yaxis.grid(True,color='#ddd',lw=.6);ax.set_axisbelow(True);save(fig,'f48_tradeoff')
# ---------- 4.6 demand sweep ----------
L={}
for o in R6A+R6B:
    if o['boardings'] in L: assert abs(L[o['boardings']]['old']['mean']-o['old']['mean'])<1e-9 and abs(L[o['boardings']]['new']['mean']-o['new']['mean'])<1e-9
    L[o['boardings']]=o
ks=sorted(L);fig,ax=plt.subplots(figsize=(6.8,4.0))
for n,lab,c,ls in (('old','ตารางปัจจุบัน',BLUE,'-'),('new','ตารางที่เสนอ (สร้างใหม่ทุกระดับ)',ORG,'-'),('hyb','ปัจจุบัน + CVRP',GRN,'--')):
    ax.plot(ks,[L[k][n]['mean'] for k in ks],color=c,ls=ls,marker='o',ms=4,label=lab)
ax.set_xscale('log');ax.set_xticks([168,337,561,1122,1696,3392]);ax.set_xticklabels(['168','337','561','1,122\n(ฐาน)','1,696','3,392'],fontsize=8)
ax.minorticks_off();ax.set_xlabel('จำนวนครั้งขึ้นรถต่อวัน (สเกลลอการิทึม)');ax.set_ylabel('เวลารอเฉลี่ยทั้งวัน (นาที) วันอังคาร');ax.legend(frameon=False,fontsize=8,loc='upper left')
ax.yaxis.grid(True,color='#ddd',lw=.6);ax.set_axisbelow(True);save(fig,'f410_sweep')
print('ok')
