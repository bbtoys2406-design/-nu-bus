import sys;sys.path.insert(0,'/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/th')
from wsim import *
B=json.load(open(SP+'th/base.json'))
for mode in ('round_off','round_on'):
    d='อังคาร'
    cells=B[mode]['days'][d]['cells']
    key='g' if mode=='round_on' else None
    # for round_off use raw goingC / ret
    if mode=='round_off':
        c2={h:{sid:{'g':x['raw']['goingC'],'r':x['raw']['ret']} for sid,x in v.items()} for h,v in cells.items()}
    else: c2=cells
    Dd=build_D(c2)
    tot=sum(sum(g.values())+sum(r.values()) for h,(g,r) in Dd.items())
    print(mode,'D total',round(tot,2),'web total',round(B[mode]['days'][d]['total'],2))
    new=[veh_row(r) for r in B[mode]['days'][d]['rows']]
    for name,veh in (('old',old35()),('new',new)):
        per=evaluate(veh,Dd);a=stats(per,('ret','go'))
        print(' ',name,len(veh),'mean %.2f p90 %.2f left %.2f n %.1f'%(a['mean'],a['p90'],a['left'],a['n']),
              '| go08 %.1f ret12 %.1f go13 %.1f ret17 %.1f'%tuple(stats(per,keys=[k])['mean'] for k in (('go',8),('ret',12),('go',13),('ret',17))))
