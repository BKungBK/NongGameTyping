import pygame
import random
import math
import os
from typing import List, Dict, Optional, Callable
from .data_manager import DataManager, Rarity, Item
from dataclasses import dataclass

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

def get_rarity_color(rarity: Rarity) -> tuple:
    """Modern gaming theme colors"""
    colors = {
        Rarity.R: (100, 149, 237),      # Cornflower Blue
        Rarity.SR: (147, 112, 219),     # Medium Slate Blue
        Rarity.SSR: (255, 215, 0)       # Gold
    }
    return colors[rarity]

# --- Animation Classes ---
class AnimatedValue:
    def __init__(self, initial_value, target_value, duration, easing="ease_out"):
        self.initial = initial_value
        self.target = target_value
        self.current = initial_value
        self.duration = duration
        self.elapsed = 0
        self.easing = easing
        self.completed = False
    
    def update(self, dt):
        if self.completed:
            return self.current
        
        self.elapsed += dt
        progress = min(self.elapsed / self.duration, 1.0)
        
        if self.easing == "ease_out":
            progress = 1 - math.pow(1 - progress, 3)
        elif self.easing == "ease_in":
            progress = math.pow(progress, 3)
        elif self.easing == "ease_in_out":
            if progress < 0.5:
                progress = 2 * progress * progress
            else:
                progress = 1 - math.pow(-2 * progress + 2, 3) / 2
        
        self.current = self.initial + (self.target - self.initial) * progress
        
        if progress >= 1.0:
            self.completed = True
            self.current = self.target
        
        return self.current

class Particle:
    def __init__(self, x, y, color, velocity, life):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.life = life
        self.max_life = life
        self.size = random.uniform(1, 2)
    
    def update(self, dt):
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        self.life -= dt
        return self.life > 0
    
    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        size = max(1, int(self.size * (self.life / self.max_life)))
        if size > 0:
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (size, size), size)
            screen.blit(surf, (self.x - size, self.y - size))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.max_particles = 30
    
    def add_particle(self, x, y, color, velocity=None, life=1.0):
        if len(self.particles) >= self.max_particles:
            return
        if velocity is None:
            velocity = (random.uniform(-20, 20), random.uniform(-20, 20))
        self.particles.append(Particle(x, y, color, velocity, life))
    
    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)
    
    def add_magic_burst(self, x, y, color, count=5):
        for _ in range(min(count, self.max_particles - len(self.particles))):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(10, 40)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.add_particle(x, y, color, velocity, random.uniform(0.5, 1.5))

class ModernButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 bg_color: tuple = (40, 40, 40), text_color: tuple = (255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 24)
        self.hovered = False
        self.pressed = False
        self.scale = AnimatedValue(1.0, 1.0, 0.15)
        self.glow_intensity = AnimatedValue(0, 0, 0.3)
    
    def update(self, dt):
        self.scale.update(dt)
        self.glow_intensity.update(dt)
    
    def draw(self, screen):
        scale_factor = self.scale.current
        scaled_width = int(self.rect.width * scale_factor)
        scaled_height = int(self.rect.height * scale_factor)
        scaled_rect = pygame.Rect(
            self.rect.centerx - scaled_width // 2,
            self.rect.centery - scaled_height // 2,
            scaled_width, scaled_height
        )
        
        # Glow effect
        if self.glow_intensity.current > 0:
            glow_alpha = int(50 * self.glow_intensity.current)
            for i in range(3):
                glow_rect = scaled_rect.inflate(i * 4, i * 4)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*self.bg_color, glow_alpha), (0, 0, glow_rect.width, glow_rect.height), border_radius=12)
                screen.blit(glow_surf, glow_rect.topleft)
        
        # Main button
        intensity = int(30 * self.glow_intensity.current)
        color = tuple(min(255, c + intensity) for c in self.bg_color)
        pygame.draw.rect(screen, color, scaled_rect, border_radius=12)
        pygame.draw.rect(screen, (80, 80, 80), scaled_rect, 2, border_radius=12)
        
        # Text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            was_hovered = self.hovered
            self.hovered = self.rect.collidepoint(event.pos)
            if self.hovered and not was_hovered:
                self.scale = AnimatedValue(1.0, 1.05, 0.15, "ease_out")
                self.glow_intensity = AnimatedValue(0, 1, 0.3, "ease_out")
            elif not self.hovered and was_hovered:
                self.scale = AnimatedValue(1.05, 1.0, 0.15, "ease_out")
                self.glow_intensity = AnimatedValue(1, 0, 0.3, "ease_out")
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                self.scale = AnimatedValue(1.05, 0.95, 0.1, "ease_in")
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed:
                self.pressed = False
                self.scale = AnimatedValue(0.95, 1.05, 0.1, "ease_out")
        
        return False

