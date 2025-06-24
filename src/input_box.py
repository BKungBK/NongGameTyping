# NongGameTyping/src/input_box.py
import pygame as pg

class InputBox:
    """กล่องรับข้อความจากผู้เล่น"""
    def __init__(self, x, y, w, h, font):
        self.rect = pg.Rect(x, y, w, h)
        self.color = (255, 255, 255)
        self.text = ''
        self.font = font
        self.txt_surface = self.font.render('', True, (60, 60, 60))
        self.active = True # เริ่มมาให้พิมพ์ได้เลย

    def handle_event(self, event):
        """จัดการกับ event การพิมพ์"""
        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode.lower()
            # อัปเดตพื้นผิวข้อความทุกครั้งที่มีการเปลี่ยนแปลง
            self.txt_surface = self.font.render(self.text, True, (60, 60, 60))
            return True # คืนค่าว่ามีการพิมพ์เกิดขึ้น
        return False

    def update(self):
        """อัปเดตความกว้างของกล่องข้อความ (ถ้าต้องการ)"""
        # สามารถเพิ่มโค้ดให้กล่องขยายตามข้อความได้ตรงนี้
        pass

    def draw(self, screen):
        """วาดกล่องข้อความและตัวอักษรลงบนหน้าจอ"""
        # วาดพื้นหลังของ input box
        pg.draw.rect(screen, self.color, self.rect, 0, 15) # boader radius 15
        # วาดกรอบ
        pg.draw.rect(screen, (200, 200, 200), self.rect, 2, 15)
        # วาดข้อความ
        screen.blit(self.txt_surface, (self.rect.x + 15, self.rect.y + (self.rect.h - self.txt_surface.get_height()) / 2))

    def reset(self):
        """รีเซ็ตข้อความในกล่อง"""
        self.text = ''
        self.txt_surface = self.font.render('', True, (60, 60, 60))