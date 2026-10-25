import json,math
SP='/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/th/'
R=json.load(open(SP+'results.json'));P=json.load(open(SP+'page.json'));B=json.load(open(SP+'base.json'))
DAYS=['จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์']
def n0(x): return f"{int(round(x)):,}"
def up(x): return f"{int(math.ceil(x-1e-9)):,}"
def f1(x): return f"{x:.1f}"
def pc(x,d=1): return f"{x*100:.{d}f}%"
def th_hour(h): return f"{int(h):02d}:00–{int(h):02d}:59"
cells_on=B['round_on']['days']; cells_off=B['round_off']['days']
def cell_sum(days, stop=None, hour=None, key=None):
    t=0
    for d in days:
        for h,hv in cells_on[d]['cells'].items():
            if hour is not None and int(h)!=hour: continue
            for s,sv in hv.items():
                if stop is not None and int(s)!=stop: continue
                for k in ('g','r'):
                    if key and k!=key: continue
                    t+=max(0,sv[k])
    return t
def md_table(header,rows,align=None):
    out='| '+' | '.join(header)+' |\n| '+' | '.join(['---']*len(header))+' |\n'
    for r in rows: out+='| '+' | '.join(str(c) for c in r)+' |\n'
    return out

# ---------- derived facts ----------
W=R['week']; W5=R['wait5']
WEEK=int(W['total']); UNR=R['unrounded_week']; 
H12=int(W['hour']['12']); H12G=cell_sum(DAYS,hour=12,key='g'); H12R=cell_sum(DAYS,hour=12,key='r')
P16=int(W['stop']['16']); P26=int(W['stop']['26']); TOP2=P16+P26
trips_new={d:R['tt'][d]['n'] for d in DAYS}; TRIPS_NEW_WEEK=sum(trips_new.values()); TRIPS_OLD=R['old_n']; TRIPS_OLD_WEEK=TRIPS_OLD*5
def seats_day(d): return sum(r['cap'] for r in B['round_on']['days'][d]['rows'])
SEATS_NEW={d:seats_day(d) for d in DAYS}; SEATS_OLD=TRIPS_OLD*35
UTIL_NEW={d:R['demand'][d]['total']/SEATS_NEW[d] for d in DAYS}; UTIL_OLD={d:R['demand'][d]['total']/SEATS_OLD for d in DAYS}
def wavg(k,seg='all'):
    n=sum(W5[d][k][seg]['n'] for d in DAYS); return sum(W5[d][k][seg]['mean']*W5[d][k][seg]['n'] for d in DAYS)/n
P90={k:[W5[d][k]['all']['p90'] for d in DAYS] for k in ('old','new')}
LEFT={k:int(sum(W5[d][k]['all']['left'] for d in DAYS)) for k in ('old','new')}
SPLIT=R['split']
