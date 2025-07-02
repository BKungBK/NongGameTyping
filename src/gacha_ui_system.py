import pygame
import math
import random
import os
from typing import List, Tuple, Dict, Optional, Callable
from .data_manager import DataManager, Rarity

# --- Constants ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
GOLD_LIGHT = (255, 235, 100)
PURPLE = (138, 43, 226)
PURPLE_LIGHT = (180, 100, 255)
BLUE = (70, 130, 180)
BLUE_LIGHT = (120, 180, 255)
SILVER = (192, 192, 192)

SPIN_DURATION = 90 * 2  # 3s at 60 FPS
REVEAL_DURATION = 30 * 2  # 1s
RESULT_SHOW_DURATION = 60 * 2  # 2s
PREVIEW_CHANGE_RATE = 8

# --- Gacha Costs ---
GACHA_1_COST = 100
GACHA_10_COST = 900

# --- Easing functions ---
def ease_in_out_cubic(t):
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

def ease_out_bounce(t):
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t = t - 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t = t - 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t = t - 2.625 / d1
        return n1 * t * t + 0.984375

def ease_out_elastic(t):
    c4 = (2 * math.pi) / 3
    return 0 if t == 0 else 1 if t == 1 else pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1

# --- Effect Classes ---
class Particle:
    def __init__(self, x, y, color, velocity, life, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = 0.008
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.999
        self.life -= 1
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            size = max(1, int(self.size * (self.life / self.max_life)))
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*self.color, alpha), (size, size), size)
            screen.blit(particle_surf, (self.x - size, self.y - size))

class StarParticle(Particle):
    def __init__(self, x, y):
        super().__init__(x, y, GOLD, (0, random.uniform(-2, -0.5)), 72, 6)
        self.angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(1, 3)
        self.scale_pulse = random.uniform(0.8, 1.2)
    def update(self):
        self.y += self.vy
        self.angle += self.rotation_speed
        self.life -= 1
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            pulse = 1 + 0.3 * math.sin(self.angle * 0.1)
            size = max(1, int(self.size * (self.life / self.max_life) * self.scale_pulse * pulse))
            if size < 1: return
            star_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            points = []
            for i in range(10):
                angle_rad = math.radians(self.angle + i * 36)
                radius = size if i % 2 == 0 else size // 2
                px = size * 2 + radius * math.cos(angle_rad)
                py = size * 2 + radius * math.sin(angle_rad)
                points.append((px, py))
            pygame.draw.polygon(star_surf, (*self.color, alpha), points)
            screen.blit(star_surf, (self.x - size * 2, self.y - size * 2))

class RadialBurst:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 0
        self.max_radius = 250
        self.life = 72
        self.max_life = 72
    def update(self):
        progress = 1 - (self.life / self.max_life)
        self.radius = self.max_radius * ease_out_elastic(progress)
        self.life -= 1
    def draw(self, screen):
        if self.life > 0:
            alpha = int(128 * (self.life / self.max_life))
            for i in range(16):
                angle = math.radians(i * 22.5)
                end_x = self.x + self.radius * math.cos(angle)
                end_y = self.y + self.radius * math.sin(angle)
                pygame.draw.line(screen, (*self.color, alpha), (self.x, self.y), (end_x, end_y), 4)

