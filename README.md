# NongGame - Typing Farmer

เกมปลูกผักด้วยการพิมพ์คำศัพท์ให้ถูกต้อง สร้างด้วย Python และ Pygame

## ✅ ฟีเจอร์หลัก

* **Typing Challenge:** พิมพ์คำศัพท์ที่สุ่มมาให้ถูกต้องและรวดเร็ว
* **Time Limit:** มีเวลาจำกัดในแต่ละคำ เพิ่มความท้าทาย
* **Score & Combo:** ยิ่งพิมพ์ถูกติดต่อกันมากเท่าไหร่ คะแนนยิ่งพุ่งกระฉูด
* **Planting Animation:** ทุกครั้งที่พิมพ์สำเร็จ จะมีอนิเมชันการปลูกผักเพื่อเป็นรางวัล
* **Sound Effects & BGM:** เพิ่มอรรถรสในการเล่น
* **Modern UI:** หน้าจอสวยงาม สบายตา ธีมสวนผัก

## 🔧 การติดตั้ง (Installation)

1.  Clone a repository หรือดาวน์โหลดไฟล์ทั้งหมดลงในเครื่องของคุณ
2.  ตรวจสอบว่าคุณมี Python 3.8+ ติดตั้งอยู่
3.  ติดตั้งไลบรารีที่จำเป็นผ่าน `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
4.  **(สำคัญ)** หาไฟล์ Assets ต่างๆ มาใส่ในโฟลเดอร์ `assets/` ให้ครบ:
    * `assets/fonts/Kanit-Regular.ttf` (หรือฟอนต์ภาษาไทยอื่นๆ)
    * `assets/sounds/typing.wav`, `success.wav`, `error.wav`, `bgm.mp3`
    * `assets.images/vegetable_animation/` (หากต้องการอนิเมชันแบบรูปภาพ)

## 🎮 วิธีการเล่น

1.  เข้าไปที่โฟลเดอร์ `src`
2.  รันไฟล์ `main.py` เพื่อเริ่มเกม:
    ```bash
    python main.py
    ```
3.  พิมพ์คำศัพท์ที่ปรากฏบนหน้าจอให้ถูกต้องและทันเวลา!

## 🧩 โครงสร้างโปรเจกต์

โปรเจกต์นี้ใช้หลักการ Object-Oriented Programming (OOP) เพื่อให้ง่ายต่อการแก้ไขและต่อยอด

* `main.py`: จุดเริ่มต้นของโปรแกรม
* `game_manager.py`: คลาสหลัก ควบคุม Game Loop และสถานะของเกม
* `word_manager.py`: จัดการการโหลดและสุ่มคำศัพท์
* `input_box.py`: จัดการกล่องรับข้อความจากผู้เล่น
* `score_manager.py`: จัดการคะแนนและระบบคอมโบ
* `money_manager.py`: จัดการค่าเงินในเกม
* `sound_manager.py`: จัดการเสียงและดนตรี
* `ui.py`: รับผิดชอบการวาด UI ทั้งหมด