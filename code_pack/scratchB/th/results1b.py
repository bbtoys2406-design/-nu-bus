# Extra variants (scenario-B tree only): b1696 = all 1,696 dorm students ride once per day; b3392 = all ride both ways (stress test). -> th/page_extra.json
from playwright.sync_api import sync_playwright
import json
SP='/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/'
ROWJS="LAST_TIMETABLE.map(r=>({t:r.time,rt:r.rawTime,type:r.type,sign:r.sign,label:r.label,cap:r.cap,load:r.load,cars:r.carCount,deps:r.departures}))"
CELLJS="""()=>{const o={};const sd=APP_STATE.stopDemand['อังคาร']||{};
 for(const sid in sd){for(const h in sd[sid]){const v=sd[sid][h];const c=cellPeople(v);(o[h]=o[h]||{})[sid]={g:c.g,r:c.r}}}return o}"""
def variant(pg,name,dorm):
    pg.goto('file://'+SP+'v4_new.html');pg.wait_for_timeout(900)
    pg.evaluate("(r)=>{document.getElementById('roundUp').checked=r}",True)
    pg.select_option('#goingLead','30');pg.select_option('#captivePercent','100')
    pg.fill('#dormStudents',str(dorm));pg.fill('#motorcycleParking','0')
    pg.evaluate("onTargetChange()");pg.wait_for_timeout(400)
    pg.select_option('#ttDaySelect','อังคาร');pg.wait_for_timeout(500)
    rows=pg.evaluate(ROWJS);cells=pg.evaluate(CELLJS);tot=pg.evaluate("LAST_DAY_TOTAL")
    fc=pg.evaluate("LAST_FLEETCHECK.map(f=>({h:f.hour,cvrp:f.cvrpBusy,loop:f.loopN,inS:f.inService,ok:f.ok,short:f.short}))")
    return {'name':name,'dorm':dorm,'rows':rows,'cells':cells,'total':tot,'fleet':fc}
out={}
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1200,'height':900})
    for n,d in (('b1696',1696),('b3392',3392)):
        out[n]=variant(pg,n,d);print(n,len(out[n]['rows']),round(out[n]['total'],1),[ (f['h'],f['inS'],f['ok'],f['short']) for f in out[n]['fleet'] if not f['ok'] or f['short']],flush=True)
    b.close()
json.dump(out,open(SP+'th/page_extra.json','w'),ensure_ascii=False)
