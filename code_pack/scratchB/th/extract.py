# Extract everything needed for the thesis from the final web model (v4_new.html), rounding ON/OFF
from playwright.sync_api import sync_playwright
import json,sys
SP='/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/'
DAYS=['จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์']
ROWJS="LAST_TIMETABLE.map(r=>({t:r.time,rt:r.rawTime,type:r.type,sign:r.sign,label:r.label,cap:r.cap,load:r.load,cars:r.carCount,deps:r.departures}))"
FCJS="LAST_FLEETCHECK.map(f=>({h:f.hour,cvrp:f.cvrpBusy,loop:f.loopN,inS:f.inService,ok:f.ok,short:f.short}))"
def run(pg,roundup,lead='30',cfg=None):
    pg.goto('file://'+SP+'v4_new.html');pg.wait_for_timeout(1200)
    pg.evaluate("(r)=>{document.getElementById('roundUp').checked=r}",roundup)
    pg.select_option('#goingLead',lead)
    for k,v in dict(dormStudents=1122,motorcycleParking=0,**(cfg or {})).items():
        if k=='useCvrp': pg.evaluate("document.getElementById('useCvrp').checked=false")
        else: pg.fill('#'+k,str(v))
    pg.evaluate("onTargetChange()");pg.wait_for_timeout(500)
    out={'scale':pg.evaluate("APP_STATE.scale"),'days':{}}
    for d in DAYS:
        pg.select_option('#ttDaySelect',d);pg.wait_for_timeout(600)
        rows=pg.evaluate(ROWJS);fc=pg.evaluate(FCJS);tot=pg.evaluate("LAST_DAY_TOTAL")
        cells=pg.evaluate("""(d)=>{const o={};const sd=APP_STATE.stopDemand[d]||{};for(const sid in sd){for(const h in sd[sd?sid:0]){}}
          for(const sid in sd){for(const h in sd[sid]){const v=sd[sid][h];const c=cellPeople(v);
            (o[h]=o[h]||{})[sid]={g:c.g,r:c.r,raw:{going:v.going*APP_STATE.scale,goingB:v.goingB*APP_STATE.scale,goingC:(v.goingC||0)*APP_STATE.scale,ret:v.return*APP_STATE.scale}}}}return o}""",d)
        out['days'][d]={'rows':rows,'fleet':fc,'total':tot,'cells':cells}
    return out
if __name__=='__main__':
    res={}
    with sync_playwright() as p:
        b=p.chromium.launch();pg=b.new_page(viewport={'width':1200,'height':900})
        res['round_on']=run(pg,True)
        res['round_off']=run(pg,False)
        b.close()
    json.dump(res,open(SP+'th/base.json','w'),ensure_ascii=False)
    for k in res:
        print(k,'scale',res[k]['scale'])
        for d in DAYS:
            r=res[k]['days'][d];import collections
            c=collections.Counter(x['type'] for x in r['rows'])
            print('  ',d,'trips',len(r['rows']),dict(c),'day total',round(r['total'],1))
