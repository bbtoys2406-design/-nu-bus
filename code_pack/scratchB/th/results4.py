# Sensitivity of the demand DISTRIBUTION to the same-room chaining rule (no wait model). Uses the independent parser in xc.py.
import json,math,collections
SP='/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/th/'
exec(open(SP+'xc.py').read().split("RAW=sum(raw.values())")[0])
def build(chain=True):
    raw=collections.defaultdict(float);excl_g=excl_r=0
    for (d,room),recs in byDR.items():
        st=sorted(r['st'] for r in recs);en=sorted(r['en'] for r in recs)
        for r in recs:
            if not chain or not any(0<r['st']-e<=10 for e in en): raw[(d,r['stop'],(r['st']-30)//60,'g')]+=r['enr']
            else: excl_g+=1
            if not chain or not any(0<s-r['en']<=10 for s in st): raw[(d,r['stop'],(r['en']+10)//60,'r')]+=r['enr']
            else: excl_r+=1
    return raw,excl_g,excl_r
OUT={}
for name,chain in (('chain_on',True),('chain_off',False)):
    raw,eg,er=build(chain);RAW=sum(raw.values());k=1122*5/RAW
    hr=collections.Counter();st=collections.Counter()
    for (d,s,h,t),v in raw.items():
        c=math.ceil(v*k-1e-9);hr[h]+=c;st[s]+=c
    tot=sum(hr.values());ph,pv=max(hr.items(),key=lambda x:x[1])
    OUT[name]=dict(raw_total=RAW,k=k,cells=len(raw),total_rounded=tot,peak_hour=ph,peak_people=pv,peak_share=pv/tot,
                   p16_p26_share=(st[16]+st[26])/tot,going_excluded=eg,return_excluded=er,hour={str(h):v for h,v in sorted(hr.items())})
E_=json.load(open(SP+'results_extra.json'));E_['chain_sens']=OUT
json.dump(E_,open(SP+'results_extra.json','w'),ensure_ascii=False,indent=1)
print(json.dumps({k:{a:(round(b,4) if isinstance(b,float) else b) for a,b in v.items() if a!='hour'} for k,v in OUT.items()},ensure_ascii=False,indent=1))
