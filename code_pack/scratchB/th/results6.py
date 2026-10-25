# results6.py - Tuesday demand sweep for three timetables (old / proposed / old + CVRP). Run in each tree; reads page.json (+ page_extra.json if present).
# boardings/day = round(target*pct/100); the proposed timetable is rebuilt by the web code at each level (variants pctNN), old is fixed, hybrid = old + CVRP/express rows of that level.
import sys,os,json,math
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
from wsim import *
import fullday as F
import passup as PU
PG=json.load(open(SP+'th/page.json'));V=PG['variants']
EX=json.load(open(SP+'th/page_extra.json')) if os.path.exists(SP+'th/page_extra.json') else {}
TARGET=json.load(open(SP+'th/results.json'))['pop']['100']['pop']   # boardings/day at pct100 of this tree
def late(per):
    s=F.summarize(per,('go',));return float(s['late']),float(s['late']*s['served'])
def pk(per):
    a=stats(per,('ret','go'));a['late_share'],a['late_people']=late(per);return a
levels=[]
src=[(k,V[k],round(TARGET*pc/100)) for k,pc in (('pct30',30),('pct50',50),('pct70',70),('pct80',80),('base',100))]+[(k,v,v['dorm']) for k,v in EX.items()]
for k,v,pop in src:
    Dd=build_D(v['cells']);rows=v['rows'];cv=[r for r in rows if r['type'] in('cvrp','express')]
    tot=sum(sum(g.values())+sum(r.values()) for g,r in Dd.values())
    assert abs(tot-v['total'])<1e-6,(k,tot,v['total'])
    tabs={'old':old35(),'new':[veh_row(r) for r in rows],'hyb':old35()+[veh_row(r) for r in cv]}
    o={'key':k,'boardings':pop,'tue_total':tot,'trips':{n:len(x) for n,x in tabs.items()},'seats':{n:sum(y['cap'] for y in x) for n,x in tabs.items()},
       'fleet_short':[f['h'] for f in v['fleet'] if f['short'] or not f['ok']],'max_inS':max(f['inS'] for f in v['fleet'])}
    assert o['trips']['hyb']==156+len(cv)
    for n,x in tabs.items():
        per=evaluate(x,Dd);o[n]=pk(per)
        for hi in (31,45):
            tot,cells=PU.pass_eval(x,Dd,hi=hi,lo=30);o[n]['pass%d'%hi]={'ret':tot['ret'],'go':tot['go']}
        if n=='old':
            o['old_left_cells']={f'{kk}{h:02d}':round(float(l),2) for (kk,h),(nn,W,l) in per.items() if l>1e-6}
            o['old_left_in_service']=round(float(sum(l for (kk,h),(nn,W,l) in per.items() if h<=18)),2)
    levels.append(o)
levels.sort(key=lambda x:x['boardings'])
for o in levels: print(o['boardings'],round(o['tue_total']),o['trips'],'mean',[round(o[n]['mean'],2) for n in('old','new','hyb')],'p90',[round(o[n]['p90'],1) for n in('old','new','hyb')],'left',[round(o[n]['left'],1) for n in('old','new','hyb')],'short',o['fleet_short'],'inS',o['max_inS'])
json.dump(levels,open(SP+'th/results6.json','w'),ensure_ascii=False,indent=1)
