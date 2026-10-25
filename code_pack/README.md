# โค้ดที่ใช้ทำผลในเล่ม (ฐาน B: 561 คน x 2 เที่ยว = 1,122 ครั้ง/วัน)
ลำดับการรัน (สคริปต์ส่วนใหญ่ใช้ path เต็มของเครื่องผม ตัวแปร SP ต้นไฟล์ — แก้ก่อนรันในเครื่องอื่น):
1. scratchB/v4_new.html  = เว็บแบบจำลองที่สร้างความต้องการและตารางที่เสนอ (ต้นแบบเว็บ)
2. th/extract.py   -> base.json (ดึงตาราง/ความต้องการจากเว็บ ปัดขึ้นเปิด/ปิด)  [ใช้ playwright]
3. th/results1.py  -> page.json ; results1b.py
4. th/results2.py  -> results.json (ความต้องการ, ตาราง, เวลารอ 5 วัน, ความไว)
5. th/results3.py, results4.py
6. th/results5.py  -> results5.json (4 ตาราง x 5 วัน x ช่วงมาถึง 31-30 และ 45-30 นาที, ถูกข้าม, ที่นั่ง)
7. th/results6.py, results7.py, passup.py, xc.py (ตรวจสอบข้าม), check_wait.py, unit_tests.py
8. th/figs.py, figs4.py  -> ภาพ 4.x ; build_p3/p4/p5.py, ch3_tabs.py, p4data.py = ตารางในเล่ม
9. docbuild/build.py = สร้างไฟล์ Word ทรงคณะจากเอกสาร Docs ที่ export เป็น docx
แบบจำลองรอเวลา: th/wsim.py + scratchB/fullday.py (ของไหล FIFO, รถ 40 กม./ชม., จอด 20 วินาที)
ข้อมูลดิบอยู่ที่ inputs/ (point.geojson, road.geojson, build_nu.geojson, schedule.xlsx, bus.csv, stop_line_dist.json)
