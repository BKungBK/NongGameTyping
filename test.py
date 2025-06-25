import pygame

# เริ่มต้น Pygame
pygame.init()

# ตั้งค่าหน้าจอ
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Health Bar Example")

# สี
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Health Bar Parameters
player_max_hp = 100
player_current_hp = 100 # เริ่มต้นที่ HP เต็ม

# ตำแหน่งและขนาดของกรอบ Health Bar
bar_x = 50
bar_y = 50
bar_width = 300
bar_height = 30
bar_border_thickness = 3

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player_current_hp -= 10 # ลด HP เมื่อกด Spacebar
                if player_current_hp < 0:
                    player_current_hp = 0

    # เคลียร์หน้าจอ
    screen.fill(BLACK)

    # --- วาด Health Bar ---

    # 1. วาดกรอบ Health Bar
    # ใช้ pygame.draw.rect() สำหรับกรอบภายนอก (สีดำ)
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), bar_border_thickness)

    # 2. คำนวณความกว้างของหลอด HP ปัจจุบัน
    # ตรวจสอบให้แน่ใจว่า player_max_hp ไม่เป็น 0 เพื่อป้องกันการหารด้วยศูนย์
    if player_max_hp > 0:
        health_ratio = player_current_hp / player_max_hp
        current_bar_width = int(bar_width * health_ratio) # ใช้ int() เพราะขนาดพิกเซลต้องเป็นจำนวนเต็ม
    else:
        current_bar_width = 0 # ถ้า Max HP เป็น 0 ก็ให้ Bar กว้าง 0

    # 3. วาดหลอด HP ข้างใน
    # ใช้ pygame.Rect() เพื่อความสะดวกในการจัดการตำแหน่งและขนาด
    # ตำแหน่งของหลอด HP จะอยู่ถัดจากกรอบเข้ามาเล็กน้อย (ตาม bar_border_thickness)
    # แต่ถ้าเราต้องการให้หลอด HP เริ่มต้นที่มุมซ้ายบนของกรอบด้านในพอดี
    # เราสามารถกำหนดตำแหน่ง (bar_x + bar_border_thickness, bar_y + bar_border_thickness)
    # และลดขนาดความกว้าง/สูงของกรอบลงตามความหนาของเส้นขอบ (bar_width - 2*bar_border_thickness)
    # แล้วคำนวณความกว้างของแถบด้านในจากนั้น

    # หรือวิธีที่ง่ายกว่าและตรงไปตรงมาคือ: วาดหลอด Health ที่ตำแหน่ง bar_x, bar_y
    # แล้วใช้ความกว้างที่คำนวณได้ current_bar_width
    health_bar_rect = pygame.Rect(bar_x, bar_y, current_bar_width, bar_height)
    pygame.draw.rect(screen, GREEN, health_bar_rect)


    # อัปเดตหน้าจอ
    pygame.display.flip()

    # ควบคุม FPS
    clock.tick(60)

pygame.quit()