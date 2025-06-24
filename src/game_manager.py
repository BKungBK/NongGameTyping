# NongGameTyping/src/game_manager.py
import pygame
import sys
from .word_manager import WordManager
from .input_box import InputBox
from .score_manager import ScoreManager
from .money_manager import MoneyManager
from .sound_manager import SoundManager
from .ui import UIManager

class GameManager:
    """
    คลาสหลักที่ควบคุม Game Loop, State, และการทำงานร่วมกันของ Manager ต่างๆ
    """
    def __init__(self, screen_width=1280, screen_height=720):
        pygame.init()
        # --- ค่าตั้งต้นเกม ---
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.FPS = 60
        self.MAX_TIME_PER_WORD = 20 # เวลา 5 วินาทีต่อคำ

        # --- ตั้งค่าหน้าจอและเวลา ---
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("NongGame - Typing Farmer")
        self.clock = pygame.time.Clock()

        # --- สร้าง Manager ต่างๆ ---
        self.ui_manager = UIManager(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.word_manager = WordManager('../data/word.json')
        self.score_manager = ScoreManager()
        self.money_manager = MoneyManager()
        self.sound_manager = SoundManager()
        
        # --- สร้าง Input Box ---
        input_box_w = 600
        input_box_h = 65
        input_box_x = (self.SCREEN_WIDTH - input_box_w) / 2
        input_box_y = self.SCREEN_HEIGHT / 2
        self.input_box = InputBox(input_box_x, input_box_y, input_box_w, input_box_h, self.ui_manager.font_medium)
        
        # --- ตัวแปรสถานะเกม ---
        self.running = True
        self.timer = self.MAX_TIME_PER_WORD
        self.plant_growth = 0.0  # 0.0 ถึง 1.0
        self.growth_on_success = 0.15
        self.growth_on_error = -0.05
        self.growth_timer = 0.0  # สำหรับนับเวลา 5 วิ

    def reset_round(self, is_error=False):
        """รีเซ็ตคำ, input, และ timer สำหรับรอบใหม่"""
        if is_error:
            self.ui_manager.trigger_error_effect(color=(255, 0, 0, 128)) 
            self.score_manager.reset_combo()
            self.sound_manager.play_sfx('error')
            self.plant_growth = max(0.0, self.plant_growth + self.growth_on_error)
        
        self.word_manager.get_new_word()
        self.input_box.reset()
        self.timer = self.MAX_TIME_PER_WORD

    def handle_success(self):
        """จัดการเมื่อพิมพ์คำถูกต้อง"""
        self.score_manager.add_score()
        self.plant_growth = min(1.0, self.plant_growth + self.growth_on_success)
        self.sound_manager.play_sfx('success')
        self.ui_manager.trigger_success_effect()
        self.reset_round(is_error=False)

    def run(self):
        """Game Loop หลัก"""
        self.sound_manager.play_bgm()
        
        while self.running:
            # --- จัดการเวลา (Delta Time) ---
            dt = self.clock.tick(self.FPS) / 1000.0
            self.timer -= dt
            # โตเอง 1% ทุก 5 วินาที
            self.growth_timer += dt
            if self.growth_timer >= 5.0:
                self.growth_timer = 0.0
                if self.plant_growth < 1.0:
                    self.plant_growth = min(1.0, self.plant_growth + 0.01)

            # --- จัดการ Event ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # ส่ง event ไปให้ input_box จัดการ
                if self.input_box.handle_event(event):
                    self.sound_manager.play_sfx('typing')
                    # ตรวจสอบทันทีหลังพิมพ์
                    current_input = self.input_box.text
                    target_word = self.word_manager.current_word
                    
                    # ถ้าพิมพ์ผิดแม้แต่ตัวเดียว (ไม่ใช่ส่วนหนึ่งของคำที่ถูกต้อง)
                    if not target_word.startswith(current_input):
                        print("Typo error!")
                        self.reset_round(is_error=True)

            # --- อัปเดตสถานะเกม ---
            self.input_box.update()

            # ตรวจสอบว่าพิมพ์สำเร็จหรือไม่
            if self.input_box.text == self.word_manager.current_word:
                self.handle_success()
            
            # ตรวจสอบว่าเวลาหมดหรือไม่
            if self.timer <= 0:
                print("Time out!")
                self.reset_round(is_error=True)

            # --- ได้เงินและรีเซ็ตต้นไม้ทันทีเมื่อครบ 100% ---
            if self.plant_growth >= 1.0:
                self.money_manager.add_coins(5)
                self.plant_growth = 0.0

            # --- วาดทุกอย่างลงบนหน้าจอ ---
            game_state = {
                'current_word': self.word_manager.current_word,
                'input_box': self.input_box,
                'score_manager': self.score_manager,
                'timer': self.timer,
                'max_time': self.MAX_TIME_PER_WORD,
                'plant_growth': self.plant_growth,
                'money_manager': self.money_manager
            }
            self.ui_manager.draw_all(self.screen, game_state)
            
            # --- อัปเดตหน้าจอ ---
            pygame.display.flip()

        # --- จบเกม ---
        pygame.quit()
        sys.exit()