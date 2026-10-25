import json,math,re,numpy as np
RP=json.load(open('route_pos.json'));SD=json.load(open('/root/.claude/uploads/5d08b61f-0d0d-5ed9-b111-61441aa95e91/bcc2fe4d-stop_line_dist.json'))
PT=json.load(open('/mnt/user-data/uploads/point.geojson'))
XY={f['properties']['id']:tuple(f['geometry']['coordinates']) for f in PT['features']}
D=json.load(open('stop_gr.json'))['อังคาร']
V=40000/60.0;DW=20/60.0
LINES=['แดง','เหลือง']
def on(l,s): return SD[str(s)][l]<=30
def loop_off(l,rev=False):
    L=RP[l]['length'];p0=RP[l]['pos']['0'][1]
    st=[s for s in range(1,27) if str(s) in SD and on(l,s)]
    key=lambda s:((p0-RP[l]['pos'][str(s)][1])%L if rev else (RP[l]['pos'][str(s)][1]-p0)%L)
    st.sort(key=key);return {s:key(s)/V+DW*i for i,s in enumerate(st)}
LOFF={l:loop_off(l) for l in LINES}
def euclid(a,b):return math.hypot(XY[a][0]-XY[b][0],XY[a][1]-XY[b][1])
def seq_off(seq):
    t=0;prev=0;o={}
    for i,s in enumerate(seq):
        t+=euclid(prev,s)/V+ (DW if i>0 else 0);o[s]=t;prev=s
    return o
def veh_loop(t,l,cap=20): return dict(t=t,stops=dict(LOFF[l]),cap=cap)
def veh_from_row(r):
    k=(r['rt'] or r['t']).split(':');t=int(k[0])*60+float(k[1])
    if r['type'] in('loop-r','loop-y'): return veh_loop(t,'แดง' if r['type']=='loop-r' else 'เหลือง')
    stops=[int(x) for x in re.findall(r'P(\d+)',r['label'])];stops=[s for s in stops if s!=0]
    if '←' in r['label']: stops=stops[::-1]
    return dict(t=t,stops=seq_off(stops),cap=r['cap'])
def old_vehicles(mr=0,my=5):
    v=[]
    for h in range(7,19):
        if h<18:
            for k in range(6):
                v.append(veh_loop(h*60+mr+10*k,'แดง'));v.append(veh_loop(h*60+my+10*k,'เหลือง'))
        else:
            for k in range(5): v.append(veh_loop(h*60+12*k,'แดง'))
            for k in range(4): v.append(veh_loop(h*60+5+15*k,'เหลือง'))
    return v
def sim_return(veh,dem,w0,w1,step=0.5):
    q={s:[] for s in dem};n=int(round((w1-w0)/step))
    for s,m in dem.items():
        for i in range(n):q[s].append([w0+(i+.5)*step,m/n])
    ev=sorted((v['t']+o,vi,s) for vi,v in enumerate(veh) for s,o in v['stops'].items() if s in dem)
    onb={};ptr={s:0 for s in dem};W=[]
    for t,vi,s in ev:
        free=veh[vi]['cap']-onb.get(vi,0)
        while free>1e-9 and ptr[s]<len(q[s]) and q[s][ptr[s]][0]<=t:
            a,m=q[s][ptr[s]];take=min(m,free);W.append((t-a,take,0));free-=take;onb[vi]=onb.get(vi,0)+take
            if take<m-1e-12:q[s][ptr[s]][1]=m-take
            else:ptr[s]+=1
    left=sum(m for s in q for a,m in q[s][ptr[s]:]);return W,left
def sim_going(veh,dem,w0,w1,start,step=0.5):
    n=int(round((w1-w0)/step));P=[]
    for s,m in dem.items():
        for i in range(n):P.append([w0+(i+.5)*step,s,m/n])
    P.sort(key=lambda x:x[0]);W=[]
    for vi,v in sorted(enumerate(veh),key=lambda x:x[1]['t']):
        free=v['cap']
        for p in P:
            if free<=1e-9:break
            if p[0]>v['t'] or p[2]<=1e-12 or p[1] not in v['stops']:continue
            take=min(p[2],free);late=1 if v['t']+v['stops'][p[1]]>start else 0
            W.append((v['t']-p[0],take,late));p[2]-=take;free-=take
    left=sum(p[2] for p in P);return W,left
def evaluate(veh):
    allW=[];left=0;per={}
    for h in range(7,21):
        key=str(h)
        if key in D:
            g={int(s):v[0] for s,v in D[key].items() if v[0]>0.05}
            r={int(s):v[1] for s,v in D[key].items() if v[1]>0.05}
            if r:
                W,l=sim_return(veh,r,h*60,h*60+15);per[('ret',h)]=(sum(r.values()),W,l)
            if g:
                W,l=sim_going(veh,g,h*60-30,h*60-15,h*60);per[('go',h)]=(sum(g.values()),W,l)
    return per
def summarize(per,kinds=None,hours=None):
    W=[];tot=0;left=0
    for (k,h),(n,w,l) in per.items():
        if kinds and k not in kinds:continue
        if hours and h not in hours:continue
        W+=w;tot+=n;left+=l
    if not W:return None
    a=np.array([x[0] for x in W]);m=np.array([x[1] for x in W]);late=np.array([x[2] for x in W])
    o=np.argsort(a);a2=a[o];m2=m[o];c=np.cumsum(m2)/m2.sum()
    return dict(n=tot,served=m.sum(),left=left,mean=(a*m).sum()/m.sum(),p90=a2[np.searchsorted(c,.9)],late=(late*m).sum()/m.sum())
if __name__=='__main__':
    T=json.load(open('full_tt.json'))
    systems={'old141':old_vehicles(0,5),'base67':[veh_from_row(r) for r in T['base']],'alt75':[veh_from_row(r) for r in T['peak12']]}
    for name,veh in systems.items():
        per=evaluate(veh)
        print('===',name,'vehicles',len(veh))
        for kinds,label in((('ret',),'returns'),(('go',),'going'),(('ret','go'),'all')):
            s=summarize(per,kinds)
            print(f"  {label:8s} n={s['n']:.0f} served={s['served']:.0f} unserved={s['left']:.1f} mean={s['mean']:.1f} p90={s['p90']:.1f}"+(f" late={s['late']*100:.0f}%" if 'go' in kinds else ''))
        for (k,h),(n,W,l) in sorted(per.items(),key=lambda x:(x[0][1],x[0][0])):
            if n<20: continue
            a=np.array([x[0] for x in W]);m=np.array([x[1] for x in W])
            print(f"    {k} {h:02d}:00 n={n:5.1f} mean={(a*m).sum()/m.sum():5.1f} unserved={l:.1f}")
