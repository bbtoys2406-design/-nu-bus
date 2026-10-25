import sys;sys.path.insert(0,'.')
from tdat import *
tmin=min(trips_new.values());tmax=max(trips_new.values())
uo=[UTIL_OLD[d]*100 for d in DAYS];un=[UTIL_NEW[d]*100 for d in DAYS]
th=f"""## บทคัดย่อ

งานวิจัยเรื่อง การวิเคราะห์ความต้องการและแนวคิดการจัดสัดส่วนรถรับส่งตามปริมาณความต้องการนักศึกษา: กรณีศึกษาระบบรถไฟฟ้ามหาวิทยาลัยนเรศวร มีวัตถุประสงค์เพื่อ (1) ประมาณความต้องการใช้รถรับส่งรายจุดจอดและรายชั่วโมงจากตารางเรียนและตำแหน่งอาคาร และ (2) เสนอแนวทางกำหนดเที่ยวรถตามความต้องการรายช่วงเวลา แล้วเปรียบเทียบกับตารางเดินรถปัจจุบันของมหาวิทยาลัยด้วยแบบจำลอง

ข้อมูลที่ใช้เป็นข้อมูลทุติยภูมิ ได้แก่ ตารางเรียนภาคเรียนที่ 1 วันจันทร์ถึงศุกร์ 4,260 รายการ อาคาร 40 รายการ จุดจอด 26 จุด (รวมจุดหอพัก P0) และเส้นทางสายสีแดงและสายสีเหลือง ผู้วิจัยจับคู่อาคารกับจุดจอดที่ใกล้ที่สุดด้วยระบบสารสนเทศภูมิศาสตร์ (GIS) กำหนดกลุ่มผู้ใช้ในแบบจำลอง 561 คน (นิสิตหอใน 1,696 คน หักด้วยที่จอดรถจักรยานยนต์ 1,135 คัน ซึ่งเป็นสมมติฐานของแบบจำลอง) ปรับสเกลความต้องการให้รวมสัปดาห์ละ {n0(UNR)} เที่ยวคนก่อนปัดเศษ และปัดจำนวนคนขึ้นเป็นจำนวนเต็มในทุกจุดจอดทุกชั่วโมง ทำให้รวมสัปดาห์ละ {n0(WEEK)} เที่ยวคน จากนั้นออกแบบตารางเที่ยวรถภายใต้รถ 21 คัน (รถส้ม 35 ที่นั่ง 16 คัน และรถกอล์ฟ 11 ที่นั่ง 5 คัน) โดยใช้กฎรถวนเส้นทางในช่วงกลางวัน และการจัดเส้นทางยานพาหนะที่มีข้อจำกัดความจุ (CVRP) ด้วยวิธี Clarke–Wright ในช่วงเช้าและเย็น และประเมินเวลารอด้วยแบบจำลองการไหลของผู้โดยสาร

ผลการวิจัยพบว่า ความต้องการกระจุกตัวที่ชั่วโมง 12:00–12:59 น. คิดเป็นร้อยละ {f1(H12/WEEK*100)} ของทั้งสัปดาห์ ({n0(H12)} เที่ยวคน) และจุดจอด P16 กับ P26 รวมกันร้อยละ {f1(TOP2/WEEK*100)} ตารางที่ออกแบบใหม่ใช้ {tmin}–{tmax} เที่ยวต่อวัน เทียบกับ {TRIPS_OLD} เที่ยวของตารางปัจจุบัน (ลดลงราวร้อยละ {f1((1-TRIPS_NEW_WEEK/TRIPS_OLD_WEEK)*100)}) โดยไม่เพิ่มจำนวนรถ และเพิ่มสัดส่วนเที่ยวคนต่อที่นั่งที่เสนอจากร้อยละ {f1(min(uo))}–{f1(max(uo))} เป็นร้อยละ {f1(min(un))}–{f1(max(un))} อย่างไรก็ตาม เวลารอเฉลี่ยของแบบจำลองสูงขึ้นจาก {f1(wavg('old'))} เป็น {f1(wavg('new'))} นาที (P90 จาก {f1(min(P90['old']))}–{f1(max(P90['old']))} เป็น {f1(min(P90['new']))}–{f1(max(P90['new']))} นาที) งานวิจัยจึงสรุปได้เพียงว่าแบบจำลองแสดงการแลกกันระหว่างจำนวนเที่ยวกับเวลารอ ไม่ได้แสดงว่าตารางใหม่ดีกว่าในทุกด้าน นอกจากนี้ ไม่สามารถแบ่งสัดส่วนรถสายสีแดงและสายสีเหลืองตามความต้องการได้ เพราะความต้องการร้อยละ {f1(SPLIT['both']/SPLIT['total']*100)} อยู่ที่จุดจอดที่อยู่ติดทั้งสองสาย ผลทั้งหมดเป็นผลจากแบบจำลอง ไม่ใช่ผลจากการนับผู้โดยสารจริง

**คำสำคัญ:** ความต้องการเดินทาง, รถรับส่งในมหาวิทยาลัย, การจัดสัดส่วนรถ, ปัญหาการจัดเส้นทางยานพาหนะที่มีข้อจำกัดความจุ (CVRP), ระบบสารสนเทศภูมิศาสตร์

## Abstract

This study, "Demand Analysis and Fleet-Ratio Concept for Campus Shuttle System: A Case Study of Naresuan University", (1) estimates shuttle demand by stop and by hour from the class timetable and building locations, and (2) proposes a trip timetable matched to hourly demand and compares it with the university's current timetable by simulation.

Secondary data were used: 4,260 class records of the first semester (Monday to Friday), 40 buildings, 26 stops (including the dormitory stop P0) and the red and yellow routes. Buildings were matched to their nearest stops with GIS. The modelled rider group was set at 561 students (1,696 dormitory residents minus 1,135 motorcycle parking spaces, a modelling assumption). Demand was scaled to {n0(UNR)} person-trips per week before rounding; people were then rounded up to whole numbers for every stop-hour-direction cell, giving {n0(WEEK)} person-trips per week. Trips were designed with 21 vehicles (16 buses of 35 seats and 5 golf carts of 11 seats): a loop rule at midday, and a capacitated vehicle routing problem (CVRP, Clarke–Wright savings) in the morning and evening. Waiting time was evaluated with a passenger-flow simulation.

Demand concentrates in the 12:00–12:59 hour ({f1(H12/WEEK*100)}% of the week, {n0(H12)} person-trips), and stops P16 and P26 together carry {f1(TOP2/WEEK*100)}%. The new timetable needs {tmin}–{tmax} trips a day against {TRIPS_OLD} in the current timetable (about {f1((1-TRIPS_NEW_WEEK/TRIPS_OLD_WEEK)*100)}% fewer) with no additional vehicles, and raises person-trips per offered seat from {f1(min(uo))}–{f1(max(uo))}% to {f1(min(un))}–{f1(max(un))}%. However, the simulated mean waiting time rises from {f1(wavg('old'))} to {f1(wavg('new'))} minutes (90th percentile from {f1(min(P90['old']))}–{f1(max(P90['old']))} to {f1(min(P90['new']))}–{f1(max(P90['new']))} minutes). The model therefore shows a trade-off between the number of trips and waiting time; it does not show that the new timetable is better in every respect. The fleet cannot be split between the red and yellow routes by demand, because {f1(SPLIT['both']/SPLIT['total']*100)}% of demand is at stops served by both routes. All results come from the model, not from counts of actual passengers.

**Keywords:** travel demand, campus shuttle, fleet allocation, capacitated vehicle routing problem (CVRP), geographic information system (GIS)
"""
open('md/s1.md','w').write(th);print(th)
