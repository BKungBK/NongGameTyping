# NongGameTyping/src/game_manager.py
import pygame
import sys
from .word_manager import WordManager
from .input_box import InputBox
from .combo_manager import ComboManager
from .money_manager import MoneyManager
from .sound_manager import SoundManager
from .ui import UIManager
from .gacha_ui_system import GachaOverlaySystem
from .collection_ui_system import CollectionOverlaySystem
from .data_manager import DataManager

class GameManager:
    """
    คลาสหลักที่ควบคุม Game Loop, State, และการทำงานร่วมกันของ Manager ต่างๆ
    """
    def __init__(self):
        # โหลดค่าตั้งค่าจาก DataManager
        self.data_manager = DataManager()
        config = self.data_manager.get_settings()
        
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

        # Initialize all managers with proper integration
        self.sound_manager = SoundManager()
        self.ui_manager = UIManager(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, sound_manager=self.sound_manager)
        self.word_manager = WordManager()
        self.combo_manager = ComboManager()
        self.money_manager = MoneyManager()  # This now loads from DataManager
        self.current_scene = "main"

        input_box_w = 600
        input_box_h = 65
        input_box_x = (self.SCREEN_WIDTH - input_box_w) / 2
        input_box_y = self.SCREEN_HEIGHT / 2
        self.input_box = InputBox(input_box_x, input_box_y, input_box_w, input_box_h, self.ui_manager.font_medium)

        self.running = True
        self.timer = self.MAX_TIME_PER_WORD
        self.plant_growth = 0.0  # 0.0 ถึง 1.0
        self.growth_timer = 0.0  # สำหรับนับเวลา 5 วิ
        self.gacha_overlay = None  # สำหรับ overlay กาชา
        self.collection_overlay = None  # สำหรับ overlay collection

        # Game statistics
        self.total_words_typed = config.get('total_words_typed', 0)
        self.total_coins_earned = config.get('total_coins_earned', 0)
        self.best_combo = config.get('best_combo', 0)

        self.load_autosave()  # โหลด autosave ถ้ามี
        self._autosave_timer = 0.0  # ตัวจับเวลา autosave

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
        
        # Update statistics
        self.total_words_typed += 1
        if self.combo_manager.combo > self.best_combo:
            self.best_combo = self.combo_manager.combo
        
        self.reset_round(is_error=False)

    def save_game_statistics(self):
        """บันทึกสถิติเกมลง DataManager"""
        settings = self.data_manager.get_settings()
        settings['total_words_typed'] = self.total_words_typed
        settings['total_coins_earned'] = self.total_coins_earned
        settings['best_combo'] = self.best_combo
        self.data_manager.update_settings(settings)

    def load_autosave(self):
        """โหลด autosave ถ้ามี"""
        data = self.data_manager.load_autosave()
        if data:
            self.money_manager.coins = data.get("coins", self.money_manager.coins)
            self.combo_manager.combo = data.get("combo", self.combo_manager.combo)
            self.plant_growth = data.get("plant_growth", self.plant_growth)

    def autosave(self):
        """บันทึก autosave"""
        self.data_manager.save_autosave(
            self.money_manager.coins,
            self.combo_manager.combo,
            self.plant_growth
        )

    def run(self):
        self.sound_manager.play_bgm()
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0
            self._autosave_timer += dt
            if self._autosave_timer >= 5.0:
                self._autosave_timer = 0.0
                self.autosave()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # --- ถ้ามี overlay กาชา ---
                if self.gacha_overlay is not None:
                    self.gacha_overlay.handle_event(event)
                    continue  # ไม่ส่ง event ให้ input/game หลัก

                # --- ถ้ามี overlay collection ---
                if self.collection_overlay is not None:
                    self.collection_overlay.handle_event(event)
                    continue  # ไม่ส่ง event ให้ input/game หลัก

                if self.current_scene == "main":
                    # Handle typing game events
                    if self.input_box.handle_event(event):
                        self.sound_manager.play_sfx('typing')
                        current_input = self.input_box.text
                        target_word = self.word_manager.current_word
                        if not target_word.startswith(current_input):
                            self.reset_round(is_error=True)
                    # Handle DiamondButton events
                    button_result = self.ui_manager.handle_event(event)
                    if button_result == "gacha":
                        # First button clicked -> open gacha
                        self.open_gacha_overlay()
                    elif button_result == "collection":
                        # Second button clicked -> open collection
                        self.open_collection_overlay()
                elif self.current_scene == "gacha":
                    pass

            # --- อัปเดต/วาด overlay กาชา ถ้ามี ---
            if self.gacha_overlay is not None:
                self.gacha_overlay.update(dt)
                # ตรวจสอบอีกครั้งหลังจาก update (อาจถูก set เป็น None ระหว่าง fade-out)
                if self.gacha_overlay is not None:
                    self.ui_manager.draw_background_image(self.screen)  # วาดพื้นหลังเกม
                    self.gacha_overlay.draw(self.screen)
                    pygame.display.flip()
                    continue  # ข้าม logic เกมหลัก (หยุดเวลา)

            # --- อัปเดต/วาด overlay collection ถ้ามี ---
            if self.collection_overlay is not None:
                self.collection_overlay.update(dt)
                # ตรวจสอบอีกครั้งหลังจาก update (อาจถูก set เป็น None ระหว่าง fade-out)
                if self.collection_overlay is not None:
                    self.ui_manager.draw_background_image(self.screen)  # วาดพื้นหลังเกม
                    self.collection_overlay.draw(self.screen)
                    pygame.display.flip()
                    continue  # ข้าม logic เกมหลัก (หยุดเวลา)

            if self.current_scene == "main":
                self.timer -= dt
                self.growth_timer += dt
                if self.growth_timer >= self.growth_timer_interval:
                    self.growth_timer = 0.0
                    if self.plant_growth < 1.0:
                        self.plant_growth = min(1.0, self.plant_growth + 0.01 * self.combo_manager.combo)

                self.input_box.update()
                if self.input_box.text == self.word_manager.current_word:
                    self.handle_success()
                if self.timer <= 0:
                    self.reset_round(is_error=True)
                if self.plant_growth >= 1.0:
                    self.sound_manager.play_sfx('harvest')
                    self.money_manager.add_coins(self.coins_per_growth)
                    self.total_coins_earned += self.coins_per_growth
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
            elif self.current_scene == "gacha":
                pass

            pygame.display.flip()

        pygame.quit()
        # บันทึกสถิติก่อนปิดเกม
        self.save_game_statistics()
        self.autosave()  # autosave ก่อนออก
        sys.exit()

    def open_gacha_overlay(self):
        # เตรียม fonts dict สำหรับ gacha overlay
        fonts = {
            "large": self.ui_manager.font_large,
            "medium": self.ui_manager.font_medium,
            "icon_large": self.ui_manager.font_xlarge,
            "icon_small": self.ui_manager.font_large,
            "small": self.ui_manager.font_small,
            "rarity": self.ui_manager.font_medium,
            "floating_large": self.ui_manager.font_large,
            "floating_medium": self.ui_manager.font_medium,
            "floating_small": self.ui_manager.font_small,
        }
        def close_overlay():
            self.gacha_overlay = None
            self.sound_manager.play_bgm()
        self.sound_manager.play_gacha_bgm()
        self.gacha_overlay = GachaOverlaySystem(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            fonts,
            self.money_manager,  # ส่ง money_manager
            self.ui_manager,  # ส่ง ui_manager
            self.sound_manager,  # ส่ง sound_manager ใหม่
            on_close=close_overlay
        )

    def open_collection_overlay(self):
        # เตรียม fonts dict สำหรับ collection overlay
        fonts = {
            "large": self.ui_manager.font_large,
            "medium": self.ui_manager.font_medium,
            "icon_large": self.ui_manager.font_xlarge,
            "icon_small": self.ui_manager.font_large,
            "small": self.ui_manager.font_small,
            "rarity": self.ui_manager.font_medium,
            "floating_large": self.ui_manager.font_large,
            "floating_medium": self.ui_manager.font_medium,
            "floating_small": self.ui_manager.font_small,
        }
        def close_overlay():
            self.collection_overlay = None
        self.collection_overlay = CollectionOverlaySystem(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            fonts,
            self.ui_manager,  # ส่ง ui_manager
            on_close=close_overlay
        )