# results7.py - design/demand mismatch: timetables designed for scenario A (561 boardings/day) or B (1,122) evaluated against demand A or B, 5 days.
# Reads both trees' base.json (round_on rows + cells). Cross-tree script: lives in the B tree, reads the A tree by absolute path.
import sys,os,json
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
from wsim import *
import fullday as F
PA='/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchpad/th/base.json'
PB=SP+'th/base.json'
BA=json.load(open(PA))['round_on']['days'];BB=json.load(open(PB))['round_on']['days']
def tabs(rows):
    cv=[r for r in rows if r['type'] in('cvrp','express')]
    return {'new':[veh_row(r) for r in rows],'hyb':old35()+[veh_row(r) for r in cv]}
OUT={}
for d in DAYS:
    DA=build_D(BA[d]['cells']);DB=build_D(BB[d]['cells'])
    totA=sum(sum(g.values())+sum(r.values()) for g,r in DA.values());totB=sum(sum(g.values())+sum(r.values()) for g,r in DB.values())
    TA=tabs(BA[d]['rows']);TB=tabs(BB[d]['rows'])
    o={'dem_total':{'A':totA,'B':totB}}
    for dn,Dd in (('A',DA),('B',DB)):
        r={'old':None}
        per=evaluate(old35(),Dd);r['old']=stats(per,('ret','go'))
        for des,T in (('A',TA),('B',TB)):
            for k in ('new','hyb'):
                per=evaluate(T[k],Dd);s=stats(per,('ret','go'));s['trips']=len(T[k]);r[f'{k}_{des}']=s
        o['dem'+dn]=r
    OUT[d]=o
    print(d,{dn:{k:(round(v['mean'],2),round(v['p90'],1),round(v['left'],1)) for k,v in o['dem'+dn].items()} for dn in 'AB'})
json.dump(OUT,open(SP+'th/results7.json','w'),ensure_ascii=False,indent=1)
