import json,math,collections,statistics
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import unary_union, transform
SP='/tmp/claude-0/-home-claude/5d08b61f-0d0d-5ed9-b111-61441aa95e91/scratchB/th/'
P=json.load(open(SP+'page.json'));b2s=P['b2s']
pt=json.load(open('/mnt/user-data/uploads/point.geojson'));bd=json.load(open('/mnt/user-data/uploads/build_nu.geojson'))
stops={f['properties']['id']:tuple(f['geometry']['coordinates']) for f in pt['features']}
tr=Transformer.from_crs('EPSG:4326','EPSG:32647',always_xy=True)
groups=collections.defaultdict(list)
for f in bd['features']:
    groups[f['properties']['name']].append(shape(f['geometry']))
res={}
for name,geoms in groups.items():
    u=unary_union(geoms);c=transform(lambda x,y,z=None:tr.transform(x,y),u).centroid
    ds=sorted((math.hypot(c.x-xy[0],c.y-xy[1]),sid) for sid,xy in stops.items() if sid!=0)
    res[name]=dict(n=len(geoms),near=ds[0][1],d1=ds[0][0],second=ds[1][1],d2=ds[1][0])
print('names in geojson',len(groups),'rows',sum(len(v) for v in groups.values()))
print('names in b2s',len(b2s))
miss=[n for n in b2s if n not in res and n not in('หอใน','จุดเริิ่มเส้นทาง')]
print('b2s names not in geojson:',miss)
print('geojson names not in b2s:',[n for n in res if n not in b2s])
diff=[];ds=[];close=[]
for n,s in b2s.items():
    if n in res:
        r=res[n]
        if n in('หอใน','จุดเริิ่มเส้นทาง'): continue
        ds.append(r['d1'])
        if r['near']!=s: diff.append((n,s,r['near'],round(r['d1']),r['second'],round(r['d2'])))
        if r['d2']-r['d1']<=20: close.append((n,round(r['d2']-r['d1'],1)))
print('matched names compared',len(ds),'median',round(statistics.median(ds)),'min',round(min(ds)),'max',round(max(ds)))
print('DIFF vs embedded:',diff)
print('second within 20 m:',len(close),close)
json.dump(res,open(SP+'geo_res.json','w'),ensure_ascii=False)