class FilterTab:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: tuple):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.active = False
        self.font = pygame.font.Font(None, 20)
        self.hover_scale = AnimatedValue(1.0, 1.0, 0.2)
        self.glow_intensity = AnimatedValue(0, 0, 0.3)
    
    def update(self, dt):
        self.hover_scale.update(dt)
        self.glow_intensity.update(dt)
    
    def draw(self, screen):
        scale = self.hover_scale.current
        scaled_width = int(self.rect.width * scale)
        scaled_height = int(self.rect.height * scale)
        draw_rect = pygame.Rect(
            self.rect.centerx - scaled_width // 2,
            self.rect.centery - scaled_height // 2,
            scaled_width, scaled_height
        )
        
        # Glow effect for active tab
        if self.active or self.glow_intensity.current > 0:
            glow_alpha = int(80 * (1.0 if self.active else self.glow_intensity.current))
            for i in range(2):
                glow_rect = draw_rect.inflate(i * 3, i * 3)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*self.color, glow_alpha), (0, 0, glow_rect.width, glow_rect.height), border_radius=8)
                screen.blit(glow_surf, glow_rect.topleft)
        
        # Tab background
        if self.active:
            bg_color = tuple(min(255, c + 40) for c in self.color)
            border_color = (255, 255, 255)
        else:
            bg_color = (30, 30, 30)
            border_color = (60, 60, 60)
        
        pygame.draw.rect(screen, bg_color, draw_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, draw_rect, 2, border_radius=8)
        
        # Text
        text_color = (255, 255, 255) if self.active else (160, 160, 160)
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=draw_rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if not self.active:
                    self.hover_scale = AnimatedValue(1.0, 1.1, 0.2, "ease_out")
                    self.glow_intensity = AnimatedValue(0, 1, 0.3, "ease_out")
            else:
                self.hover_scale = AnimatedValue(self.hover_scale.current, 1.0, 0.2, "ease_out")
                self.glow_intensity = AnimatedValue(self.glow_intensity.current, 0, 0.3, "ease_out")
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class ItemCard:
    def __init__(self, item: Item, x: int, y: int, width: int = 300, height: int = 400):
        self.item = item
        self.rect = pygame.Rect(x, y, width, height)
        self.original_x = x
        self.original_y = y
        self.scale = AnimatedValue(0.8, 0.8, 0.3)
        self.alpha = AnimatedValue(0, 255, 0.5)
        self.glow_intensity = AnimatedValue(0, 0, 0.3)
        self.font_title = pygame.font.Font(None, 28)
        self.font_icon = pygame.font.Font(None, 80)
        self.font_rarity = pygame.font.Font(None, 22)
        self.font_rate = pygame.font.Font(None, 18)
        self.is_center = False
        self.hovered = False
        self.item_image = None
        self.is_emoji = self._is_emoji(self.item.icon)
        if not self.is_emoji:
            self._load_item_image()
    
    def _is_emoji(self, text):
        """Check if the icon is an emoji (not a filename ending with .png)"""
        return not text.lower().endswith('.png')
    
    def _load_item_image(self):
        """Load the item image from assets"""
        try:
            # Get the image path using DataManager
            data_manager = DataManager()
            image_path = data_manager.get_assets_path("images", f"Item/{self.item.icon}")
            
            if os.path.exists(image_path):
                self.item_image = pygame.image.load(image_path).convert_alpha()
            else:
                print(f"Warning: Image not found for {self.item.name}: {image_path}")
                self.item_image = None
        except Exception as e:
            print(f"Error loading image for {self.item.name}: {e}")
            self.item_image = None
    
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
            return font.render(self.item.icon, True, (255, 255, 255))
        if self.item_image is None:
            font = pygame.font.Font(None, size or 60)
            return font.render(self.item.icon, True, (255, 255, 255))
        if size:
            return self._scale_image_to_fit(self.item_image, size)
        return self.item_image
    
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
    
    def set_center(self, is_center: bool):
        if is_center != self.is_center:
            self.is_center = is_center
            target_scale = 1.0 if is_center else 0.8
            self.scale = AnimatedValue(self.scale.current, target_scale, 0.4, "ease_out")
            self.alpha = AnimatedValue(self.alpha.current, 255 if is_center else 180, 0.4, "ease_out")
    
    def update(self, dt):
        self.scale.update(dt)
        self.alpha.update(dt)
        self.glow_intensity.update(dt)
    
    def draw(self, screen, particle_system):
        if self.alpha.current < 10:
            return
        
        # Calculate scaled dimensions
        scale = self.scale.current
        width = int(self.rect.width * scale)
        height = int(self.rect.height * scale)
        x = self.rect.centerx - width // 2
        y = self.rect.centery - height // 2
        card_rect = pygame.Rect(x, y, width, height)
        
        # Create card surface
        card_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        alpha = int(self.alpha.current)
        
        # Glow effect for center card or collected items
        if self.is_center or (self.item.is_owned and self.glow_intensity.current > 0):
            glow_color = self.item.get_rarity_color()
            glow_alpha = int(60 * (1.0 if self.is_center else self.glow_intensity.current))
            for i in range(4):
                glow_rect = card_rect.inflate(i * 6, i * 6)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*glow_color, glow_alpha // (i + 1)), 
                               (0, 0, glow_rect.width, glow_rect.height), border_radius=15)
                screen.blit(glow_surf, glow_rect.topleft)
        
        # Card background
        bg_color = (20, 20, 20) if not self.item.is_owned else (30, 30, 30)
        pygame.draw.rect(card_surface, (*bg_color, alpha), (0, 0, width, height), border_radius=15)
        
        # Rarity border
        rarity_color = self.item.get_rarity_color()
        border_width = 3 if self.is_center else 2
        pygame.draw.rect(card_surface, (*rarity_color, alpha), (0, 0, width, height), border_width, border_radius=15)
        
        # Item icon area
        icon_size = int(120 * scale)
        icon_x = (width - icon_size) // 2
        icon_y = 60
        icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
        
        # Icon background
        pygame.draw.rect(card_surface, (40, 40, 40, alpha), icon_rect, border_radius=12)
        pygame.draw.rect(card_surface, (*rarity_color, alpha), icon_rect, 2, border_radius=12)
        
        # Item icon
        icon_surface = self.get_icon_surface(icon_size)
        icon_text_rect = icon_surface.get_rect(center=icon_rect.center)
        card_surface.blit(icon_surface, icon_text_rect)
        
        # Item name
        name_surface = self.font_title.render(self.item.name, True, (255, 255, 255, alpha))
        name_rect = name_surface.get_rect(centerx=width//2, y=icon_y + icon_size + 20)
        card_surface.blit(name_surface, name_rect)
        
        # Rarity badge
        rarity_surface = self.font_rarity.render(self.item.rarity.value, True, (*rarity_color, alpha))
        rarity_rect = rarity_surface.get_rect(centerx=width//2, y=name_rect.bottom + 15)
        card_surface.blit(rarity_surface, rarity_rect)
        
        # Rate info
        rate_surface = self.font_rate.render(f"Rate: {self.item.rate}%", True, (180, 180, 180, alpha))
        rate_rect = rate_surface.get_rect(centerx=width//2, y=rarity_rect.bottom + 10)
        card_surface.blit(rate_surface, rate_rect)
        
        # Collection status
        if self.item.is_owned:
            # Render star with emoji font
            star_font = None
            star_font_size = int(self.font_rarity.get_height() * 1.5)  # ให้ดาวใหญ่ขึ้น 1.5 เท่า
            try:
                star_font = pygame.font.SysFont("Segoe UI Symbol", star_font_size)
            except Exception:
                star_font = None
            if star_font is None or star_font.get_height() == 0:
                try:
                    star_font = pygame.font.Font("assets/fonts/NotoColorEmoji-Regular.ttf", star_font_size)
                except Exception:
                    star_font = pygame.font.Font(None, star_font_size)
            star_surface = star_font.render("★", True, (0, 255, 100, alpha))
            owned_surface = self.font_rarity.render(" OWNED", True, (0, 255, 100, alpha))
            # ต่อภาพดาวกับ OWNED
            total_width = star_surface.get_width() + owned_surface.get_width()
            total_height = max(star_surface.get_height(), owned_surface.get_height())
            status_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
            # วางดาวให้ฐานเท่ากันกับ OWNED
            star_y = total_height - star_surface.get_height()
            owned_y = total_height - owned_surface.get_height()
            status_surface.blit(star_surface, (0, star_y))
            status_surface.blit(owned_surface, (star_surface.get_width(), owned_y))
            status_rect = status_surface.get_rect(centerx=width//2, y=rate_rect.bottom + 10)
            card_surface.blit(status_surface, status_rect)
        else:
            status_surface = self.font_rarity.render("NOT OWNED", True, (150, 150, 150, alpha))
            status_rect = status_surface.get_rect(centerx=width//2, y=rate_rect.bottom + 10)
            card_surface.blit(status_surface, status_rect)
        
        # Blit to screen
        screen.blit(card_surface, card_rect.topleft)
    
    def handle_event(self, event, particle_system):
        if event.type == pygame.MOUSEMOTION:
            was_hovered = self.hovered
            self.hovered = self.rect.collidepoint(event.pos)
            
            if self.hovered and not was_hovered and self.item.is_owned:
                self.glow_intensity = AnimatedValue(0, 1, 0.3, "ease_out")
                if len(particle_system.particles) < 15:
                    particle_system.add_magic_burst(self.rect.centerx, self.rect.centery, 
                                                  self.item.get_rarity_color(), 3)
            elif not self.hovered and was_hovered:
                self.glow_intensity = AnimatedValue(1, 0, 0.3, "ease_out")

class CarouselSystem:
    def __init__(self, screen_width: int):
        self.screen_width = screen_width
        self.center_x = screen_width // 2
        self.current_index = 0
        self.cards = []
        self.card_spacing = 350
        self.scroll_offset = AnimatedValue(0, 0, 0.5, "ease_out")
        
    def set_items(self, items: List[Item]):
        self.cards = []
        self.current_index = 0
        
        for i, item in enumerate(items):
            x = self.center_x - 150  # Center the first card
            y = 160
            card = ItemCard(item, x, y)
            self.cards.append(card)
        
        self.update_positions()
    
    def update_positions(self):
        if not self.cards:
            return
            
        # Calculate target positions
        for i, card in enumerate(self.cards):
            offset_from_center = i - self.current_index
            target_x = self.center_x + (offset_from_center * self.card_spacing) + self.scroll_offset.current - 150
            card.rect.x = int(target_x)
            
            # Set center card
            card.set_center(i == self.current_index)
    
    def navigate_to(self, index: int):
        if 0 <= index < len(self.cards):
            self.current_index = index
            self.scroll_offset = AnimatedValue(0, 0, 0.5, "ease_out")
            self.update_positions()
    
    def navigate_left(self):
        if self.current_index > 0:
            self.navigate_to(self.current_index - 1)
    
    def navigate_right(self):
        if self.current_index < len(self.cards) - 1:
            self.navigate_to(self.current_index + 1)
    
    def update(self, dt):
        self.scroll_offset.update(dt)
        self.update_positions()
        
        for card in self.cards:
            card.update(dt)
    
    def draw(self, screen, particle_system):
        # Draw cards from back to front (center card last)
        draw_order = []
        for i, card in enumerate(self.cards):
            distance = abs(i - self.current_index)
            draw_order.append((distance, i, card))
        
        draw_order.sort(key=lambda x: -x[0])  # Far to near
        
        for _, _, card in draw_order:
            card.draw(screen, particle_system)
    
    def handle_event(self, event, particle_system):
        for card in self.cards:
            card.handle_event(event, particle_system)

class CollectionOverlaySystem:
    def __init__(self, screen_size, font_dict, ui_manager, on_close: Optional[Callable]=None):
        self.width, self.height = screen_size
        self.fonts = font_dict
        self.ui_manager = ui_manager
        self.on_close = on_close
        self.state = "idle"
        
        # Initialize systems
        self.data_manager = DataManager()
        self.particle_system = ParticleSystem()
        self.carousel = CarouselSystem(self.width)
        
        # Setup UI
        self.setup_ui()
        self.current_filter = "ALL"
        self.background_particles_timer = 0
        
        # Fade animation
        self.fade_alpha = 0
        self.fading_out = False
        self._fade_out_called = False
        
        # Close button
        self.close_btn_size = 40
        margin = 32
        self.close_rect = pygame.Rect(self.width - margin - self.close_btn_size, margin, self.close_btn_size, self.close_btn_size)
        
        self._update_collection()
    
    def setup_ui(self):
        # Filter tabs
        self.filter_tabs = {
            "ALL": FilterTab(0, 85, 100, 35, "ALL", (60, 60, 60)),
            "R": FilterTab(0, 85, 100, 35, "COMMON", (100, 149, 237)),
            "SR": FilterTab(0, 85, 100, 35, "RARE", (147, 112, 219)),
            "SSR": FilterTab(0, 85, 100, 35, "LEGEND", (255, 215, 0)),
            "COLLECTED": FilterTab(0, 85, 100, 35, "OWNED", (0, 200, 100))
        }
        self.filter_tabs["ALL"].active = True
        
        # Center tabs
        self._center_tabs()
    
    def _center_tabs(self):
        tab_width = 110
        tab_spacing = 15
        total_width = len(self.filter_tabs) * tab_width + (len(self.filter_tabs) - 1) * tab_spacing
        start_x = (self.width - total_width) // 2
        
        for i, tab in enumerate(self.filter_tabs.values()):
            tab.rect.x = start_x + i * (tab_width + tab_spacing)
            tab.rect.width = tab_width
    
    def _update_collection(self):
        items = self._get_filtered_items()
        self.carousel.set_items(items)
    
    def _get_filtered_items(self) -> List[Item]:
        if self.current_filter == "ALL":
            return self.data_manager.get_all_items()
        elif self.current_filter == "COLLECTED":
            return self.data_manager.get_collected_items()
        else:
            try:
                rarity = Rarity(self.current_filter)
                return self.data_manager.get_items_by_rarity(rarity)
            except ValueError:
                return self.data_manager.get_all_items()
    
    def _draw_collection_stats(self, screen):
        """Draw collection statistics"""
        stats = self.data_manager.get_player_stats()
        font_stats = pygame.font.Font(None, 20)
        
        # Total collection progress
        total_progress = f"Collection: {stats['owned_items']}/{stats['total_items']} ({stats['completion_rate']}%)"
        progress_surface = font_stats.render(total_progress, True, (200, 200, 200))
        progress_rect = progress_surface.get_rect(x=20, y=20)
        screen.blit(progress_surface, progress_rect)
        
        # Rarity breakdown
        y_offset = 50
        for rarity in ["R", "SR", "SSR"]:
            if rarity in stats['owned_rarity_counts']:
                owned = stats['owned_rarity_counts'][rarity]
                total = stats['rarity_counts'][rarity]
                rarity_text = f"{rarity}: {owned}/{total}"
                color = get_rarity_color(Rarity(rarity))
                rarity_surface = font_stats.render(rarity_text, True, color)
                rarity_rect = rarity_surface.get_rect(x=20, y=y_offset)
                screen.blit(rarity_surface, rarity_rect)
                y_offset += 25
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.close_rect.collidepoint(mouse_pos):
                if not self.fading_out:
                    self.fading_out = True
                    self.state = "fading_out"
                    return
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if not self.fading_out:
                    self.fading_out = True
                    self.state = "fading_out"
                    return
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.carousel.navigate_left()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.carousel.navigate_right()
            elif event.key == pygame.K_HOME:
                self.carousel.navigate_to(0)
            elif event.key == pygame.K_END:
                self.carousel.navigate_to(len(self.carousel.cards) - 1)
            # Test ownership toggle with 'T' key
            elif event.key == pygame.K_t and self.carousel.cards:
                current_item = self.carousel.cards[self.carousel.current_index].item
                new_status = not current_item.is_owned
                self.data_manager.set_item_ownership(current_item.name, current_item.rarity, new_status)
                self._update_collection()
        
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.carousel.navigate_left()
            else:
                self.carousel.navigate_right()
        
        # Handle filter tabs
        for filter_name, tab in self.filter_tabs.items():
            if tab.handle_event(event):
                # Deactivate old tab
                if self.current_filter in self.filter_tabs:
                    self.filter_tabs[self.current_filter].active = False
                
                # Activate new tab
                self.current_filter = filter_name
                tab.active = True
                self._update_collection()
                
                # Add filter change particles
                self.particle_system.add_magic_burst(tab.rect.centerx, tab.rect.centery, 
                                                   tab.color, 6)
        
        # Handle carousel events
        self.carousel.handle_event(event, self.particle_system)
    
    def update(self, dt):
        # Fade animation
        if self.fading_out:
            if self.fade_alpha > 0:
                self.fade_alpha = max(0, self.fade_alpha - 24)
            if self.fade_alpha <= 0 and not self._fade_out_called:
                self._fade_out_called = True
                if self.on_close:
                    self.on_close()
            return
        else:
            if self.fade_alpha < 255:
                self.fade_alpha = min(255, self.fade_alpha + 24)
        
        # Update UI elements
        for tab in self.filter_tabs.values():
            tab.update(dt)
        
        # Update carousel
        self.carousel.update(dt)
        
        # Update particle system
        self.particle_system.update(dt)
        
        # Spawn background particles occasionally
        self.background_particles_timer += dt
        if self.background_particles_timer > 0.5:
            self.background_particles_timer = 0
            if len(self.particle_system.particles) < 15:
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                color = random.choice([(80, 80, 120), (120, 80, 80), (80, 120, 80), (120, 120, 80)])
                self.particle_system.add_particle(x, y, color, life=2.0)
    
    def draw(self, surface):
        # Background
        self.ui_manager.draw_background_image(surface)
        
        # Draw background particles
        self.particle_system.draw(surface)
        
        # Draw title
        title_surface = self.fonts["large"].render("NEXUS COLLECTION", True, (255, 255, 255))
        title_rect = title_surface.get_rect(centerx=self.width//2, y=20)
        surface.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle_surface = self.fonts["small"].render("Gaming Archive", True, (150, 150, 150))
        subtitle_rect = subtitle_surface.get_rect(centerx=self.width//2, y=title_rect.bottom + 5)
        surface.blit(subtitle_surface, subtitle_rect)
        
        # Draw collection statistics
        self._draw_collection_stats(surface)
        
        # Draw filter tabs
        for tab in self.filter_tabs.values():
            tab.draw(surface)
        
        # Draw carousel
        self.carousel.draw(surface, self.particle_system)
        
        # Draw navigation hints
        font_hint = pygame.font.Font(None, 18)
        hints = [
            "Use ← → or A/D to navigate",
            "Mouse wheel to scroll",
            "T to toggle ownership (test)",
            "ESC to exit"
        ]
        
        for i, hint in enumerate(hints):
            hint_surface = font_hint.render(hint, True, (100, 100, 100))
            hint_rect = hint_surface.get_rect(centerx=self.width//2, y=self.height - 80 + i * 20)
            surface.blit(hint_surface, hint_rect)
        
        # Draw close button
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.close_rect.collidepoint(mouse_pos)
        pulse = 1.0 + (0.12 if is_hover else 0.06) * math.sin(pygame.time.get_ticks() * 0.001 * 18)
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
        
        # Fade overlay
        if self.fade_alpha < 255:
            fade_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, 255 - self.fade_alpha))
            surface.blit(fade_surf, (0, 0)) 