# NongGameTyping/src/game_manager.py
import pygame
import sys
import json
import os
from .word_manager import WordManager
from .input_box import InputBox
from .combo_manager import ComboManager
from .money_manager import MoneyManager
from .sound_manager import SoundManager
from .ui import UIManager
from .shop_screen import ShopScreen

class GameManager:
    """
    คลาสหลักที่ควบคุม Game Loop, State, และการทำงานร่วมกันของ Manager ต่างๆ
    """
    def __init__(self, setting_path='setting/setting.json'):
        # โหลดค่าตั้งค่าจากไฟล์
        with open(setting_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.SCREEN_WIDTH = config.get('screen_width', 1280)
        self.SCREEN_HEIGHT = config.get('screen_height', 720)
        self.FPS = config.get('fps', 60)
        self.MAX_TIME_PER_WORD = config.get('max_time_per_word', 20)
        self.growth_on_success = config.get('growth_on_success', 0.15)
        self.growth_on_error = config.get('growth_on_error', -0.05)
        self.growth_timer_interval = config.get('growth_timer_interval', 5.0)
        self.growth_per_interval = config.get('growth_per_interval', 0.01)
        self.coins_per_growth = config.get('coins_per_growth', 5)

        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("NongGame - Typing Farmer")
        self.clock = pygame.time.Clock()

        self.ui_manager = UIManager(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.word_manager = WordManager('../data/word.json')
        self.combo_manager = ComboManager()
        self.money_manager = MoneyManager()
        self.sound_manager = SoundManager()

        input_box_w = 600
        input_box_h = 65
        input_box_x = (self.SCREEN_WIDTH - input_box_w) / 2
        input_box_y = self.SCREEN_HEIGHT / 2
        self.input_box = InputBox(input_box_x, input_box_y, input_box_w, input_box_h, self.ui_manager.font_medium)

        self.running = True
        self.timer = self.MAX_TIME_PER_WORD
        self.plant_growth = 0.0  # 0.0 ถึง 1.0
        self.growth_timer = 0.0  # สำหรับนับเวลา 5 วิ
        self.scene = "game"  # เพิ่มตัวแปร scene
        self.shop_screen = ShopScreen(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.ui_manager.font_large, self.close_shop)
        # ปุ่มร้านค้า (มุมล่างขวา)
        self.shop_button_rect = pygame.Rect(self.SCREEN_WIDTH-140, self.SCREEN_HEIGHT-80, 120, 56)

    def reset_round(self, is_error=False):
        if is_error:
            self.sound_manager.play_sfx('error')
            # หา index ตัวแรกที่ผิด
            current_input = self.input_box.text
            target_word = self.word_manager.current_word
            wrong_index = None
            for i, c in enumerate(current_input):
                if i >= len(target_word) or c.upper() != target_word[i].upper():
                    wrong_index = i
                    break
            if wrong_index is not None:
                # คำนวณตำแหน่งตัวอักษรผิด
                x = self.SCREEN_WIDTH // 2
                y = self.SCREEN_HEIGHT // 2
                char_spacing = 80
                char_x = x - (len(target_word)-1) * char_spacing // 2 + wrong_index * char_spacing
                char_y = y
                self.ui_manager.trigger_error_effect(char_x, char_y)
            else:
                self.ui_manager.trigger_error_effect()  # fallback กลางจอ
            self.combo_manager.reset_combo()
            self.plant_growth = max(0.0, self.plant_growth + self.growth_on_error)
        self.word_manager.get_new_word()
        self.input_box.reset()
        self.timer = self.MAX_TIME_PER_WORD

    def handle_success(self):
        self.combo_manager.increment_combo()
        self.ui_manager.trigger_success_effect()
        self.plant_growth = min(1.0, self.plant_growth + self.growth_on_success * self.combo_manager.get_combo_multiplier())
        self.sound_manager.play_sfx('success')
        self.reset_round(is_error=False)

    def open_shop(self):
        self.scene = "shop"

    def close_shop(self):
        self.scene = "game"

    def run(self):
        self.sound_manager.play_bgm()
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0
            # อัปเดต timer เฉพาะตอนอยู่ในเกมหลัก
            if self.scene == "game":
                self.timer -= dt
                self.growth_timer += dt
                if self.growth_timer >= self.growth_timer_interval:
                    self.growth_timer = 0.0
                    if self.plant_growth < 1.0:
                        self.plant_growth = min(1.0, self.plant_growth + 0.01 * self.combo_manager.combo)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.scene == "game":
                    # handle shop button click
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.shop_button_rect.collidepoint(event.pos):
                            self.open_shop()
                            continue
                    if self.input_box.handle_event(event):
                        self.sound_manager.play_sfx('typing')
                        current_input = self.input_box.text
                        target_word = self.word_manager.current_word
                        if not target_word.startswith(current_input):
                            self.reset_round(is_error=True)
                elif self.scene == "shop":
                    if self.shop_screen.handle_event(event):
                        continue
            if self.scene == "game":
                self.input_box.update()
                if self.input_box.text == self.word_manager.current_word:
                    self.handle_success()
                if self.timer <= 0:
                    self.reset_round(is_error=True)
                if self.plant_growth >= 1.0:
                    self.money_manager.add_coins(self.coins_per_growth)
                    self.plant_growth = 0.0
                game_state = {
                    'current_word': self.word_manager.current_word,
                    'input_box': self.input_box,
                    'combo_manager': self.combo_manager,
                    'timer': self.timer,
                    'max_time': self.MAX_TIME_PER_WORD,
                    'plant_growth': self.plant_growth,
                    'money_manager': self.money_manager
                }
                self.ui_manager.draw_all(self.screen, game_state)
                # วาดปุ่มร้านค้า
                self.ui_manager.draw_shop_button(self.screen, self.shop_button_rect)
            elif self.scene == "shop":
                self.shop_screen.update(dt)
                self.shop_screen.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
        sys.exit()