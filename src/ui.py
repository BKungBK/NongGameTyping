import pygame
import os

class UIManager:
    """จัดการการวาดองค์ประกอบ UI ทั้งหมด"""
    def __init__(self, screen_width, screen_height):
        # --- ค่าคงที่ ---
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.FONT_PATH = os.path.join('assets', 'fonts', 'NotoSansThai-Regular.ttf')
        self.FONT_PATH_X = os.path.join('assets', 'fonts', 'BotsmaticDemo-MXOr.ttf')
        self.COLOR_SKY_TOP = (135, 206, 250)
        self.COLOR_SKY_BOTTOM = (176, 224, 230)
        self.COLOR_SOIL = (94, 63, 44)
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_SHADOW = (50, 50, 50)
        self.COLOR_TIMER_BAR = (255, 193, 7)
        self.COLOR_TIMER_BG = (90, 90, 90)
        self.COLOR_BOX_BG = (255, 255, 255, 220)
        self.COLOR_BOX_SHADOW = (180, 180, 180)

        # --- โหลดฟอนต์ ---
        try:
            self.font_large = pygame.font.Font(self.FONT_PATH, 72)
            self.font_medium = pygame.font.Font(self.FONT_PATH, 36)
            self.font_small = pygame.font.Font(self.FONT_PATH, 24)
            self.font_xlarge = pygame.font.Font(self.FONT_PATH_X, 96)
        except FileNotFoundError:
            print(f"Font file not found at {self.FONT_PATH}. Using default font.")
            self.font_large = pygame.font.Font(None, 80)
            self.font_medium = pygame.font.Font(None, 48)
            self.font_small = pygame.font.Font(None, 36)
            self.font_xlarge = pygame.font.Font(None, 120)
            
        # --- อนิเมชัน ---
        self.success_effect_alpha = 0
        self.current_success_color = (124, 252, 0, 128) # สีเขียวโปร่งแสง (ค่าเริ่มต้น)
        self.plant_growth = 0.0  # 0.0 to 1.0

        # --- โหลดภาพต้นไม้ (4 ขั้น) ---
        self.tree_images = []
        for idx in range(1, 5):
            path = os.path.join('assets', 'images\\Tree_Growain', f'tree{idx}.png')
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.tree_images.append(img)
            else:
                self.tree_images.append(None)  # กัน error
        self.current_tree_index = 0
        self.tree_anim_scale = 1.0
        self.tree_anim_direction = 0  # 0=นิ่ง, -1=หุบ, 1=เด้ง
        self.tree_anim_timer = 0.0
        self.last_tree_index = 0

    def draw_gradient_bg(self, surface):
        top = pygame.Color(*self.COLOR_SKY_TOP)
        bottom = pygame.Color(*self.COLOR_SKY_BOTTOM)
        for y in range(self.SCREEN_HEIGHT):
            color = [top[i] + (bottom[i] - top[i]) * y // self.SCREEN_HEIGHT for i in range(3)]
            pygame.draw.line(surface, color, (0, y), (self.SCREEN_WIDTH, y))

    def draw_timer(self, surface, current_time, max_time, x=None, y=None, w=None):
        ratio = max(0, min(1, current_time / max_time))
        bar_width = w if w else self.SCREEN_WIDTH * 0.7
        bar_height = 24
        x = x if x is not None else self.SCREEN_WIDTH * 0.15
        y = y if y is not None else 40
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(surface, self.COLOR_TIMER_BG, bg_rect, 0, 12)
        current_width = bar_width * ratio
        current_rect = pygame.Rect(x, y, current_width, bar_height)
        pygame.draw.rect(surface, self.COLOR_TIMER_BAR, current_rect, 0, 12)

    def draw_plant_animation(self, surface):
        """วาดอนิเมชันปลูกผัก (แบบง่าย)"""
        if self.plant_growth > 0:
            plant_height = 100 * self.plant_growth
            plant_width = 60
            plant_x = self.SCREEN_WIDTH / 2 - plant_width / 2
            plant_y = self.SCREEN_HEIGHT * 0.7 - plant_height
            
            # วาดลำต้น
            pygame.draw.rect(surface, (34, 139, 34), (plant_x + 20, plant_y, 20, plant_height))
            # วาดใบ (เป็นวงกลม)
            if self.plant_growth > 0.5:
                 pygame.draw.circle(surface, (0, 128, 0), (plant_x + 30, plant_y), 30)

            # ค่อยๆ ลดค่า growth ลงเพื่อให้ effect หายไป
            self.plant_growth -= 0.01

    def trigger_success_effect(self, color=None):
        """
        เริ่มเอฟเฟกต์ปลูกสำเร็จ
        :param color: สีของ overlay (tuple, เช่น (R, G, B, A)). หากเป็น None จะใช้สีเริ่มต้น.
        """
        self.success_effect_alpha = 200
        if color:
            self.current_success_color = color
        else:
            self.current_success_color = (124, 252, 0, 128)
            
    def trigger_error_effect(self, color=None):
        """
        เริ่มเอฟเฟกต์ปลูกสำเร็จ
        :param color: สีของ overlay (tuple, เช่น (R, G, B, A)). หากเป็น None จะใช้สีเริ่มต้น.
        """
        self.success_effect_alpha = 200
        if color:
            self.current_success_color = color
        else:
            self.current_success_color = (124, 252, 0, 128)

    def draw_success_overlay(self, surface):
        """วาด Overlay สีเขียวเมื่อสำเร็จ"""
        if self.success_effect_alpha > 0:
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            
            # ใช้สีที่ถูกตั้งค่าใน self.current_success_color และปรับค่า alpha
            overlay_color_with_alpha = self.current_success_color[:3] + (self.success_effect_alpha,)
            overlay.fill(overlay_color_with_alpha)
            
            surface.blit(overlay, (0, 0))
            self.success_effect_alpha -= 5 # ทำให้ค่อยๆจางลง

    def update_tree_animation(self, growth_percent):
        # 0-24% = 0, 25-49% = 1, 50-74% = 2, 75-100% = 3
        if growth_percent < 25:
            idx = 0
        elif growth_percent < 50:
            idx = 1
        elif growth_percent < 75:
            idx = 2
        else:
            idx = 3
        if idx != self.current_tree_index:
            self.last_tree_index = self.current_tree_index
            self.current_tree_index = idx
            self.tree_anim_direction = -1
            self.tree_anim_timer = 0.0
        if self.tree_anim_direction == -1:
            self.tree_anim_timer += 0.08
            self.tree_anim_scale = max(0.2, 1.0 - self.tree_anim_timer)
            if self.tree_anim_scale <= 0.21:
                self.tree_anim_direction = 1
                self.tree_anim_timer = 0.0
        elif self.tree_anim_direction == 1:
            self.tree_anim_timer += 0.08
            self.tree_anim_scale = min(1.0, 0.2 + self.tree_anim_timer)
            if self.tree_anim_scale >= 0.99:
                self.tree_anim_direction = 0
                self.tree_anim_scale = 1.0

    def draw_tree(self, surface, growth_percent):
        if growth_percent < 25:
            idx = 0
        elif growth_percent < 50:
            idx = 1
        elif growth_percent < 75:
            idx = 2
        else:
            idx = 3
        img = self.tree_images[idx]
        scale = self.tree_anim_scale
        # ปรับขนาดต้นไม้ตาม growth
        growth = max(0.0, min(0.5, growth_percent/100))
        size_scale = 0.5 + 0.5 * growth
        if img:
            w, h = img.get_width(), img.get_height()
            new_w = max(1, int(w * size_scale))
            new_h = max(1, int(h * size_scale * scale))
            x = self.SCREEN_WIDTH//2 - new_w//2
            y = int(self.SCREEN_HEIGHT*0.73 - new_h)
            tree_img = pygame.transform.smoothscale(img, (new_w, new_h))
            surface.blit(tree_img, (x, y))
        else:
            x = self.SCREEN_WIDTH//2
            y = int(self.SCREEN_HEIGHT*0.73 - 60)
            pygame.draw.circle(surface, (124, 252, 0), (x, y), int(40*size_scale))
            ch_surf = self.font_large.render("?", True, (255,255,255))
            ch_rect = ch_surf.get_rect(center=(x, y))
            surface.blit(ch_surf, ch_rect)

    def draw_growth_bar(self, surface, growth, y_offset=None):
        bar_w = 320
        bar_h = 22
        x = self.SCREEN_WIDTH//2 - bar_w//2
        y = self.SCREEN_HEIGHT - bar_h - 30  # ล่างสุด
        pygame.draw.rect(surface, (220,220,220), (x, y, bar_w, bar_h), border_radius=12)
        fill_w = int(bar_w * min(1.0, max(0.0, growth)))
        pygame.draw.rect(surface, (124, 252, 0), (x, y, fill_w, bar_h), border_radius=12)
        percent = int(growth*100)
        percent_surf = self.font_small.render(f"{percent}%", True, (60,60,60))
        percent_rect = percent_surf.get_rect(center=(x+bar_w//2, y+bar_h//2))
        surface.blit(percent_surf, percent_rect)

    def draw_box(self, surface, rect, radius=18, shadow=True):
        if shadow:
            shadow_rect = rect.move(4, 4)
            pygame.draw.rect(surface, self.COLOR_BOX_SHADOW, shadow_rect, border_radius=radius)
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill(self.COLOR_BOX_BG)
        surface.blit(s, rect.topleft)
        pygame.draw.rect(surface, (220,220,220), rect, 2, border_radius=radius)

    def draw_input_feedback(self, surface, target_word, user_input, center_pos):
        x, y = center_pos
        spacing = 60
        for i, ch in enumerate(target_word):
            if i < len(user_input):
                if user_input[i] == ch:
                    color = (0, 200, 0)
                else:
                    color = (220, 0, 0)
                font = self.font_xlarge
            elif i == len(user_input):
                color = (80, 180, 255)  # ตัวถัดไป (active) สีฟ้า
                font = self.font_xlarge
            else:
                color = (220, 220, 220)
                font = self.font_xlarge
            ch_surf = font.render(ch, True, color)
            ch_rect = ch_surf.get_rect()
            ch_rect.center = (x - (len(target_word)-1)*spacing//2 + i*spacing, y)
            surface.blit(ch_surf, ch_rect)

    def draw_all(self, surface, game_state):
        self.draw_gradient_bg(surface)
        pygame.draw.rect(surface, self.COLOR_SOIL, (0, self.SCREEN_HEIGHT * 0.7, self.SCREEN_WIDTH, self.SCREEN_HEIGHT * 0.3))
        self.draw_success_overlay(surface)
        growth_percent = game_state.get('plant_growth', 0.0) * 100
        self.update_tree_animation(growth_percent)
        self.draw_tree(surface, growth_percent)
        self.draw_input_feedback(surface, game_state['current_word'], game_state['input_box'].text, (self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT-160))
        self.draw_growth_bar(surface, game_state.get('plant_growth', 0.0))
        coins_rect = pygame.Rect(self.SCREEN_WIDTH-260, 30, 220, 60)
        self.draw_box(surface, coins_rect)
        coins_text = game_state['money_manager'].get_display_value()
        coins_surf = self.font_medium.render(coins_text, True, (255, 223, 0))
        coins_rect_text = coins_surf.get_rect(center=(coins_rect.centerx, coins_rect.centery))
        surface.blit(coins_surf, coins_rect_text)
        score_rect = pygame.Rect(40, self.SCREEN_HEIGHT-90, 220, 60)
        self.draw_box(surface, score_rect)
        score_text, combo_text = game_state['score_manager'].get_display_values()
        score_surf = self.font_medium.render(score_text, True, self.COLOR_TEXT)
        score_rect_text = score_surf.get_rect(center=(score_rect.centerx, score_rect.centery-12))
        surface.blit(score_surf, score_rect_text)
        combo_surf = self.font_small.render(combo_text, True, (255, 215, 0))
        combo_rect_text = combo_surf.get_rect(center=(score_rect.centerx, score_rect.centery+18))
        surface.blit(combo_surf, combo_rect_text)
        self.draw_timer(surface, game_state['timer'], game_state['max_time'], x=self.SCREEN_WIDTH-260, y=100, w=220)