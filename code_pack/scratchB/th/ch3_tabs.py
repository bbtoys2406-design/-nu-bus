import json,collections
from tdat import *
G=json.load(open(SP+'geo_res.json'))
cov=P['coverage']
wk=cov['wk'];mw=cov['matchedWk'];ew=cov['enrW'];em=cov['enrM']
print('### COVERAGE')
print(md_table(['รายการ','ช่วงเรียน','ที่นั่งลงทะเบียน'],[
 ['ช่วงเรียนวันจันทร์–ศุกร์ทั้งหมด',n0(wk),n0(ew)],
 ['จับคู่กับจุดจอดได้ (ใช้ในแบบจำลอง)',f"{n0(mw)} ({pc(mw/wk)})",f"{n0(em)} ({pc(em/ew)})"],
 ['จับคู่ไม่ได้ (ตัดออก ไม่ถ่วงน้ำหนักชดเชย)',f"{n0(wk-mw)} ({pc((wk-mw)/wk)})",f"{n0(ew-em)} ({pc((ew-em)/ew)})"]]))
print('by day',{d:cov['byDay'][d] for d in DAYS},'sum',sum(cov['byDay'][d] for d in DAYS))
u=cov['unm']
grp=[('ห้องที่ระบุว่า "ติดต่อผู้สอน"',['ติดต่อผู้สอน']),('LDSC',['LDSC']),('Shop / shop',['Shop','shop']),('LAB / Lab / Lab.',['LAB','Lab','Lab.']),('H',['H']),('โถงกิจกรรมชั้น',['โถงกิจกรรมชั้น']),('อาคารกิจกรรม / ลานกิจกรรม',['อาคารกิจกรรม','ลานกิจกรรม']),('IDB',['IDB']),('สนามกีฬาในร่ม / วอลเลย์บอล / บาสเกตบอล',['สนามกีฬาในร่ม','สนามกีฬาวอลเลย์บอล','สนามกีฬาบาสเกตบอล']),('แปลงฝึกงาน',['แปลงฝึกงาน']),('สระว่ายน้ำ',['สระว่ายน้ำ']),('Online',['Online']),('ห้องเรียน (ไม่ระบุอาคาร)',['ห้องเรียน'])]
rows=[];tot=0
for name,ks in grp:
    c=sum(u[k] for k in ks);tot+=c;rows.append([name,n0(c),pc(c/(wk-mw))])
rows.sort(key=lambda r:-int(r[1].replace(',','')))
print('### UNMATCHED total',tot,wk-mw)
print(md_table(['กลุ่มรหัสห้อง','ช่วงเรียน','สัดส่วนของที่จับคู่ไม่ได้'],rows+[['รวม',n0(tot),'100.0%']]))
# b2s table
b2s=P['b2s'];by=collections.defaultdict(list)
close={n for n in b2s if n in G and n not in('หอใน','จุดเริิ่มเส้นทาง') and G[n]['d2']-G[n]['d1']<=20}
for n,s in b2s.items(): by[s].append(n)
rows=[]
for s in sorted(by):
    names=[]
    for n in sorted(by[s],key=lambda x:x.lower()):
        label=n.replace('จุดเริิ่มเส้นทาง','จุดเริ่มเส้นทาง')
        if n=='สนามฟุตบอล': label+='*†'
        elif n in close: label+='*'
        names.append(label)
    rows.append([('P0 (จุดต้นทาง)' if s==0 else f'P{s}'),', '.join(names),len(names)])
print('### B2S');print(md_table(['จุดจอด','อาคารหรือหน่วยงานที่จับคู่ (ชื่อตามไฟล์ขอบเขตอาคาร)','จำนวนชื่อ'],rows))
nostop=[s for s in [1,2,3,4]+list(range(6,27)) if s not in by]
print('stops without names','P'+', P'.join(map(str,nostop)),len(nostop))
print('stops with demand', sorted(int(k) for k in W['stop']))
# rounding per day
print('### ROUNDING')
rows=[];
for d in DAYS:
    a=R['unrounded_day_total'][d];b=R['demand'][d]['total'];rows.append([d,f1(a),n0(b),'+'+f1((b-a)/a*100)+'%'])
rows.append(['รวม 5 วัน',f1(UNR),n0(WEEK),'+'+f1((WEEK-UNR)/UNR*100)+'%'])
print(md_table(['วัน','ก่อนปัดเศษ (เที่ยวคน)','หลังปัดเศษขึ้น (เที่ยวคน)','ส่วนที่เพิ่ม'],rows))
print('cells',len([1 for d in DAYS for h,hv in cells_on[d]['cells'].items() for s,sv in hv.items() for k in('g','r') if sv[k]>0]))
