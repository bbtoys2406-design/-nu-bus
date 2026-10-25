# Independent cross-check (Python) of demand pipeline from schedule.xlsx -> compare with the web model's base.json
import re,json,math,collections,openpyxl
SP='/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/th/'
P=json.load(open(SP+'page.json'));B=json.load(open(SP+'base.json'))
b2s=P['b2s']
wb=openpyxl.load_workbook('/mnt/user-data/uploads/schedule.xlsx',read_only=True);ws=wb[wb.sheetnames[0]]
rows=[r[0] if isinstance(r[0],str) else str(r[0]) for i,r in enumerate(ws.iter_rows(values_only=True)) if i>=4 and r and r[0]]
TAIL=re.compile(r'(\d+)\s*\((\d+)/(\d+)\)\s+(\d+)\s+(\d+)\s+(\d+)\s+([WN])\s*$')
DAYRE=re.compile(r'(MO|TU|WE|TH|FR|SA|SU)\s+(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})')
DAYTH={'MO':'จันทร์','TU':'อังคาร','WE':'พุธ','TH':'พฤหัสบดี','FR':'ศุกร์'}
stat=collections.Counter();segs=[]
for t in rows:
    if t.startswith('[หน้า'): stat['page_sep']+=1;continue
    m=TAIL.search(t)
    if not m: stat['no_tail']+=1;continue
    if m.group(7)!='W': stat['status_N']+=1;continue
    body=t[:m.start()];ms=list(DAYRE.finditer(body))
    if not ms: stat['W_no_day']+=1;continue
    stat['W_with_day']+=1
    for i,mm in enumerate(ms):
        rs=mm.end();re_=ms[i+1].start() if i+1<len(ms) else len(body)
        segs.append(dict(day=mm.group(1),sh=int(mm.group(2)),sm=int(mm.group(3)),eh=int(mm.group(4)),em=int(mm.group(5)),room=body[rs:re_].strip(),enr=int(m.group(5))))
print('records',len(rows),dict(stat),'segments',len(segs))
wk=[s for s in segs if s['day'] in DAYTH]
print('weekday segs',len(wk),'weekend',len(segs)-len(wk))
PREF={'QS':'qs','HU':'มนุษย์','ED':'ศึกษา','NUIC':'นานาชาติ','EN':'วิศวะ','MD':'วิทย์แพทย์','ARC':'สถาปัต','PH':'เภสัช','AHS':'สหเวช','BEC':'bec','DT':'ทันตแพทย์','LAW':'นิติ','EE':'วิศวะ','CE':'วิศวะ','IE':'วิศวะ','AN':'agi','ARL':'agi','Pharma':'เภสัช'}
def r2b(room):
    room=room.strip()
    if room.startswith('ปราบไตรจักร2') or room.startswith('ปราบ2'): return 'ปราบ2'
    if room.startswith('ปราบไตรจักร') or room.startswith('ปราบไตร'): return 'ปราบไตร'
    if room.startswith('AG'): return 'agi'
    if room.startswith('สนามกีฬาฟุตบ'): return 'สนามฟุตบอล'
    m=re.match(r'^SC\s*([1-5])',room)
    if m: return 'sc'+m.group(1)
    m=re.match(r'^([A-Za-z]+)',room)
    if m and m.group(1) in PREF: return PREF[m.group(1)]
    return None
byDR=collections.defaultdict(list);matched=0;enrW=0;enrM=0
for s in wk:
    enrW+=s['enr'];b=r2b(s['room'])
    if not b or b not in b2s: continue
    matched+=1;enrM+=s['enr']
    byDR[(DAYTH[s['day']],s['room'])].append(dict(stop=b2s[b],st=s['sh']*60+s['sm'],en=s['eh']*60+s['em'],enr=s['enr']))
