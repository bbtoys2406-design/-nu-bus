import sys;sys.path.insert(0,'/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/th')
from wsim import *
import fullday as F
B=json.load(open(SP+'th/base.json'));OUT={}
on=B['round_on']['days']
late={}
for d in DAYS:
    Dd=build_D(on[d]['cells']);new=[veh_row(r) for r in on[d]['rows']]
    r={}
    for name,veh in (('old',old35()),('new',new)):
        per=evaluate(veh,Dd)
        s=F.summarize(per,('go',))
        r[name]={'go_n':float(s['n']),'late_share':float(s['late']),'late_people':float(s['late']*s['served'])}
    late[d]=r
OUT['late']=late
# round-off Tuesday
d='อังคาร';cells=B['round_off']['days'][d]['cells']
c2={h:{sid:{'g':x['raw']['goingC'],'r':x['raw']['ret']} for sid,x in v.items()} for h,v in cells.items()}
Dd=build_D(c2);new=[veh_row(r) for r in B['round_off']['days'][d]['rows']]
OUT['round_off_tue']={'trips_new':len(new),'old':stats(evaluate(old35(),Dd),('ret','go')),'new':stats(evaluate(new,Dd),('ret','go')),'D_total':sum(sum(g.values())+sum(r.values()) for g,r in Dd.values())}
# unserved by hour per day (hour-20 returns etc.)
left={}
for d in DAYS:
    Dd=build_D(on[d]['cells']);new=[veh_row(r) for r in on[d]['rows']]
    lo={};ln={}
    for name,veh,tgt in (('old',old35(),lo),('new',new,ln)):
        per=evaluate(veh,Dd)
        for (k,h),(n,W,l) in per.items():
            if l>1e-6: tgt[f'{k}{h:02d}']=round(float(l),2)
    left[d]={'old':lo,'new':ln}
OUT['left_by_cell']=left
json.dump(OUT,open(SP+'th/results_extra.json','w'),ensure_ascii=False)
print(json.dumps(OUT,ensure_ascii=False,indent=0)[:3500])
