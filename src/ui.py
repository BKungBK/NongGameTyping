import pygame
import math
import os

class UIManager:
    """จัดการการวาดองค์ประกอบ UI ทั้งหมด - ปรับปรุงแล้ว"""
    def __init__(self, screen_width, screen_height):
        # --- ค่าคงที่ ---
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.FONT_PATH = os.path.join('assets', 'fonts', 'NotoSansThai_Condensed-Bold.ttf')
        self.FONT_PATH_X = os.path.join('assets', 'fonts', 'BotsmaticDemo-MXOr.ttf')
        
        # --- สีสำหรับธีมเกม ---
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_TEXT_SECONDARY = (200, 200, 200)
        self.COLOR_SHADOW = (0, 0, 0, 100)
        
        # --- สีสำหรับ UI Elements ---
        self.COLOR_TIMER_BAR = (255, 165, 0)
        self.COLOR_TIMER_BG = (40, 40, 40)
        self.COLOR_BOX_BG = (30, 30, 30, 200)
        self.COLOR_BOX_BORDER = (80, 80, 80)
        self.COLOR_ACCENT = (100, 200, 255)
        self.COLOR_SUCCESS = (50, 255, 50)
        self.COLOR_ERROR = (255, 50, 50)
        self.COLOR_WARNING = (255, 200, 50)

        # --- โหลดฟอนต์ ---
        try:
            self.font_xlarge = pygame.font.Font(self.FONT_PATH_X, 96)
            self.font_large = pygame.font.Font(self.FONT_PATH, 64)
            self.font_medium = pygame.font.Font(self.FONT_PATH, 32)
            self.font_small = pygame.font.Font(self.FONT_PATH, 24)
            self.font_tiny = pygame.font.Font(self.FONT_PATH, 18)
        except FileNotFoundError:
            print(f"Font file not found. Using default fonts.")
            self.font_xlarge = pygame.font.Font(None, 96)
            self.font_large = pygame.font.Font(None, 64)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)
            self.font_tiny = pygame.font.Font(None, 18)
            
        # --- โหลดรูปภาพพื้นหลัง ---
        self.background_image = None
        try:
            bg_path = os.path.join('assets', 'images', 'bg.png')
            if os.path.exists(bg_path):
                self.background_image = pygame.image.load(bg_path).convert()
                # ปรับขนาดให้พอดีกับหน้าจอ
                self.background_image = pygame.transform.smoothscale(
                    self.background_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
                )
                print(f"Background image loaded successfully: {bg_path}")
            else:
                print(f"Background image not found: {bg_path}")
        except Exception as e:
            print(f"Error loading background image: {e}")
            
        # --- Animation Variables ---
        self.success_effect_alpha = 0
        self.current_success_color = (50, 255, 50, 128)
        self.plant_growth = 0.0
        self.animation_time = 0.0
        
        # --- UI Animation Variables ---
        self.ui_bounce_scale = 1.0
        self.ui_pulse_alpha = 0
        self.score_pop_scale = 1.0
        self.score_pop_timer = 0.0
        self.combo_glow_intensity = 0.0
        
        # --- Tree Animation (improved) ---
        self.tree_images = []
        for idx in range(1, 5):
            path = os.path.join('assets', 'images\\Tree_Growain', f'tree{idx}.png')
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.tree_images.append(img)
            else:
                self.tree_images.append(None)
        
        self.current_tree_index = 0
        self.tree_anim_scale = 1.0
        self.tree_anim_direction = 0
        self.tree_anim_timer = 0.0
        self.tree_sway_offset = 0.0
        
        # --- Particle System ---
        self.particles = []
        
        # --- Layout Constants ---
        self.PADDING = 20
        self.CORNER_RADIUS = 15
        self.SHADOW_OFFSET = 6

    def update(self, dt):
        """อัปเดตแอนิเมชันทั้งหมด"""
        self.animation_time += dt
        
        # อัปเดต particle system
        self.update_particles(dt)
        
        # อัปเดต UI animations
        self.ui_pulse_alpha = abs(math.sin(self.animation_time * 3)) * 50
        
        # อัปเดต tree sway
        self.tree_sway_offset = math.sin(self.animation_time * 2) * 3
        
        # อัปเดต score pop animation
        if self.score_pop_timer > 0:
            self.score_pop_timer -= dt
            progress = 1.0 - (self.score_pop_timer / 0.5)
            self.score_pop_scale = 1.0 + (math.sin(progress * math.pi) * 0.3)
        else:
            self.score_pop_scale = 1.0
            
        # อัปเดต combo glow
        self.combo_glow_intensity = abs(math.sin(self.animation_time * 4)) * 0.5 + 0.5

    def add_particle(self, x, y, color, velocity=(0, -50), lifetime=2.0):
        """เพิ่ม particle effect"""
        particle = {
            'x': x,
            'y': y,
            'vx': velocity[0] + (pygame.time.get_ticks() % 20 - 10) * 0.1,
            'vy': velocity[1],
            'color': color,
            'lifetime': lifetime,
            'max_lifetime': lifetime,
            'size': 4
        }
        self.particles.append(particle)

    def update_particles(self, dt):
        """อัปเดต particle system"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] += 100 * dt  # gravity
            particle['lifetime'] -= dt
            
            # ลด size ตามเวลา
            progress = particle['lifetime'] / particle['max_lifetime']
            particle['size'] = max(1, int(4 * progress))
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)

    def draw_particles(self, surface):
        """วาด particles"""
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            color = (*particle['color'][:3], alpha)
            
            # สร้าง surface สำหรับ particle
            particle_surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, (particle['size'], particle['size']), particle['size'])
            
            surface.blit(particle_surf, (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))

    def draw_background_image(self, surface):
        """วาดรูปภาพพื้นหลัง"""
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            # หากไม่มีรูปภาพพื้นหลัง ให้ใช้สีพื้นหลังธรรมดา
            surface.fill((25, 25, 40))

    def draw_gradient_bg(self, surface):
        """วาดพื้นหลังแบบไล่สี (ใช้รูปภาพแทน)"""
        self.draw_background_image(surface)

    def draw_modern_box(self, surface, rect, color=None, border_color=None, corner_radius=None, shadow=True):
        """วาดกล่องสไตล์โมเดิร์น"""
        if color is None:
            color = self.COLOR_BOX_BG
        if border_color is None:
            border_color = self.COLOR_BOX_BORDER
        if corner_radius is None:
            corner_radius = self.CORNER_RADIUS
            
        # วาดเงา
        if shadow:
            shadow_rect = rect.move(self.SHADOW_OFFSET, self.SHADOW_OFFSET)
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect(), border_radius=corner_radius)
            surface.blit(shadow_surf, shadow_rect.topleft)
        
        # วาดกล่องหลัก
        box_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surf, color, box_surf.get_rect(), border_radius=corner_radius)
        pygame.draw.rect(box_surf, border_color, box_surf.get_rect(), 2, border_radius=corner_radius)
        
        surface.blit(box_surf, rect.topleft)

    def draw_animated_timer(self, surface, current_time, max_time, x, y, w, h=None):
        """วาด timer แบบมีแอนิเมชัน"""
        if h is None:
            h = 28
            
        ratio = max(0, min(1, current_time / max_time))
        
        # วาดพื้นหลัง
        bg_rect = pygame.Rect(x, y, w, h)
        self.draw_modern_box(surface, bg_rect, self.COLOR_TIMER_BG, shadow=False, corner_radius=4)
        
        # วาดแถบเวลา
        if ratio > 0:
            current_width = int(w * ratio)
            min_fill = 4
            actual_width = max(min_fill, current_width - 4)
            current_rect = pygame.Rect(x + 2, y + 2, actual_width, h - 4)
            
            # เปลี่ยนสีตามเวลาที่เหลือ
            if ratio > 0.5:
                color = self.COLOR_SUCCESS
            elif ratio > 0.25:
                color = self.COLOR_WARNING
            else:
                color = self.COLOR_ERROR
                # เพิ่มเอฟเฟกต์กะพริบเมื่อเวลาใกล้หมด
                flash = abs(math.sin(self.animation_time * 8))
                color = tuple(int(c * (0.5 + flash * 0.5)) for c in color)
            
            pygame.draw.rect(surface, color, current_rect, border_radius=4)
        
        # (ลบเลขเวลาออก ไม่ต้องวาดข้อความเวลา)

    def draw_combo_display(self, surface, combo_manager, x, y):
        """วาดการแสดงคอมโบแบบพิเศษ"""
        combo_text = combo_manager.get_display_value()
        box_rect = pygame.Rect(x, y, 240, 80)
        self.draw_modern_box(surface, box_rect)
        combo_surf = self.font_medium.render(combo_text, True, self.COLOR_WARNING)
        combo_rect = combo_surf.get_rect(center=(box_rect.centerx, box_rect.centery))
        surface.blit(combo_surf, combo_rect)

    def draw_money_display(self, surface, money_manager, x=None, y=None):
        """วาดการแสดงเงินแบบพิเศษ (กล่องชิดขวาบน, ข้อความชิดขวา, ขนาดพอดี)"""
        money_text = money_manager.get_display_value()
        
        # เตรียม surface ของข้อความและไอคอน
        money_surf = self.font_medium.render(money_text, True, (255, 223, 0))
        symbol_surf = self.font_small.render("¢", True, (200, 150, 0))
        
        padding_x = 18
        padding_y = 10
        spacing = 20
        icon_diameter = 36  # 18*2
        content_height = max(money_surf.get_height(), icon_diameter, symbol_surf.get_height())
        box_w = icon_diameter + spacing + money_surf.get_width() + padding_x * 2
        box_h = content_height + padding_y * 2
        
        # กล่องชิดขวาบน
        if x is None:
            x = self.SCREEN_WIDTH - box_w - 8  # 8px margin
        if y is None:
            y = 8
        box_rect = pygame.Rect(x, y, box_w, box_h)
        self.draw_modern_box(surface, box_rect, color=(50, 50, 30, 200))
        
        # วาดไอคอนเหรียญ (ชิดซ้าย)
        coin_center = (box_rect.left + padding_x + icon_diameter // 2, box_rect.centery)
        coin_bounce = math.sin(self.animation_time * 6) * 2
        coin_y = coin_center[1] + coin_bounce
        pygame.draw.circle(surface, (255, 215, 0), (coin_center[0], int(coin_y)), 18)
        pygame.draw.circle(surface, (255, 165, 0), (coin_center[0], int(coin_y)), 18, 3)
        # วาดสัญลักษณ์เหรียญ
        symbol_rect = symbol_surf.get_rect(center=(coin_center[0], int(coin_y)))
        surface.blit(symbol_surf, symbol_rect)
        
        # วาดจำนวนเงิน (ชิดขวา)
        money_rect = money_surf.get_rect()
        money_rect.centery = box_rect.centery
        money_rect.right = box_rect.right - padding_x
        surface.blit(money_surf, money_rect)

    def draw_enhanced_input_feedback(self, surface, target_word, user_input, center_pos):
        """วาดการแสดงผลการพิมพ์แบบปรับปรุง"""
        x, y = center_pos
        char_spacing = 70
        
        # วาดพื้นหลังสำหรับพื้นที่พิมพ์
        total_width = len(target_word) * char_spacing
        bg_rect = pygame.Rect(x - total_width//2 - 20, y - 60, total_width + 40, 120)
        self.draw_modern_box(surface, bg_rect, color=(20, 20, 20, 150))
        
        for i, ch in enumerate(target_word):
            char_x = x - (len(target_word)-1) * char_spacing // 2 + i * char_spacing
            char_y = y
            
            # กำหนดสีและเอฟเฟกต์
            if i < len(user_input):
                if user_input[i] == ch:
                    # ถูกต้อง - สีเขียว
                    color = self.COLOR_SUCCESS
                    # เพิ่มเอฟเฟกต์ particle เมื่อพิมพ์ถูก
                    if i == len(user_input) - 1:  # ตัวที่เพิ่งพิมพ์
                        self.add_particle(char_x, char_y - 20, self.COLOR_SUCCESS, (0, -30), 1.5)
                else:
                    # ผิด - สีแดง
                    color = self.COLOR_ERROR
                    # เอฟเฟกต์สั่น
                    shake = math.sin(self.animation_time * 20) * 3
                    char_x += shake
            elif i == len(user_input):
                # ตัวที่กำลังจะพิมพ์ - สีฟ้าพร้อมเอฟเฟกต์เรืองแสง
                color = self.COLOR_ACCENT
                glow_alpha = int(abs(math.sin(self.animation_time * 5)) * 100)
                
                # วาดเรืองแสง
                glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color[:3], glow_alpha), (40, 40), 40)
                surface.blit(glow_surf, (char_x - 40, char_y - 40))
            else:
                # ยังไม่ถึง - สีเทา
                color = self.COLOR_TEXT_SECONDARY
            
            # วาดตัวอักษร
            char_surf = self.font_xlarge.render(ch, True, color)
            char_rect = char_surf.get_rect(center=(char_x, char_y))
            
            # เพิ่มเงาให้ตัวอักษร
            shadow_surf = self.font_xlarge.render(ch, True, (0, 0, 0, 100))
            shadow_rect = shadow_surf.get_rect(center=(char_x + 3, char_y + 3))
            surface.blit(shadow_surf, shadow_rect)
            surface.blit(char_surf, char_rect)

    def trigger_success_effect(self, color=None):
        """เริ่มเอฟเฟกต์ความสำเร็จ"""
        self.success_effect_alpha = 150
        if color:
            self.current_success_color = color
        else:
            self.current_success_color = (50, 255, 50, 128)
        
        # เพิ่ม particles
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2
        for _ in range(10):
            angle = pygame.time.get_ticks() % 360
            vx = math.cos(math.radians(angle)) * 100
            vy = math.sin(math.radians(angle)) * 100
            self.add_particle(center_x, center_y, self.COLOR_SUCCESS, (vx, vy), 2.0)

    def trigger_error_effect(self, color=None):
        """เริ่มเอฟเฟกต์ความผิดพลาด"""
        self.success_effect_alpha = 150
        if color:
            self.current_success_color = color
        else:
            self.current_success_color = (255, 0, 0, 128)
        # เพิ่ม particles สีแดง
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2
        for _ in range(10):
            angle = pygame.time.get_ticks() % 360
            vx = math.cos(math.radians(angle)) * 100
            vy = math.sin(math.radians(angle)) * 100
            self.add_particle(center_x, center_y, self.COLOR_ERROR, (vx, vy), 2.0)

    def trigger_score_pop(self):
        """เริ่มเอฟเฟกต์คะแนนกระโดด"""
        self.score_pop_timer = 0.5

    def draw_success_overlay(self, surface):
        """วาดเลเยอร์ซ้อนทับเมื่อสำเร็จ"""
        if self.success_effect_alpha > 0:
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            color_with_alpha = (*self.current_success_color[:3], self.success_effect_alpha)
            overlay.fill(color_with_alpha)
            surface.blit(overlay, (0, 0))
            self.success_effect_alpha -= 3

    def update_tree_animation(self, growth_percent):
        """อัปเดตแอนิเมชันต้นไม้"""
        # กำหนดขั้นตอนการเติบโต
        if growth_percent < 25:
            idx = 0
        elif growth_percent < 50:
            idx = 1
        elif growth_percent < 75:
            idx = 2
        else:
            idx = 3
        
        # เปลี่ยนขั้นตอนการเติบโต
        if idx != self.current_tree_index:
            self.current_tree_index = idx
            self.tree_anim_direction = -1
            self.tree_anim_timer = 0.0
            
            # เพิ่ม particle เมื่อต้นไม้เติบโต
            tree_x = self.SCREEN_WIDTH // 2
            tree_y = int(self.SCREEN_HEIGHT * 0.85)  # ปรับตำแหน่งให้ตรงกับต้นไม้ใหม่
            for _ in range(5):
                self.add_particle(tree_x, tree_y, self.COLOR_SUCCESS, (0, -50), 1.0)
        
        # อัปเดตแอนิเมชันการเปลี่ยนขนาด
        if self.tree_anim_direction == -1:
            self.tree_anim_timer += 0.1
            self.tree_anim_scale = max(0.3, 1.0 - self.tree_anim_timer)
            if self.tree_anim_scale <= 0.31:
                self.tree_anim_direction = 1
                self.tree_anim_timer = 0.0
        elif self.tree_anim_direction == 1:
            self.tree_anim_timer += 0.1
            self.tree_anim_scale = min(1.0, 0.3 + self.tree_anim_timer)
            if self.tree_anim_scale >= 0.99:
                self.tree_anim_direction = 0
                self.tree_anim_scale = 1.0

    def draw_enhanced_tree(self, surface, growth_percent):
        """วาดต้นไม้แบบปรับปรุง"""
        # กำหนดขั้นตอนการเติบโต
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
        
        # คำนวณขนาดต้นไม้
        growth_factor = max(0.3, min(1.0, growth_percent / 100))
        size_scale = 0.4 + 0.6 * growth_factor
        
        if img:
            w, h = img.get_width(), img.get_height()
            new_w = max(1, int(w * size_scale))
            new_h = max(1, int(h * size_scale * scale))
            
            # เพิ่มการโยกไหวเล็กน้อย
            x = self.SCREEN_WIDTH // 2 - new_w // 2 + int(self.tree_sway_offset)
            y = int(self.SCREEN_HEIGHT * 0.95 - new_h)
            
            tree_img = pygame.transform.smoothscale(img, (new_w, new_h))
            surface.blit(tree_img, (x, y))
        else:
            # วาดต้นไม้ง่ายๆ หากไม่มีภาพ
            x = self.SCREEN_WIDTH // 2 + int(self.tree_sway_offset)
            y = int(self.SCREEN_HEIGHT * 0.95 - 60 * size_scale)
            radius = int(40 * size_scale * scale)
            
            # วาดเงา
            pygame.draw.circle(surface, (0, 0, 0, 100), (x + 3, y + 3), radius)
            # วาดต้นไม้
            pygame.draw.circle(surface, self.COLOR_SUCCESS, (x, y), radius)
            
            # วาดเครื่องหมายคำถาม
            question_surf = self.font_large.render("?", True, self.COLOR_TEXT)
            question_rect = question_surf.get_rect(center=(x, y))
            surface.blit(question_surf, question_rect)

    def draw_enhanced_growth_bar(self, surface, growth):
        """วาดแถบการเติบโตแบบปรับปรุง"""
        bar_w = 400
        bar_h = 30
        x = self.SCREEN_WIDTH // 2 - bar_w // 2
        y = self.SCREEN_HEIGHT - bar_h - 40
        
        # วาดพื้นหลัง
        bg_rect = pygame.Rect(x, y, bar_w, bar_h)
        self.draw_modern_box(surface, bg_rect, self.COLOR_TIMER_BG, corner_radius=5)
        
        # วาดแถบการเติบโต
        fill_w = int(bar_w * min(1.0, max(0.0, growth)))
        min_fill = 4  # ความกว้างขั้นต่ำ
        if fill_w > 0:
            actual_fill_w = max(min_fill, fill_w - 6)
            fill_rect = pygame.Rect(x + 3, y + 3, actual_fill_w, bar_h - 6)
            radius = max(2, min(5, fill_rect.width // 2))  # ปรับมุมให้สัมพันธ์กับขนาด
            
            # เปลี่ยนสีตามความคืบหน้า
            if growth < 0.25:
                color = (255, 100, 100)
            elif growth < 0.5:
                color = (255, 200, 100)
            elif growth < 0.75:
                color = (200, 255, 100)
            else:
                color = self.COLOR_SUCCESS

            pygame.draw.rect(surface, color, fill_rect, border_radius=radius)

            if actual_fill_w > 10:
                highlight_rect = pygame.Rect(x + 3, y + 3, actual_fill_w, 8)
                highlight_color = tuple(min(255, c + 50) for c in color[:3])
                pygame.draw.rect(surface, highlight_color, highlight_rect, border_radius=radius)

        # วาดเปอร์เซ็นต์
        percent = int(growth * 100)
        percent_surf = self.font_medium.render(f"{percent}%", True, self.COLOR_TEXT)
        percent_rect = percent_surf.get_rect(center=(x + bar_w // 2, y + bar_h // 2))
        
        # วาดเงาให้ข้อความ
        shadow_surf = self.font_medium.render(f"{percent}%", True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(x + bar_w // 2 + 2, y + bar_h // 2 + 2))
        surface.blit(shadow_surf, shadow_rect)
        surface.blit(percent_surf, percent_rect)

    def draw_all(self, surface, game_state):
        """วาดทุกอย่างด้วยเลย์เอาต์ใหม่"""
        # อัปเดตแอนิเมชัน
        dt = 1/60  # สมมติ 60 FPS
        self.update(dt)
        
        # วาดพื้นหลัง (ใช้รูปภาพแทน gradient และดิน)
        self.draw_background_image(surface)
        
        # วาดเอฟเฟกต์ความสำเร็จ
        self.draw_success_overlay(surface)
        
        # วาดต้นไม้
        growth_percent = game_state.get('plant_growth', 0.0) * 100
        self.update_tree_animation(growth_percent)
        self.draw_enhanced_tree(surface, growth_percent)
        
        # วาดการป้อนข้อมูล (ตรงกลางจอ)
        input_center = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
        self.draw_enhanced_input_feedback(surface, game_state['current_word'], 
                                        game_state['input_box'].text, input_center)
        
        # วาดแถบการเติบโต
        self.draw_enhanced_growth_bar(surface, game_state.get('plant_growth', 0.0))
        
        # วาดจอแสดงเงิน (มุมขวาบน)
        money_x = self.SCREEN_WIDTH - 150
        money_y = 30
        self.draw_money_display(surface, game_state['money_manager'], money_x, money_y)
        
        # วาดจอแสดงคอมโบ (มุมซ้ายล่าง)
        combo_x = 40
        combo_y = self.SCREEN_HEIGHT - 130
        self.draw_combo_display(surface, game_state['combo_manager'], combo_x, combo_y)
        
        # วาดจับเวลา (ย้ายไปขอบบนและขยายความกว้าง)
        timer_x = 0
        timer_y = 0
        timer_w = self.SCREEN_WIDTH
        timer_h = 20
        self.draw_animated_timer(surface, game_state['timer'], game_state['max_time'], 
                               timer_x, timer_y, timer_w, timer_h)
        
        # วาดระบบ particle
        self.draw_particles(surface)
        

    def create_floating_text(self, text, x, y, color, duration=2.0):
        """สร้างข้อความลอย (สำหรับแสดงคะแนนที่ได้)"""
        self.add_particle(x, y, color, (0, -80), duration)
        
        # เพิ่มข้อความลอยถ้าต้องการ (ต้องสร้างระบบแยก)
        pass