print('matched weekday',matched,'of',len(wk),round(matched/len(wk)*100,2),'| seats',enrM,'of',enrW,round(enrM/enrW*100,2))
raw=collections.defaultdict(float);chain_in=chain_out=0
for (d,room),recs in byDR.items():
    st=sorted(r['st'] for r in recs);en=sorted(r['en'] for r in recs)
    for r in recs:
        if not any(0<r['st']-e<=10 for e in en):
            raw[(d,r['stop'],(r['st']-30)//60,'g')]+=r['enr']
        else: chain_in+=1
        if not any(0<s-r['en']<=10 for s in st):
            raw[(d,r['stop'],(r['en']+10)//60,'r')]+=r['enr']
        else: chain_out+=1
RAW=sum(raw.values());k=1122*5/RAW
print('RAW',RAW,'k',k,'chained going excluded',chain_in,'chained return excluded',chain_out)
# compare with web model cells (rounded)
bad=0;tot_on=0;tot_off=0
DAYS=['จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์']
for d in DAYS:
    cells=B['round_on']['days'][d]['cells']
    for key,v in raw.items():
        pass
    py={}
    for (dd,stop,h,kind),v in raw.items():
        if dd==d: py[(h,stop,kind)]=v*k
    web={}
    for h,hv in cells.items():
        for sid,x in hv.items():
            web[(int(h),int(sid),'g')]=x['g'];web[(int(h),int(sid),'r')]=x['r']
    keys=set(py)|{kk for kk,v in web.items() if v}
    for kk in keys:
        a=math.ceil(py.get(kk,0)-1e-9);b=web.get(kk,0)
        if a!=b: bad+=1;print('MISMATCH',d,kk,a,b)
        tot_on+=a
    tot_off+=sum(py.values())
print('python ceil total',tot_on,'unrounded',round(tot_off,3),'cell mismatches',bad)

# ---- extra: share of demand by building; names whose 2nd-nearest stop is within 20 m
rawb=collections.defaultdict(float)
for s in wk:
    pass
byb=collections.defaultdict(list)
for s in wk:
    b=r2b(s['room'])
    if b and b in b2s: byb[(DAYTH[s['day']],s['room'])].append((b,s))
tb=collections.defaultdict(float)
for (d,room),lst in byb.items():
    st=sorted(x[1]['sh']*60+x[1]['sm'] for x in lst);en=sorted(x[1]['eh']*60+x[1]['em'] for x in lst)
    for b,s in lst:
        a=s['sh']*60+s['sm'];e=s['eh']*60+s['em']
        if not any(0<a-x<=10 for x in en): tb[b]+=s['enr']
        if not any(0<x-e<=10 for x in st): tb[b]+=s['enr']
G=json.load(open(SP+'geo_res.json'))
close=[n for n in b2s if n in G and n not in('หอใน','จุดเริิ่มเส้นทาง') and G[n]['d2']-G[n]['d1']<=20]
sh=sum(tb[n] for n in close)/sum(tb.values())
print('raw share of 11 close names',round(sh*100,1),'%','; football share',round(tb['สนามฟุตบอล']/sum(tb.values())*100,2))
cells=sum(1 for kk,v in raw.items())
print('nonzero raw cells',cells)
cc=set()
for (d,stop,h,kind) in raw: cc.add((d,stop,h,kind))
print('cells (day,stop,hour,dir)',len(cc))
json.dump({k:v for k,v in tb.items()},open(SP+'raw_by_bldg.json','w'),ensure_ascii=False)

# ---- extra: minute-of-hour structure of counted events (weighted by enrolment, after chaining exclusion)
gm=collections.Counter();rm=collections.Counter()
for (d,room),recs in byDR.items():
    st=sorted(r['st'] for r in recs);en=sorted(r['en'] for r in recs)
    for r in recs:
        if not any(0<r['st']-e<=10 for e in en): gm[r['st']%60]+=r['enr']
        if not any(0<s-r['en']<=10 for s in st): rm[(r['en']+10)%60]+=r['enr']
G_=sum(gm.values());R_=sum(rm.values())
print('going start minute dist',{k:round(v/G_*100,2) for k,v in gm.items()})
print('return arrival minute dist',{k:round(v/R_*100,2) for k,v in rm.items()})
# total weekly going / return raw
gt=sum(v for kk,v in raw.items() if kk[3]=='g');rt=sum(v for kk,v in raw.items() if kk[3]=='r')
print('raw going',gt,'raw return',rt)
print('going scaled',gt*k,'return scaled',rt*k)