class RotatingBorder:
    def __init__(self, center, size, rotation_speed, thickness, color):
        self.center_x, self.center_y = center
        self.base_size = size
        self.size = size
        self.base_speed = rotation_speed
        self.rotation_speed = rotation_speed
        self.thickness = thickness
        self.color = color
        self.angle = 0
        self.scale = 1.0
        self.target_scale = 1.0
        self.target_speed = rotation_speed
    def update(self):
        self.angle = (self.angle + self.rotation_speed) % 360
        self.scale += (self.target_scale - self.scale) * 0.1
        self.rotation_speed += (self.target_speed - self.rotation_speed) * 0.1
        self.size = int(self.base_size * self.scale)
    def set_speed(self, speed_multiplier):
        self.target_speed = self.base_speed * speed_multiplier
    def set_scale(self, scale):
        self.target_scale = scale
    def draw(self, screen):
        half_size = self.size // 2
        points = [ (0, -half_size), (half_size, 0), (0, half_size), (-half_size, 0) ]
        cos_a = math.cos(math.radians(self.angle))
        sin_a = math.sin(math.radians(self.angle))
        rotated_points = [
            (x * cos_a - y * sin_a + self.center_x,
             x * sin_a + y * cos_a + self.center_y)
            for x, y in points
        ]
        glow_surf = pygame.Surface((self.size + 20, self.size + 20), pygame.SRCALPHA)
        glow_points = [
            (x * cos_a - y * sin_a + (self.size + 20) // 2,
             x * sin_a + y * cos_a + (self.size + 20) // 2)
            for x, y in [(p[0] * 1.1, p[1] * 1.1) for p in points]
        ]
        pygame.draw.polygon(glow_surf, (*self.color, 50), glow_points, self.thickness + 2)
        screen.blit(glow_surf, (self.center_x - (self.size + 20) // 2, self.center_y - (self.size + 20) // 2))
        pygame.draw.polygon(screen, self.color, rotated_points, self.thickness)

class GachaItem:
    RARITY_COLORS = {'SSR': GOLD, 'SR': PURPLE, 'R': BLUE}
    def __init__(self, data, rarity):
        self.name = data["name"]
        self.icon = data["icon"]  # This can now be either emoji or image filename
        self.rate = data["rate"]
        self.rarity = rarity
        self.color = self.RARITY_COLORS[rarity]
        self.image = None
        self.is_emoji = self._is_emoji(self.icon)
        if not self.is_emoji:
            self._load_image()
    
    def _is_emoji(self, text):
        """Check if the icon is an emoji (not a filename ending with .png)"""
        return not text.lower().endswith('.png')
    
    def _load_image(self):
        """Load the item image from assets"""
        try:
            # Get the image path using DataManager
            data_manager = DataManager()
            image_path = data_manager.get_assets_path("images", f"Item/{self.icon}")
            
            if os.path.exists(image_path):
                self.image = pygame.image.load(image_path).convert_alpha()
            else:
                print(f"Warning: Image not found for {self.name}: {image_path}")
                self.image = None
        except Exception as e:
            print(f"Error loading image for {self.name}: {e}")
            self.image = None
    
    def get_icon_surface(self, size=None):
        if self.is_emoji:
            font = None
            emoji_font_size = max(10, (size or 60) // 2)
            # ลองใช้ฟอนต์อิโมจิที่รองรับบน Windows ก่อน
            try:
                font = pygame.font.SysFont("Segoe UI Emoji", emoji_font_size)
            except Exception:
                font = None
            if font is None or font.get_height() == 0:
                try:
                    font = pygame.font.Font("assets/fonts/NotoColorEmoji-Regular.ttf", emoji_font_size)
                except Exception:
                    font = pygame.font.Font(None, emoji_font_size)
            return font.render(self.icon, True, WHITE)
        if self.image is None:
            font = pygame.font.Font(None, size or 60)
            return font.render(self.icon, True, WHITE)
        if size:
            return self._scale_image_to_fit(self.image, size)
        return self.image
    
    def _scale_image_to_fit(self, image, target_size):
        """Scale image to fit within target_size while maintaining aspect ratio"""
        img_width, img_height = image.get_size()
        
        # Calculate scale factor to fit within target_size
        scale_x = target_size / img_width
        scale_y = target_size / img_height
        scale = min(scale_x, scale_y)  # Use smaller scale to fit within bounds
        
        # Calculate new dimensions
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Scale the image
        scaled_image = pygame.transform.scale(image, (new_width, new_height))
        
        # Create a surface with the target size and center the scaled image
        result_surface = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
        
        # Calculate centering offset
        offset_x = (target_size - new_width) // 2
        offset_y = (target_size - new_height) // 2
        
        # Blit the scaled image centered on the result surface
        result_surface.blit(scaled_image, (offset_x, offset_y))
        
        return result_surface

class FloatingText:
    def __init__(self, text, x, y, color, font):
        self.x = x
        self.y = y
        self.start_y = y
        self.life = 144
        self.max_life = 144
        self.scale = 0.5
        self.target_scale = 1.0
        self.text_surf = font.render(text, True, color)
        self.original_surf = self.text_surf.copy()
    def update(self):
        self.scale += (self.target_scale - self.scale) * 0.1
        progress = (self.max_life - self.life) / self.max_life
        self.y = self.start_y - ease_out_bounce(progress) * 80
        if self.scale != 1.0:
            new_size = (int(self.original_surf.get_width() * self.scale),
                       int(self.original_surf.get_height() * self.scale))
            if new_size[0] > 0 and new_size[1] > 0:
                self.text_surf = pygame.transform.scale(self.original_surf, new_size)
        self.life -= 1
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            self.text_surf.set_alpha(alpha)
            text_rect = self.text_surf.get_rect(center=(self.x, self.y))
            screen.blit(self.text_surf, text_rect)

class GachaOverlaySystem:
    def __init__(self, screen_size, font_dict, money_manager, ui_manager, sound_manager=None, on_close: Optional[Callable]=None):
        self.width, self.height = screen_size
        self.fonts = font_dict
        self.money_manager = money_manager
        self.ui_manager = ui_manager
        self.sound_manager = sound_manager
        self.on_close = on_close
        self.state = "idle"
        self.animation_timer = 0
        self.effects = []
        self.screen_flash_alpha = 0
        self.result_scale = 0.5
        self.target_result_scale = 1.0
        self.center = (self.width // 2, self.height // 2 - 50)
        self.current_results = []
        self.current_item_index = 0
        self._load_data()
        self._load_fonts()
        self.borders = [
            RotatingBorder(self.center, 300, 0.5, 4, WHITE),
            RotatingBorder(self.center, 240, -0.3, 3, SILVER),
            RotatingBorder(self.center, 180, 0.2, 2, WHITE)
        ]
        # --- ปรับตำแหน่งปุ่ม X และกล่อง coin ---
        self.close_btn_size = 40
        margin = 32  # เพิ่มระยะห่างขอบบน
        padding_x = 18
        padding_y = 10
        spacing = 20
        icon_diameter = 36
        money_text = str(self.money_manager.coins)
        money_surf = self.fonts["medium"].render(money_text, True, (255, 223, 0))
        box_w = icon_diameter + spacing + money_surf.get_width() + padding_x * 2
        box_h = max(money_surf.get_height(), icon_diameter) + padding_y * 2
        self.close_rect = pygame.Rect(self.width - margin - self.close_btn_size, margin, self.close_btn_size, self.close_btn_size)
        self.coin_box_x = self.close_rect.left - 8 - box_w
        self.coin_box_y = self.close_rect.top + (self.close_btn_size - box_h)//2
        self.coin_box_w = box_w
        self.coin_box_h = box_h
        self.button1_rect = pygame.Rect(self.width // 2 - 200, self.height - 120, 180, 70)
        self.button10_rect = pygame.Rect(self.width // 2 + 20, self.height - 120, 180, 70)
        self.preview_item = None
        # --- Fade-in animation ---
        self.fade_alpha = 0  # 0 = โปร่งใส, 255 = ทึบ
        self.fading_out = False
        self._fade_out_called = False
        self._prev_state = None

    def _load_data(self):
        # ใช้ DataManager แทนการโหลดไฟล์โดยตรง
        self.data_manager = DataManager()
        gacha_data = self.data_manager.get_gacha_data()
        
        self.items_by_rarity = {
            rarity: [GachaItem(item, rarity) for item in items]
            for rarity, items in gacha_data["items"].items()
        }
        self.all_items = [item for sublist in self.items_by_rarity.values() for item in sublist]
        self.rates = gacha_data["base_rates"]

    def _load_fonts(self):
        # ใช้ fonts จาก dict ที่ main ส่งมา (รองรับขนาดใหญ่/กลาง/เล็ก/ไอคอน)
        # ถ้าไม่มีขนาดไหนจะ fallback เป็น default
        def get_font(name, default_size):
            return self.fonts.get(name) or pygame.font.Font(None, default_size)
        self.fonts.setdefault("large", get_font("large", 56))
        self.fonts.setdefault("medium", get_font("medium", 36))
        self.fonts.setdefault("small", get_font("small", 28))
        self.fonts.setdefault("icon_large", get_font("icon_large", 80))
        self.fonts.setdefault("icon_small", get_font("icon_small", 60))
        self.fonts.setdefault("rarity", get_font("rarity", 32))
        self.fonts.setdefault("floating_large", get_font("floating_large", 48))
        self.fonts.setdefault("floating_medium", get_font("floating_medium", 42))
        self.fonts.setdefault("floating_small", get_font("floating_small", 36))

    def _get_weighted_item(self, rarity):
        items = self.items_by_rarity[rarity]
        weights = [item.rate for item in items]
        return random.choices(items, weights=weights)[0]
    def _get_rarity(self):
        rand = random.uniform(0, 100)
        cumulative_rate = 0
        for rarity, rate in self.rates.items():
            cumulative_rate += rate
            if rand < cumulative_rate:
                return rarity
        return 'R'
    def _draw_items(self, count):
        return [self._get_weighted_item(self._get_rarity()) for _ in range(count)]

    def _create_particles(self, x, y, color, count, speed_range, life_range, size_range):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            velocity = (speed * math.cos(angle), speed * math.sin(angle))
            life = random.randint(*life_range)
            size = random.randint(*size_range)
            self.effects.append(Particle(x, y, color, velocity, life, size))

    def _create_rarity_effects(self, item):
        x, y = self.center
        if item.rarity == 'SSR':
            self._create_particles(x, y, random.choice([GOLD, GOLD_LIGHT]), 40, (2.5, 7.0), (72, 144), (3, 6))
            for _ in range(12):
                self.effects.append(StarParticle(
                    x + random.randint(-150, 150),
                    y + random.randint(-150, 150)
                ))
            self.effects.append(RadialBurst(x, y, GOLD))
            self.effects.append(FloatingText("✨ SSR ✨", x, y - 120, GOLD, self.fonts["floating_large"]))
            self.screen_flash_alpha = 200
        elif item.rarity == 'SR':
            for i in range(20):
                angle = math.radians(i * 18)
                px = x + 120 * math.cos(angle)
                py = y + 120 * math.sin(angle)
                velocity = (math.cos(angle) * 2.5, math.sin(angle) * 2.5)
                self.effects.append(Particle(px, py, PURPLE_LIGHT, velocity, 72, 4))
            self.effects.append(FloatingText("⭐ SR ⭐", x, y - 120, PURPLE, self.fonts["floating_medium"]))
            self.screen_flash_alpha = 120
        else:
            self._create_particles(x, y, BLUE_LIGHT, 24, (1.5, 4.0), (36, 72), (4, 6))
            self.effects.append(FloatingText(f"• {item.name} •", x, y - 120, BLUE, self.fonts["floating_small"]))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.state == "idle":
                if self.button1_rect.collidepoint(mouse_pos):
                    if self.money_manager.spend_coins(GACHA_1_COST):
                        if self.sound_manager:
                            self.sound_manager.play_sfx('button')
                            self.sound_manager.play_sfx('gacha_start')
                        self.current_results = self._draw_items(1)
                        self.current_item_index = 0
                        self.state = "spinning"
                        self.animation_timer = 0
                        self.effects.clear()
                elif self.button10_rect.collidepoint(mouse_pos):
                    if self.money_manager.spend_coins(GACHA_10_COST):
                        if self.sound_manager:
                            self.sound_manager.play_sfx('button')
                            self.sound_manager.play_sfx('gacha_start')
                        self.current_results = self._draw_items(10)
                        self.current_item_index = 0
                        self.state = "spinning"
                        self.animation_timer = 0
                        self.effects.clear()
                elif self.close_rect.collidepoint(mouse_pos):
                    if not self.fading_out:
                        if self.sound_manager:
                            self.sound_manager.play_sfx('button')
                        self.fading_out = True
                        self.state = "fading_out"
            elif self.state == "showing_result":
                self.animation_timer = RESULT_SHOW_DURATION
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if not self.fading_out:
                if self.sound_manager:
                    self.sound_manager.play_sfx('button')
                self.fading_out = True
                self.state = "fading_out"

    def update(self, dt):
        prev_state = getattr(self, '_prev_state', None)
        if prev_state != self.state:
            if self.sound_manager and self.state == "revealing":
                self.sound_manager.play_sfx('gacha_result')
            self._prev_state = self.state
        self.animation_timer += 1
        # --- Fade-in/out animation ---
        if self.fading_out:
            if self.fade_alpha > 0:
                self.fade_alpha = max(0, self.fade_alpha - 24)
            if self.fade_alpha <= 0 and not self._fade_out_called:
                self._fade_out_called = True
                if self.on_close:
                    self.on_close()
            return  # skip other updates while fading out
        else:
            if self.fade_alpha < 255:
                self.fade_alpha = min(255, self.fade_alpha + 24)  # ปรับความเร็ว fade ได้
        # --- State machine ---
        if self.state == "spinning" and self.animation_timer >= SPIN_DURATION:
            self.state = "revealing"
            self.animation_timer = 0
            self.result_scale = 0.5
            self.target_result_scale = 1.0
        elif self.state == "revealing" and self.animation_timer >= REVEAL_DURATION:
            self.state = "showing_result"
            self.animation_timer = 0
            item = self.current_results[self.current_item_index]
            # บันทึกไอเทมที่ได้ลงใน collection
            rarity_enum = Rarity(item.rarity)
            self.data_manager.add_item_to_collection(item.name, rarity_enum)
            self._create_rarity_effects(item)
        elif self.state == "showing_result" and self.animation_timer >= RESULT_SHOW_DURATION:
            self.current_item_index += 1
            if self.current_item_index >= len(self.current_results):
                self.state = "idle"
            else:
                self.state = "revealing"
                self.animation_timer = 0
                self.result_scale = 0.5
                self.target_result_scale = 1.0
        # --- Effects ---
        for effect in self.effects:
            effect.update()
        self.effects = [effect for effect in self.effects if getattr(effect, 'life', 1) > 0]
        if self.screen_flash_alpha > 0:
            self.screen_flash_alpha = max(0, self.screen_flash_alpha - 3)
        self.result_scale += (self.target_result_scale - self.result_scale) * 0.15
        # --- Border animation ---
        speed_mult, scale = 1.0, 1.0
        if self.state == "spinning":
            progress = min(1.0, self.animation_timer / (SPIN_DURATION * 0.8))
            eased_progress = ease_in_out_cubic(progress)
            speed_mult = 1 + eased_progress * 3
            scale = 1 + eased_progress * 0.3
        elif self.state == "revealing":
            progress = self.animation_timer / REVEAL_DURATION
            eased_progress = ease_out_elastic(progress)
            speed_mult = max(0.1, 4 - eased_progress * 3.9)
            scale = max(1.0, 1.3 - eased_progress * 0.3)
        for border in self.borders:
            border.set_speed(speed_mult)
            border.set_scale(scale)
            border.update()

    def draw(self, surface):
        # --- พื้นหลัง: ใช้ bg เดียวกับเกมหลัก ---
        self.ui_manager.draw_background_image(surface)
        # --- Background ---
        # (Removed gradient background)
        # for y in range(self.height):
        #     color_ratio = y / self.height
        #     r = int(10 + color_ratio * 20)
        #     g = int(5 + color_ratio * 15)
        #     b = int(20 + color_ratio * 30)
        #     pygame.draw.line(surface, (r, g, b), (0, y), (self.width, y))
        # --- Borders ---
        for border in self.borders:
            border.draw(surface)
        # --- Effects ---
        for effect in self.effects:
            effect.draw(surface)
        if self.screen_flash_alpha > 0:
            flash_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, self.screen_flash_alpha))
            surface.blit(flash_surf, (0, 0))
        # --- Main ---
        if self.state == "spinning":
            if self.animation_timer % PREVIEW_CHANGE_RATE == 0 or not self.preview_item:
                self.preview_item = random.choice(self.all_items)
            center_x, center_y = self.center
            pulse = 1 + 0.2 * math.sin(self.animation_timer * 0.2)
            alpha = int(120 + 60 * math.sin(self.animation_timer * 0.15))
            item_size = int(120 * pulse)
            preview_surf = pygame.Surface((item_size, item_size), pygame.SRCALPHA)
            glow_rect = pygame.Rect(5, 5, item_size - 10, item_size - 10)
            pygame.draw.rect(preview_surf, (*self.preview_item.color, alpha // 2), glow_rect, border_radius=10)
            pygame.draw.rect(preview_surf, (*self.preview_item.color, alpha), glow_rect, 3, border_radius=10)
            surface.blit(preview_surf, (center_x - item_size // 2, center_y - item_size // 2))
            
            # Use image instead of text for icon
            icon_size = int(80 * pulse)
            icon_surface = self.preview_item.get_icon_surface(icon_size)
            icon_rect = icon_surface.get_rect(center=(center_x, center_y - 5))
            surface.blit(icon_surface, icon_rect)
        elif self.state in ("revealing", "showing_result"):
            if self.current_results:
                item = self.current_results[self.current_item_index]
                center_x, center_y = self.center
                if item.rarity == 'SSR':
                    center_y += math.sin(self.animation_timer * 0.08) * 8
                item_size = int(140 * self.result_scale)
                item_rect = pygame.Rect(center_x - item_size // 2, center_y - item_size // 2, item_size, item_size)
                glow_size = item_size + 20
                glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                glow_alpha = int(100 * self.result_scale)
                pygame.draw.rect(glow_surf, (*item.color, glow_alpha), glow_surf.get_rect(), border_radius=15)
                surface.blit(glow_surf, (center_x - glow_size // 2, center_y - glow_size // 2))
                pygame.draw.rect(surface, item.color, item_rect, border_radius=12)
                pygame.draw.rect(surface, WHITE, item_rect, int(4 * self.result_scale), border_radius=12)
                
                # Use image instead of text for icon
                icon_size = int(100 * self.result_scale)
                icon_surface = item.get_icon_surface(icon_size)
                icon_rect = icon_surface.get_rect(center=(center_x, center_y - 5))
                surface.blit(icon_surface, icon_rect)
                
                rarity_text = self.fonts["rarity"].render(item.rarity, True, item.color)
                name_text = self.fonts["small"].render(item.name, True, WHITE)
                rarity_rect = rarity_text.get_rect(center=(center_x, center_y + item_size // 2 + 20))
                name_rect = name_text.get_rect(center=(center_x, center_y + item_size // 2 + 50))
                surface.blit(rarity_text, rarity_rect)
                surface.blit(name_text, name_rect)
        # --- UI ---
        title_text = "TREE GACHA"
        title = self.fonts["large"].render(title_text, True, GOLD)
        title_rect = title.get_rect(center=(self.width // 2, 50))
        glow_title = self.fonts["large"].render(title_text, True, GOLD_LIGHT)
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            glow_title.set_alpha(100)
            surface.blit(glow_title, glow_rect)
        surface.blit(title, title_rect)
        
        # --- แสดง Coin (ตำแหน่งใหม่) ---
        self._draw_gacha_coin_box(surface)
        
        # --- ปุ่ม X (close) ---
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.close_rect.collidepoint(mouse_pos)
        pulse = 1.0 + (0.12 if is_hover else 0.06) * math.sin(self.animation_timer * 0.18)
        btn_size = int(self.close_btn_size * pulse)
        btn_rect = pygame.Rect(
            self.close_rect.centerx - btn_size//2,
            self.close_rect.centery - btn_size//2,
            btn_size, btn_size
        )
        color = (220, 60, 60) if is_hover else (200, 50, 50)
        shadow = pygame.Surface((btn_rect.width+6, btn_rect.height+6), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0,0,0,60), shadow.get_rect(), border_radius=12)
        surface.blit(shadow, (btn_rect.x-3, btn_rect.y-3))
        pygame.draw.rect(surface, color, btn_rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, btn_rect, 2, border_radius=12)
        x_font = self.fonts["medium"].render("X", True, WHITE)
        x_rect = x_font.get_rect(center=btn_rect.center)
        surface.blit(x_font, x_rect)
        
        if self.state == "idle":
            self.button1_rect = pygame.Rect(self.width // 2 - 200, self.height - 120, 180, 70)
            self.button10_rect = pygame.Rect(self.width // 2 + 20, self.height - 120, 180, 70)
            can_afford_1 = self.money_manager.coins >= GACHA_1_COST
            can_afford_10 = self.money_manager.coins >= GACHA_10_COST
            self._draw_button(surface, self.button1_rect, f"x1 ({GACHA_1_COST}¢)", GOLD if can_afford_1 else (100, 100, 100))
            self._draw_button(surface, self.button10_rect, f"x10 ({GACHA_10_COST}¢)", PURPLE if can_afford_10 else (100, 100, 100))

        # --- Fade-in overlay (drawn last to overlay everything) ---
        if self.fade_alpha < 255:
            fade_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, 255 - self.fade_alpha))
            surface.blit(fade_surf, (0, 0))

    def _draw_button(self, surface, rect, text, color):
        pulse = 0.8 + 0.2 * math.sin(self.animation_timer * 0.05)
        glow_alpha = int(60 * pulse)
        glow_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*color, glow_alpha), glow_surf.get_rect(), border_radius=15)
        surface.blit(glow_surf, (rect.x - 10, rect.y - 10))
        pygame.draw.rect(surface, color, rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, rect, 3, border_radius=12)
        
        # Calculate appropriate text scale to fit within button
        button_text = self.fonts["medium"].render(text, True, WHITE)
        text_width, text_height = button_text.get_size()
        
        # Calculate available space (with padding)
        available_width = rect.width - 20  # 10px padding on each side
        available_height = rect.height - 20  # 10px padding on each side
        
        # Calculate scale factors for width and height
        width_scale = available_width / text_width if text_width > 0 else 1.0
        height_scale = available_height / text_height if text_height > 0 else 1.0
        
        # Use the smaller scale to ensure text fits in both dimensions
        base_scale = min(width_scale, height_scale, 1.0)
        
        # Apply pulse effect with reduced range
        text_scale = base_scale * (0.9 + 0.05 * pulse)
        
        if text_scale != 1.0:
            new_size = (int(button_text.get_width() * text_scale),
                       int(button_text.get_height() * text_scale))
            if new_size[0] > 0 and new_size[1] > 0:
                button_text = pygame.transform.scale(button_text, new_size)
        
        text_rect = button_text.get_rect(center=rect.center)
        surface.blit(button_text, text_rect)

    def _show_insufficient_coins_effect(self):
        """แสดงเอฟเฟกต์เมื่อ coin ไม่พอ"""
        center_x, center_y = self.center
        self.effects.append(FloatingText("No Coin!", center_x, center_y - 120, (255, 100, 100), self.fonts["floating_medium"]))
        self.screen_flash_alpha = 100

    def _draw_gacha_coin_box(self, surface):
        """วาดกล่อง coin display ที่ตำแหน่งใหม่ (อิงขอบขวาหน้าจอ)"""
        money_text = self.money_manager.get_display_value()
        money_surf = self.fonts["medium"].render(money_text, True, (255, 223, 0))
        symbol_surf = self.fonts["small"].render("¢", True, (200, 150, 0))
        padding_x = 18
        padding_y = 10
        spacing = 20
        icon_diameter = 36
        box_rect = pygame.Rect(self.coin_box_x, self.coin_box_y, self.coin_box_w, self.coin_box_h)
        self.ui_manager.draw_modern_box(surface, box_rect, color=(50, 50, 30, 200))
        # วาดไอคอนเหรียญ (ชิดซ้าย)
        coin_center = (box_rect.left + padding_x + icon_diameter // 2, box_rect.centery)
        coin_bounce = math.sin(self.animation_timer * 6) * 2
        coin_y = coin_center[1] + coin_bounce
        pygame.draw.circle(surface, (255, 215, 0), (coin_center[0], int(coin_y)), 18)
        pygame.draw.circle(surface, (255, 165, 0), (coin_center[0], int(coin_y)), 18, 3)
        symbol_rect = symbol_surf.get_rect(center=(coin_center[0], int(coin_y)))
        surface.blit(symbol_surf, symbol_rect)
        # วาดจำนวนเงิน (ชิดขวา)
        money_rect = money_surf.get_rect()
        money_rect.centery = box_rect.centery
        money_rect.right = box_rect.right - padding_x
        surface.blit(money_surf, money_rect) 