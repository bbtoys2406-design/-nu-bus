# Page-dependent extraction (Tuesday variants + coverage) -> th/page.json
from playwright.sync_api import sync_playwright
import json,openpyxl,collections
SP='/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/'
ROWJS="LAST_TIMETABLE.map(r=>({t:r.time,rt:r.rawTime,type:r.type,sign:r.sign,label:r.label,cap:r.cap,load:r.load,cars:r.carCount,deps:r.departures}))"
CELLJS="""()=>{const o={};const sd=APP_STATE.stopDemand['อังคาร']||{};
 for(const sid in sd){for(const h in sd[sid]){const v=sd[sid][h];const c=cellPeople(v);(o[h]=o[h]||{})[sid]={g:c.g,r:c.r}}}return o}"""
def rows_of(f):
    wb=openpyxl.load_workbook('/mnt/user-data/uploads/'+f,read_only=True);ws=wb[wb.sheetnames[0]]
    return [r[0] if isinstance(r[0],str) else str(r[0]) for i,r in enumerate(ws.iter_rows(values_only=True)) if i>=4 and r and r[0]]
def variant(pg,name,roundup=True,lead='30',cfg=None,pct='100',fleet=None):
    pg.goto('file://'+SP+'v4_new.html');pg.wait_for_timeout(900)
    pg.evaluate("(r)=>{document.getElementById('roundUp').checked=r}",roundup)
    pg.select_option('#goingLead',lead);pg.select_option('#captivePercent',pct)
    if fleet: pg.evaluate("(f)=>{FLEET[0].cap=f[0];FLEET[1].cap=f[1];renderFleetEditor()}",fleet)
    for k,v in dict(dormStudents=1122,motorcycleParking=0,**(cfg or {})).items():
        if k=='useCvrp': pg.evaluate("document.getElementById('useCvrp').checked=false")
        else: pg.fill('#'+k,str(v))
    pg.evaluate("onTargetChange()");pg.wait_for_timeout(400)
    pg.select_option('#ttDaySelect','อังคาร');pg.wait_for_timeout(500)
    rows=pg.evaluate(ROWJS);cells=pg.evaluate(CELLJS);tot=pg.evaluate("LAST_DAY_TOTAL")
    fc=pg.evaluate("LAST_FLEETCHECK.map(f=>({h:f.hour,cvrp:f.cvrpBusy,loop:f.loopN,inS:f.inService,ok:f.ok,short:f.short}))")
    return {'name':name,'rows':rows,'cells':cells,'total':tot,'fleet':fc}
out={'variants':{}}
VAR=[('base',{}),('round_off',dict(roundup=False)),('upper',dict(fleet=[40,14])),
 ('rounds4',dict(cfg={'roundsPerHour':4})),('rounds1',dict(cfg={'roundsPerHour':1})),('cvrp_off',dict(cfg={'useCvrp':0})),
 ('min1',dict(cfg={'minCars':1})),('min3',dict(cfg={'minCars':3})),('lf100',dict(cfg={'loadFactor':100})),('lf70',dict(cfg={'loadFactor':70})),
 ('lead0',dict(lead='0')),('lead15',dict(lead='15')),
 ('pct30',dict(pct='30')),('pct50',dict(pct='50')),('pct70',dict(pct='70')),('pct80',dict(pct='80'))]
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1200,'height':900})
    for n,kw in VAR:
        out['variants'][n]=variant(pg,n,**kw);print(n,len(out['variants'][n]['rows']),round(out['variants'][n]['total'],1),flush=True)
    # coverage
    pg.goto('file://'+SP+'v4_stage1.html');pg.wait_for_timeout(1500)
    cov={}
    for f in ('schedule.xlsx',):
        rows=rows_of(f)
        res=pg.evaluate("""(rows)=>{const segs=parseTerm1Text(rows).segments;
          const byDay={};let unm={};let wk=0,matchedWk=0,enrW=0,enrM=0;
          for(const s of segs){byDay[s.day]=(byDay[s.day]||0)+1;
            const b=roomToBuildingTerm1(s.room);const isW=DAYS.includes(s.day);
            if(isW){wk++;enrW+=s.enrolled;}
            if(b && (b in GEO_DATA.building_to_stop)){ if(isW){matchedWk++;enrM+=s.enrolled;} }
            else if(isW){const k=(s.room||'').replace(/[0-9\\s-]+.*$/,'')||'(ว่าง)';unm[k]=(unm[k]||0)+1}}
          const r=computeStopDemand(segs,(seg)=>roomToBuildingTerm1(seg.room));
          return {nseg:segs.length,byDay,wk,matchedWk,enrW,enrM,unm,matched:r.matched,total:r.total}}""",rows)
        res['records']=len(rows);cov=res
    out['coverage']=cov
    out['b2s']=pg.evaluate("GEO_DATA.building_to_stop");out['stops']=pg.evaluate("GEO_DATA.stops");out['roads']=pg.evaluate("GEO_DATA.roads")
    b.close()
json.dump(out,open(SP+'th/page.json','w'),ensure_ascii=False)
print(json.dumps(out['coverage'],ensure_ascii=False)[:800])
